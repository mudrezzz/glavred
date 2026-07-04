"""Owner: drafting.application.operations

Used by: DraftRun payload budget policy to compact rich artifacts before provider calls.
Does not own: payload budget profiles, semantic contracts, provider adapters, prompt text.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

import json
from typing import Any, Mapping

from backend.app.drafting.application.operations.payload_budget_contracts import PayloadBudgetProfile, PayloadCompactionResult, SemanticInputContract


class DraftRunPayloadCompactor:
    def __init__(self) -> None:
        self._context = ContextArtifactCompactor()
        self._rules = RulePackCompactor()
        self._material = MaterialPlanCompactor()
        self._draft = DraftArtifactCompactor()
        self._trace = TraceContextCompactor()
        self._validation = ValidationReportCompactor()

    def compact(self, payload: Mapping[str, Any], *, profile: PayloadBudgetProfile, contract: SemanticInputContract) -> PayloadCompactionResult:
        suppressed = [field_name for field_name in contract.never_send_to_provider if field_name in payload]
        compact = {
            key: value
            for key, value in dict(payload).items()
            if key not in set(contract.never_send_to_provider).union(contract.diagnostic_only)
        }
        suppressed.extend([field_name for field_name in contract.diagnostic_only if field_name in payload])
        trimmed: dict[str, int] = {}

        self._compact_key(compact, trimmed, "context_artifact", self._context.compact, profile)
        self._compact_key(compact, trimmed, "contextArtifact", self._context.compact, profile)
        self._compact_key(compact, trimmed, "rule_pack", self._rules.compact, profile)
        self._compact_key(compact, trimmed, "rulePack", self._rules.compact, profile)
        self._compact_key(compact, trimmed, "material_plan", self._material.compact, profile)
        self._compact_key(compact, trimmed, "materialPlan", self._material.compact, profile)
        self._compact_candidates(compact, trimmed, profile)
        self._compact_key(compact, trimmed, "draft_artifact", self._draft.compact, profile)
        self._compact_key(compact, trimmed, "trace_context", self._trace.compact, profile)
        self._compact_key(compact, trimmed, "traceContext", self._trace.compact, profile)
        self._compact_key(compact, trimmed, "deterministic_report", self._validation.compact, profile)
        self._compact_key(compact, trimmed, "llm_validation_report", self._validation.compact, profile)
        self._compact_key(compact, trimmed, "validation_report", self._validation.compact, profile)
        return PayloadCompactionResult(payload=compact, trimmed_counts=trimmed, suppressed_fields=tuple(sorted(set(suppressed))))

    def _compact_key(self, payload: dict[str, Any], trimmed: dict[str, int], key: str, compact: Any, profile: PayloadBudgetProfile) -> None:
        if key not in payload:
            return
        payload[key], counts = compact(_record(payload[key]), profile)
        CountAccumulator.merge(trimmed, counts)

    def _compact_candidates(self, payload: dict[str, Any], trimmed: dict[str, int], profile: PayloadBudgetProfile) -> None:
        if "candidate" in payload:
            payload["candidate"] = CandidatePayloadCompactor.compact(_record(payload["candidate"]))
        if "candidates" not in payload:
            return
        candidates = _records(payload["candidates"])
        payload["candidates"] = [CandidatePayloadCompactor.compact(candidate) for candidate in candidates[: profile.max_candidates]]
        CountAccumulator.trimmed(trimmed, "candidates", len(candidates), len(payload["candidates"]))


class ContextArtifactCompactor:
    def __init__(self) -> None:
        self._ledger = SourceLedgerCompactor()
        self._public_evidence = PublicEvidenceCompactor()
        self._synthesis = EvidenceSynthesisCompactor()

    def compact(self, context_artifact: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        counts: dict[str, int] = {}
        source_ledger, ledger_counts = self._ledger.compact(_record(context_artifact.get("sourceLedger")), profile)
        public_evidence, evidence_counts = self._public_evidence.compact(_record(context_artifact.get("publicEvidence")), profile)
        synthesis, synthesis_counts = self._synthesis.compact(_record(context_artifact.get("evidenceSynthesis")), profile)
        CountAccumulator.merge(counts, ledger_counts)
        CountAccumulator.merge(counts, evidence_counts)
        CountAccumulator.merge(counts, synthesis_counts)
        compact = {
            "contextSummary": _pick(_record(context_artifact.get("contextSummary")), ("brief", "topic", "fabula", "publisher", "publicationSize", "missingContext")),
            "postContract": context_artifact.get("postContract"),
            "sourceLedger": source_ledger,
            "publicEvidence": public_evidence,
            "evidenceSynthesis": synthesis,
            "draftRunBudget": context_artifact.get("draftRunBudget"),
        }
        return _drop_empty(compact), counts


class RulePackCompactor:
    def compact(self, rule_pack: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        snapshot = _record(rule_pack.get("ruleRegistrySnapshot"))
        rules = _records(snapshot.get("rules"))
        selected = [self._compact_rule(rule) for rule in self._select_rules(rules, profile.max_rules)]
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
        CountAccumulator.trimmed(trimmed, "rules", len(rules), len(selected))
        return compact, trimmed

    def _select_rules(self, rules: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
        relevant = [rule for rule in rules if self._is_relevant_rule(rule)]
        return relevant[:limit] if relevant else rules[:limit]

    def _is_relevant_rule(self, rule: dict[str, Any]) -> bool:
        severity = str(rule.get("severity") or rule.get("priority") or "").lower()
        searchable = " ".join(str(rule.get(key) or "") for key in ("id", "title", "scope", "category", "group", "validatorType", "source")).lower()
        return severity in {"hard", "critical"} or any(
            marker in searchable
            for marker in ("evidence", "source", "claim", "topic", "fabula", "contract", "attribution")
        )

    def _compact_rule(self, rule: dict[str, Any]) -> dict[str, Any]:
        return _pick(rule, ("id", "title", "scope", "category", "group", "severity", "priority", "validatorType", "observableCriteria", "repairPolicy", "examples"))


class SourceLedgerCompactor:
    def compact(self, source_ledger: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        claims = _records(source_ledger.get("claims"))
        selected = [EvidenceRecordCompactor.compact_claim(claim) for claim in claims[: profile.max_claims]]
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
        CountAccumulator.trimmed(counts, "claims", len(claims), len(selected))
        return compact, counts


class PublicEvidenceCompactor:
    def compact(self, public_evidence: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        items = _records(public_evidence.get("items"))
        selected = [EvidenceRecordCompactor.compact_evidence_item(item) for item in items[: profile.max_evidence_items]]
        counts: dict[str, int] = {}
        CountAccumulator.trimmed(counts, "evidenceItems", len(items), len(selected))
        return _drop_empty({"items": selected, "budget": public_evidence.get("budget") or public_evidence.get("budgetTrace")}), counts


class EvidenceSynthesisCompactor:
    def compact(self, evidence_synthesis: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        claims = _records(evidence_synthesis.get("externalClaims"))
        selected = [EvidenceRecordCompactor.compact_claim(claim) for claim in claims[: profile.max_claims]]
        counts: dict[str, int] = {}
        CountAccumulator.trimmed(counts, "synthesisClaims", len(claims), len(selected))
        return _drop_empty(
            {
                "externalClaims": selected,
                "decisions": _records(evidence_synthesis.get("decisions"))[: profile.max_claims],
                "warnings": _records(evidence_synthesis.get("warnings"))[: min(8, profile.max_claims)],
                "fallbackUsed": evidence_synthesis.get("fallbackUsed"),
            }
        ), counts


class MaterialPlanCompactor:
    def compact(self, material_plan: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        counts: dict[str, int] = {}
        compact = _pick(
            material_plan,
            ("status", "thesis", "angle", "readerValue", "structure", "sections", "outline", "warnings", "rejectionReasons", "evidenceInterpretationSummary"),
        )
        for key in ("usableEvidence", "usableEvidenceCandidates", "evidenceCandidates"):
            if key in material_plan:
                values = _records(material_plan.get(key))
                compact[key] = values[: profile.max_evidence_items]
                CountAccumulator.trimmed(counts, key, len(values), len(compact[key]))
        return _drop_empty(compact), counts


class DraftArtifactCompactor:
    def compact(self, draft_artifact: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        candidates = _records(draft_artifact.get("candidates"))
        compact = {
            **_pick(draft_artifact, ("status", "scorecard", "selectedCandidateId", "fallbackUsed")),
            "candidates": [CandidatePayloadCompactor.compact(candidate) for candidate in candidates[: profile.max_candidates]],
        }
        counts: dict[str, int] = {}
        CountAccumulator.trimmed(counts, "candidates", len(candidates), len(compact["candidates"]))
        return _drop_empty(compact), counts


class TraceContextCompactor:
    def compact(self, trace_context: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        compact = _pick(trace_context, ("draftRunId", "traceStatus", "validationSummary", "unresolvedRisks"))
        compact["finalQualityGate"] = SummaryRecordCompactor.compact(_record(trace_context.get("finalQualityGate")))
        compact["alternativeAngleTournament"] = SummaryRecordCompactor.compact(_record(trace_context.get("alternativeAngleTournament")))
        revision_loop = _record(trace_context.get("revisionLoop"))
        prior_drafts = _records(revision_loop.get("cycles"))[: profile.max_prior_drafts]
        compact["revisionLoop"] = _drop_empty(
            {
                "status": revision_loop.get("status"),
                "cycleCount": len(_records(revision_loop.get("cycles"))),
                "cycles": [SummaryRecordCompactor.compact(cycle) for cycle in prior_drafts],
            }
        )
        counts: dict[str, int] = {}
        CountAccumulator.trimmed(counts, "priorDrafts", len(_records(revision_loop.get("cycles"))), len(prior_drafts))
        return _drop_empty(compact), counts


class ValidationReportCompactor:
    def compact(self, report: dict[str, Any], profile: PayloadBudgetProfile) -> tuple[dict[str, Any], dict[str, int]]:
        candidate_reports = _records(report.get("candidateReports"))
        compact = _pick(report, ("status", "summary", "overallStatus", "reason"))
        compact["candidateReports"] = [SummaryRecordCompactor.compact(item) for item in candidate_reports[: profile.max_candidates]]
        counts: dict[str, int] = {}
        CountAccumulator.trimmed(counts, "candidateReports", len(candidate_reports), len(compact["candidateReports"]))
        return _drop_empty(compact), counts


class EvidenceRecordCompactor:
    @staticmethod
    def compact_claim(claim: dict[str, Any]) -> dict[str, Any]:
        return _drop_empty(
            {
                **_pick(claim, ("id", "type", "statement", "allowedUse", "confidence", "risk", "sourceId", "publicEvidenceItemId", "sourceTitle", "sourceUrl")),
                "provenance": _pick(_record(claim.get("provenance")), ("publicEvidenceItemId", "sourceTitle", "sourceUrl", "sourceLabel", "snippet")),
            }
        )

    @staticmethod
    def compact_evidence_item(item: dict[str, Any]) -> dict[str, Any]:
        return _pick(item, ("id", "sourceTitle", "sourceUrl", "snippet", "summary", "allowedUse", "confidence", "attemptId"))


class CandidatePayloadCompactor:
    @staticmethod
    def compact(candidate: dict[str, Any]) -> dict[str, Any]:
        return _pick(candidate, ("id", "baseCandidateId", "title", "body", "rationale", "usedEvidence", "ruleCoverage", "risks", "weaknesses", "source", "score", "fallbackUsed"))


class SummaryRecordCompactor:
    @staticmethod
    def compact(payload: dict[str, Any]) -> dict[str, Any]:
        return _pick(payload, ("id", "status", "summary", "reason", "decision", "winnerId", "accepted", "rejected", "findings", "warnings", "repairGoals", "metadata"))


class PayloadBudgetCounters:
    @staticmethod
    def sent_counts(payload: Mapping[str, Any]) -> dict[str, int]:
        blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return {
            "rules": blob.count('"validatorType"') + blob.count('"ruleIds"'),
            "claims": blob.count('"statement"') + blob.count('"claimIds"'),
            "evidenceItems": blob.count('"sourceUrl"') + blob.count('"sourceTitle"'),
            "candidates": blob.count('"body"') + blob.count('"candidateId"'),
            "sourceSnippets": blob.count('"snippet"'),
            "priorDrafts": blob.count('"baseCandidateId"'),
        }


class CountAccumulator:
    @staticmethod
    def merge(target: dict[str, int], source: Mapping[str, int]) -> None:
        for key, value in source.items():
            target[key] = target.get(key, 0) + int(value)

    @staticmethod
    def trimmed(target: dict[str, int], key: str, original_count: int, sent_count: int) -> None:
        target[key] = target.get(key, 0) + max(0, original_count - sent_count)


def _drop_empty(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value not in (None, "", [], {})}


def _pick(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys if key in payload and payload[key] not in (None, "", [], {})}


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
