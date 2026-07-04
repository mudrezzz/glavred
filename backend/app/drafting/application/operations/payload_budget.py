"""Owner: drafting.application.operations

Used by: DraftRun provider-heavy services before building LLM provider messages.
Does not own: prompt wording, provider adapters, artifact storage, model selection.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Any, Mapping

from backend.app.shared.llm_operations import LlmOperationIncident, LlmOperationIncidentSeverity, LlmOperationIncidentType


EXECUTION_MODES = ("smoke", "standard", "full")
HARD_PAYLOAD_CHAR_CAP_MULTIPLIER = 1.25
CONTEXT_OVER_BUDGET_INCIDENT = "contextOverBudget"
PAYLOAD_TOO_LARGE_INCIDENT = "payloadTooLarge"


@dataclass(frozen=True)
class PayloadBudgetProfile:
    operation_id: str
    operation_kind: str
    execution_mode: str
    max_prompt_chars: int
    approx_token_budget: int
    max_rules: int
    max_claims: int
    max_evidence_items: int
    max_candidates: int
    max_source_snippets: int
    max_prior_drafts: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "operationId": self.operation_id,
            "operationKind": self.operation_kind,
            "executionMode": self.execution_mode,
            "maxPromptChars": self.max_prompt_chars,
            "approxTokenBudget": self.approx_token_budget,
            "maxRules": self.max_rules,
            "maxClaims": self.max_claims,
            "maxEvidenceItems": self.max_evidence_items,
            "maxCandidates": self.max_candidates,
            "maxSourceSnippets": self.max_source_snippets,
            "maxPriorDrafts": self.max_prior_drafts,
        }


@dataclass(frozen=True)
class SemanticInputContract:
    must_have: tuple[str, ...] = ()
    should_have: tuple[str, ...] = ()
    diagnostic_only: tuple[str, ...] = ()
    never_send_to_provider: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, list[str]]:
        return {
            "mustHave": list(self.must_have),
            "shouldHave": list(self.should_have),
            "diagnosticOnly": list(self.diagnostic_only),
            "neverSendToProvider": list(self.never_send_to_provider),
        }


@dataclass(frozen=True)
class PayloadBudgetResult:
    compact_payload: dict[str, Any]
    input_stats: dict[str, Any]
    payload_stats: dict[str, Any]
    trimmed_counts: dict[str, int] = field(default_factory=dict)
    suppressed_fields: tuple[str, ...] = ()
    quality_risk: str = "none"
    incident: LlmOperationIncident | None = None

    @property
    def payload_budget(self) -> dict[str, Any]:
        return dict(self.payload_stats.get("payloadBudget") or {})


class DraftRunPayloadBudgetPolicy:
    def __init__(self, profiles: Mapping[tuple[str, str], PayloadBudgetProfile] | None = None) -> None:
        self._profiles = dict(profiles or DEFAULT_PROFILES)

    def profile_for(self, operation_id: str, execution_mode: str | None = None) -> PayloadBudgetProfile:
        mode = _execution_mode(execution_mode)
        return self._profiles[(operation_id, mode)]

    def compact(
        self,
        operation_id: str,
        payload: Mapping[str, Any],
        *,
        execution_mode: str | None = None,
        model: str | None = None,
        model_role: str | None = None,
        generation_params: Mapping[str, Any] | None = None,
    ) -> PayloadBudgetResult:
        profile = self.profile_for(operation_id, execution_mode)
        contract = SEMANTIC_CONTRACTS[operation_id]
        compact_payload, trimmed_counts, suppressed_fields = _compact_by_operation(profile, dict(payload), contract)
        prompt_char_estimate = len(json.dumps(compact_payload, ensure_ascii=False, sort_keys=True))
        approx_tokens = math.ceil(prompt_char_estimate / 4)
        sent_counts = _sent_counts(compact_payload)
        quality_risk = _quality_risk(contract, compact_payload, trimmed_counts, prompt_char_estimate, profile.max_prompt_chars)
        payload_budget = {
            "profileId": profile.operation_id,
            "operationKind": profile.operation_kind,
            "executionMode": profile.execution_mode,
            "limits": profile.to_payload(),
            "sentCounts": sent_counts,
            "trimmedCounts": trimmed_counts,
            "suppressedFields": list(suppressed_fields),
            "semanticInputs": contract.to_payload(),
            "qualityRisk": quality_risk,
            "promptCharEstimate": prompt_char_estimate,
            "approxTokenEstimate": approx_tokens,
        }
        input_stats = {
            "promptCharEstimate": prompt_char_estimate,
            "approxTokenEstimate": approx_tokens,
            "ruleCount": sent_counts["rules"],
            "evidenceCount": sent_counts["evidenceItems"],
            "claimCount": sent_counts["claims"],
            "sourceCount": sent_counts["sourceSnippets"],
            "candidateCount": sent_counts["candidates"],
            "model": model,
            "modelRole": model_role,
            "generationParams": dict(generation_params or {}),
        }
        payload_stats = {"payloadBudget": payload_budget}
        incident = _budget_incident(profile, prompt_char_estimate, payload_stats)
        return PayloadBudgetResult(
            compact_payload=compact_payload,
            input_stats=input_stats,
            payload_stats=payload_stats,
            trimmed_counts=trimmed_counts,
            suppressed_fields=tuple(suppressed_fields),
            quality_risk=quality_risk,
            incident=incident,
        )


def _compact_by_operation(
    profile: PayloadBudgetProfile,
    payload: dict[str, Any],
    contract: SemanticInputContract,
) -> tuple[dict[str, Any], dict[str, int], list[str]]:
    suppressed_fields = [field_name for field_name in contract.never_send_to_provider if field_name in payload]
    trimmed: dict[str, int] = {}
    compact: dict[str, Any] = {
        key: value
        for key, value in payload.items()
        if key not in set(contract.never_send_to_provider).union(contract.diagnostic_only)
    }
    suppressed_fields.extend([field_name for field_name in contract.diagnostic_only if field_name in payload])

    if "context_artifact" in compact:
        compact["context_artifact"], counts = _compact_context_artifact(_record(compact["context_artifact"]), profile)
        _merge_counts(trimmed, counts)
    if "contextArtifact" in compact:
        compact["contextArtifact"], counts = _compact_context_artifact(_record(compact["contextArtifact"]), profile)
        _merge_counts(trimmed, counts)
    if "rule_pack" in compact:
        compact["rule_pack"], counts = _compact_rule_pack(_record(compact["rule_pack"]), profile)
        _merge_counts(trimmed, counts)
    if "rulePack" in compact:
        compact["rulePack"], counts = _compact_rule_pack(_record(compact["rulePack"]), profile)
        _merge_counts(trimmed, counts)
    if "material_plan" in compact:
        compact["material_plan"], counts = _compact_material_plan(_record(compact["material_plan"]), profile)
        _merge_counts(trimmed, counts)
    if "materialPlan" in compact:
        compact["materialPlan"], counts = _compact_material_plan(_record(compact["materialPlan"]), profile)
        _merge_counts(trimmed, counts)
    if "candidate" in compact:
        compact["candidate"] = _compact_candidate(_record(compact["candidate"]))
    if "candidates" in compact:
        candidates = _records(compact["candidates"])
        compact["candidates"] = [_compact_candidate(candidate) for candidate in candidates[: profile.max_candidates]]
        _trimmed(trimmed, "candidates", len(candidates), len(compact["candidates"]))
    if "draft_artifact" in compact:
        compact["draft_artifact"], counts = _compact_draft_artifact(_record(compact["draft_artifact"]), profile)
        _merge_counts(trimmed, counts)
    if "trace_context" in compact:
        compact["trace_context"], counts = _compact_trace_context(_record(compact["trace_context"]), profile)
        _merge_counts(trimmed, counts)
    if "traceContext" in compact:
        compact["traceContext"], counts = _compact_trace_context(_record(compact["traceContext"]), profile)
        _merge_counts(trimmed, counts)
    if "deterministic_report" in compact:
        compact["deterministic_report"], counts = _compact_validation_report(_record(compact["deterministic_report"]), profile)
        _merge_counts(trimmed, counts)
    if "llm_validation_report" in compact:
        compact["llm_validation_report"], counts = _compact_validation_report(_record(compact["llm_validation_report"]), profile)
        _merge_counts(trimmed, counts)
    if "validation_report" in compact:
        compact["validation_report"], counts = _compact_validation_report(_record(compact["validation_report"]), profile)
        _merge_counts(trimmed, counts)
    return compact, trimmed, sorted(set(suppressed_fields))


def _compact_context_artifact(context_artifact: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
    counts: dict[str, int] = {}
    source_ledger, ledger_counts = _compact_source_ledger(_record(context_artifact.get("sourceLedger")), profile)
    _merge_counts(counts, ledger_counts)
    public_evidence, evidence_counts = _compact_public_evidence(_record(context_artifact.get("publicEvidence")), profile)
    _merge_counts(counts, evidence_counts)
    synthesis, synthesis_counts = _compact_evidence_synthesis(_record(context_artifact.get("evidenceSynthesis")), profile)
    _merge_counts(counts, synthesis_counts)
    compact = {
        "contextSummary": _compact_context_summary(_record(context_artifact.get("contextSummary"))),
        "postContract": context_artifact.get("postContract"),
        "sourceLedger": source_ledger,
        "publicEvidence": public_evidence,
        "evidenceSynthesis": synthesis,
        "draftRunBudget": context_artifact.get("draftRunBudget"),
    }
    return _drop_empty(compact), counts


def _compact_rule_pack(rule_pack: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
    snapshot = _record(rule_pack.get("ruleRegistrySnapshot"))
    rules = _records(snapshot.get("rules"))
    selected = [_compact_rule(rule) for rule in _select_rules(rules, profile.max_rules)]
    compact_snapshot = {
        **{key: value for key, value in snapshot.items() if key not in {"rules", "sourceLedger", "fullRuleRegistry"}},
        "rules": selected,
        "metadata": {
            **_record(snapshot.get("metadata")),
            "payloadBudgeted": True,
            "originalRuleCount": len(rules),
            "sentRuleCount": len(selected),
        },
    }
    compact = {
        **{key: value for key, value in rule_pack.items() if key not in {"ruleRegistrySnapshot", "sourceLedger"}},
        "ruleRegistrySnapshot": compact_snapshot,
    }
    trimmed: dict[str, int] = {}
    _trimmed(trimmed, "rules", len(rules), len(selected))
    return compact, trimmed


def _compact_material_plan(material_plan: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
    counts: dict[str, int] = {}
    compact = _pick(
        material_plan,
        (
            "status",
            "thesis",
            "angle",
            "readerValue",
            "structure",
            "sections",
            "outline",
            "warnings",
            "rejectionReasons",
            "evidenceInterpretationSummary",
        ),
    )
    for key in ("usableEvidence", "usableEvidenceCandidates", "evidenceCandidates"):
        if key in material_plan:
            values = _records(material_plan.get(key))
            compact[key] = values[: profile.max_evidence_items]
            _trimmed(counts, key, len(values), len(compact[key]))
    return _drop_empty(compact), counts


def _compact_draft_artifact(draft_artifact: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
    candidates = _records(draft_artifact.get("candidates"))
    compact = {
        **_pick(draft_artifact, ("status", "scorecard", "selectedCandidateId", "fallbackUsed")),
        "candidates": [_compact_candidate(candidate) for candidate in candidates[: profile.max_candidates]],
    }
    counts: dict[str, int] = {}
    _trimmed(counts, "candidates", len(candidates), len(compact["candidates"]))
    return _drop_empty(compact), counts


def _compact_trace_context(trace_context: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
    compact = _pick(trace_context, ("draftRunId", "traceStatus", "validationSummary", "unresolvedRisks"))
    compact["finalQualityGate"] = _summary_record(_record(trace_context.get("finalQualityGate")))
    compact["alternativeAngleTournament"] = _summary_record(_record(trace_context.get("alternativeAngleTournament")))
    revision_loop = _record(trace_context.get("revisionLoop"))
    prior_drafts = _records(revision_loop.get("cycles"))[: profile.max_prior_drafts]
    compact["revisionLoop"] = _drop_empty(
        {
            "status": revision_loop.get("status"),
            "cycleCount": len(_records(revision_loop.get("cycles"))),
            "cycles": [_summary_record(cycle) for cycle in prior_drafts],
        }
    )
    counts: dict[str, int] = {}
    _trimmed(counts, "priorDrafts", len(_records(revision_loop.get("cycles"))), len(prior_drafts))
    return _drop_empty(compact), counts


def _compact_validation_report(report: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
    candidate_reports = _records(report.get("candidateReports"))
    compact = _pick(report, ("status", "summary", "overallStatus", "reason"))
    compact["candidateReports"] = [_summary_record(item) for item in candidate_reports[: profile.max_candidates]]
    counts: dict[str, int] = {}
    _trimmed(counts, "candidateReports", len(candidate_reports), len(compact["candidateReports"]))
    return _drop_empty(compact), counts


def _compact_source_ledger(source_ledger: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
    claims = _records(source_ledger.get("claims"))
    selected = [_compact_claim(claim) for claim in claims[: profile.max_claims]]
    compact = {
        "claims": selected,
        "warnings": _records(source_ledger.get("warnings"))[: min(8, profile.max_claims)],
        "metadata": {
            **_record(source_ledger.get("metadata")),
            "payloadBudgeted": True,
            "originalClaimCount": len(claims),
            "sentClaimCount": len(selected),
        },
    }
    counts: dict[str, int] = {}
    _trimmed(counts, "claims", len(claims), len(selected))
    return compact, counts


def _compact_public_evidence(public_evidence: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
    items = _records(public_evidence.get("items"))
    selected = [_compact_evidence_item(item) for item in items[: profile.max_evidence_items]]
    counts: dict[str, int] = {}
    _trimmed(counts, "evidenceItems", len(items), len(selected))
    return _drop_empty({"items": selected, "budget": public_evidence.get("budget") or public_evidence.get("budgetTrace")}), counts


def _compact_evidence_synthesis(evidence_synthesis: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
    claims = _records(evidence_synthesis.get("externalClaims"))
    selected = [_compact_claim(claim) for claim in claims[: profile.max_claims]]
    counts: dict[str, int] = {}
    _trimmed(counts, "synthesisClaims", len(claims), len(selected))
    return _drop_empty(
        {
            "externalClaims": selected,
            "decisions": _records(evidence_synthesis.get("decisions"))[: profile.max_claims],
            "warnings": _records(evidence_synthesis.get("warnings"))[: min(8, profile.max_claims)],
            "fallbackUsed": evidence_synthesis.get("fallbackUsed"),
        }
    ), counts


def _select_rules(rules: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    relevant = [rule for rule in rules if _is_relevant_rule(rule)]
    selected = relevant[:limit] if relevant else rules[:limit]
    return selected


def _is_relevant_rule(rule: dict[str, Any]) -> bool:
    severity = str(rule.get("severity") or rule.get("priority") or "").lower()
    searchable = " ".join(str(rule.get(key) or "") for key in ("id", "title", "scope", "category", "group", "validatorType", "source")).lower()
    return severity in {"hard", "critical"} or any(marker in searchable for marker in ("evidence", "source", "claim", "topic", "fabula", "contract", "attribution"))


def _compact_rule(rule: dict[str, Any]) -> dict[str, Any]:
    return _pick(rule, ("id", "title", "scope", "category", "group", "severity", "priority", "validatorType", "observableCriteria", "repairPolicy", "examples"))


def _compact_claim(claim: dict[str, Any]) -> dict[str, Any]:
    return _drop_empty(
        {
            **_pick(claim, ("id", "type", "statement", "allowedUse", "confidence", "risk", "sourceId", "publicEvidenceItemId", "sourceTitle", "sourceUrl")),
            "provenance": _pick(_record(claim.get("provenance")), ("publicEvidenceItemId", "sourceTitle", "sourceUrl", "sourceLabel", "snippet")),
        }
    )


def _compact_evidence_item(item: dict[str, Any]) -> dict[str, Any]:
    return _pick(item, ("id", "sourceTitle", "sourceUrl", "snippet", "summary", "allowedUse", "confidence", "attemptId"))


def _compact_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return _pick(candidate, ("id", "baseCandidateId", "title", "body", "rationale", "usedEvidence", "ruleCoverage", "risks", "weaknesses", "source", "score", "fallbackUsed"))


def _compact_context_summary(context_summary: dict[str, Any]) -> dict[str, Any]:
    return _pick(context_summary, ("brief", "topic", "fabula", "publisher", "publicationSize", "missingContext"))


def _summary_record(payload: dict[str, Any]) -> dict[str, Any]:
    return _pick(payload, ("id", "status", "summary", "reason", "decision", "winnerId", "accepted", "rejected", "findings", "warnings", "repairGoals", "metadata"))


def _sent_counts(payload: Mapping[str, Any]) -> dict[str, int]:
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return {
        "rules": blob.count('"validatorType"') + blob.count('"ruleIds"'),
        "claims": blob.count('"statement"') + blob.count('"claimIds"'),
        "evidenceItems": blob.count('"sourceUrl"') + blob.count('"sourceTitle"'),
        "candidates": blob.count('"body"') + blob.count('"candidateId"'),
        "sourceSnippets": blob.count('"snippet"'),
        "priorDrafts": blob.count('"baseCandidateId"'),
    }


def _quality_risk(contract: SemanticInputContract, payload: Mapping[str, Any], trimmed_counts: Mapping[str, int], prompt_chars: int, max_prompt_chars: int) -> str:
    missing_must_have = [field_name for field_name in contract.must_have if field_name not in payload or payload.get(field_name) in (None, {}, [])]
    if missing_must_have or prompt_chars > max_prompt_chars:
        return "high"
    if any(value > 0 for value in trimmed_counts.values()):
        return "medium"
    return "none"


def _budget_incident(profile: PayloadBudgetProfile, prompt_char_estimate: int, payload_stats: Mapping[str, Any]) -> LlmOperationIncident | None:
    if prompt_char_estimate > int(profile.max_prompt_chars * HARD_PAYLOAD_CHAR_CAP_MULTIPLIER):
        return LlmOperationIncident(
            incident_type=LlmOperationIncidentType.PAYLOAD_TOO_LARGE,
            incident_severity=LlmOperationIncidentSeverity.ERROR,
            probable_cause="compacted-provider-payload-exceeds-hard-cap",
            needs_follow_up=True,
            payload_stats=payload_stats,
        )
    if prompt_char_estimate > profile.max_prompt_chars:
        return LlmOperationIncident(
            incident_type=LlmOperationIncidentType.CONTEXT_OVER_BUDGET,
            incident_severity=LlmOperationIncidentSeverity.WARNING,
            probable_cause="compacted-provider-payload-exceeds-profile-budget",
            needs_follow_up=True,
            payload_stats=payload_stats,
        )
    return None


def _merge_counts(target: dict[str, int], source: Mapping[str, int]) -> None:
    for key, value in source.items():
        target[key] = target.get(key, 0) + int(value)


def _trimmed(target: dict[str, int], key: str, original_count: int, sent_count: int) -> None:
    target[key] = target.get(key, 0) + max(0, original_count - sent_count)


def _drop_empty(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value not in (None, "", [], {})}


def _pick(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys if key in payload and payload[key] not in (None, "", [], {})}


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _execution_mode(value: str | None) -> str:
    normalized = str(value or "standard").strip().lower()
    return normalized if normalized in EXECUTION_MODES else "standard"


def _profile(operation_id: str, operation_kind: str, family: str, mode: str) -> PayloadBudgetProfile:
    caps = {
        "research": (6000, 12000, 22000),
        "evidence": (10000, 18000, 30000),
        "writer": (12000, 24000, 40000),
        "validator": (12000, 22000, 36000),
    }[family]
    index = EXECUTION_MODES.index(mode)
    max_prompt_chars = caps[index]
    scale = (1, 2, 3)[index]
    return PayloadBudgetProfile(
        operation_id=operation_id,
        operation_kind=operation_kind,
        execution_mode=mode,
        max_prompt_chars=max_prompt_chars,
        approx_token_budget=math.ceil(max_prompt_chars / 4),
        max_rules=20 * scale,
        max_claims=12 * scale,
        max_evidence_items=12 * scale,
        max_candidates=2 * scale,
        max_source_snippets=12 * scale,
        max_prior_drafts=1 * scale,
    )


OPERATION_FAMILIES: dict[str, tuple[str, str]] = {
    "sourceIntentAndResearchPlan": ("sourceResearchPlanning", "research"),
    "evidenceSynthesis": ("evidenceSynthesis", "research"),
    "evidenceInterpretation": ("evidenceInterpretation", "evidence"),
    "materialPlan": ("materialPlanning", "evidence"),
    "draftStrategy": ("draftStrategy", "evidence"),
    "rhetoricalPlans": ("rhetoricalPlanning", "evidence"),
    "draftCandidate": ("draftCandidateGeneration", "writer"),
    "llmValidation": ("llmValidation", "validator"),
    "editorialCritique": ("reportOnlyValidator", "validator"),
    "pairwiseRanking": ("pairwiseRanking", "validator"),
    "directedRevision": ("writerRevision", "writer"),
    "finalQualityReviewRepair": ("finalQualityReviewRepair", "validator"),
    "humanCommentRevision": ("hitlWriterRevision", "writer"),
    "humanCommentRevisionQualityCheck": ("hitlQualityCheck", "validator"),
    "alternativeAngleRoute": ("alternativeAngleRoute", "validator"),
    "alternativeAngleCandidate": ("alternativeAngleCandidate", "writer"),
    "publicEvidenceSearch": ("publicEvidenceSearch", "research"),
    "publicEvidenceRead": ("publicEvidenceRead", "research"),
}

DEFAULT_PROFILES: dict[tuple[str, str], PayloadBudgetProfile] = {
    (operation_id, mode): _profile(operation_id, operation_kind, family, mode)
    for operation_id, (operation_kind, family) in OPERATION_FAMILIES.items()
    for mode in EXECUTION_MODES
}

SEMANTIC_CONTRACTS: dict[str, SemanticInputContract] = {
    "sourceIntentAndResearchPlan": SemanticInputContract(
        must_have=("context_artifact", "source_intent"),
        should_have=("draftRunBudget",),
        diagnostic_only=("rawWorkspace",),
        never_send_to_provider=("workspaceSnapshot", "fullWorkspace"),
    ),
    "evidenceSynthesis": SemanticInputContract(
        must_have=("context_artifact", "public_evidence"),
        should_have=("sourceLedger",),
        never_send_to_provider=("fullWorkspace",),
    ),
    "evidenceInterpretation": SemanticInputContract(
        must_have=("context_artifact", "rule_pack"),
        should_have=("context_pack",),
        diagnostic_only=("rawRuleRegistry",),
        never_send_to_provider=("fullWorkspace",),
    ),
    "materialPlan": SemanticInputContract(must_have=("context_artifact", "rule_pack"), should_have=("material_plan",), never_send_to_provider=("sourceLedgerFull", "ruleRegistryFull")),
    "draftStrategy": SemanticInputContract(must_have=("context_artifact", "material_plan", "rule_pack")),
    "rhetoricalPlans": SemanticInputContract(must_have=("draft_strategy", "material_plan", "rule_pack")),
    "draftCandidate": SemanticInputContract(must_have=("direction", "context_summary", "rule_pack", "material_plan", "draft_strategy")),
    "llmValidation": SemanticInputContract(must_have=("candidate", "context_artifact", "rule_pack"), diagnostic_only=("fullValidationTrace",)),
    "editorialCritique": SemanticInputContract(must_have=("candidate", "context_artifact", "rule_pack"), diagnostic_only=("draft_artifact",), never_send_to_provider=("fullCandidatePool",)),
    "pairwiseRanking": SemanticInputContract(must_have=("candidates", "validation_report", "context_artifact", "rule_pack")),
    "directedRevision": SemanticInputContract(must_have=("candidate", "instruction", "context_artifact", "rule_pack", "material_plan"), diagnostic_only=("fullRevisionTrace",)),
    "finalQualityReviewRepair": SemanticInputContract(must_have=("candidate", "validation_report", "context_artifact", "rule_pack", "material_plan")),
    "humanCommentRevision": SemanticInputContract(must_have=("current_version", "editor_comment", "trace_context"), diagnostic_only=("fullDraftRun",), never_send_to_provider=("rawDraftRun",)),
    "humanCommentRevisionQualityCheck": SemanticInputContract(must_have=("base_version", "revised_version", "editor_comment", "trace_context"), diagnostic_only=("fullDraftRun",), never_send_to_provider=("rawDraftRun",)),
    "alternativeAngleRoute": SemanticInputContract(must_have=("validation_report", "context_artifact")),
    "alternativeAngleCandidate": SemanticInputContract(must_have=("direction", "context_artifact", "rule_pack", "material_plan")),
    "publicEvidenceSearch": SemanticInputContract(must_have=("research_task",), never_send_to_provider=("fullWorkspace",)),
    "publicEvidenceRead": SemanticInputContract(must_have=("url",), never_send_to_provider=("fullWorkspace",)),
}
