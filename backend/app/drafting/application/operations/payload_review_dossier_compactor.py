"""Owner: drafting.application.operations

Used by: Provider-input budget compaction for review, ranking, revision, and final gate dossiers.
Does not own: dossier selection, prompt wording, provider calls, or review decisions.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.app.drafting.application.operations.payload_budget_contracts import PayloadBudgetProfile
from backend.app.drafting.application.operations.payload_final_quality_dossier_compactor import FinalQualityDossierSectionCompactor


_REVIEW_OPERATIONS = {
    "llmValidation",
    "pairwiseRanking",
    "directedRevision",
    "finalQualityReviewRepair",
}


class ReviewDossierPayloadCompactor:
    """Bounds nested dossier sections while preserving operation must-have inputs."""

    def __init__(self) -> None:
        self._final_quality = FinalQualityDossierSectionCompactor()

    def compact(
        self,
        payload: dict[str, Any],
        profile: PayloadBudgetProfile,
    ) -> tuple[dict[str, Any], dict[str, int]]:
        if profile.operation_id not in _REVIEW_OPERATIONS or "dossierId" not in payload:
            return payload, {}
        compact = dict(payload)
        trimmed: dict[str, int] = {}
        self._replace(compact, "candidate", self._candidate(compact.get("candidate")))
        self._replace(compact, "candidates", self._candidates(compact.get("candidates"), profile, trimmed))
        self._replace(compact, "evidence", self._records(compact.get("evidence"), self._evidence_limit(profile), self._evidence, "evidence", trimmed))
        self._replace(compact, "rules", self._records(compact.get("rules"), self._rules_limit(profile), self._rule, "rules", trimmed))
        self._replace(compact, "validationIssues", self._records(compact.get("validationIssues"), self._issue_limit(profile), self._issue, "validationIssues", trimmed))
        self._replace(compact, "postContract", self._post_contract(compact.get("postContract")))
        self._replace(compact, "revisionInstruction", self._revision_instruction(compact.get("revisionInstruction"), trimmed))
        compact, final_counts = self._final_quality.compact(compact)
        trimmed.update(final_counts)
        return compact, trimmed

    def _candidate(self, value: Any) -> dict[str, Any]:
        candidate = self._mapping(value)
        result = self._pick(candidate, ("id", "title", "body", "rhetoricalPlanId", "baseCandidateId"))
        result["usedEvidence"] = self._identifiers(candidate.get("usedEvidence"), 6)
        result["ruleCoverage"] = self._identifiers(candidate.get("ruleCoverage"), 6)
        return self._drop_empty(result)

    def _candidates(self, value: Any, profile: PayloadBudgetProfile, trimmed: dict[str, int]) -> list[dict[str, Any]]:
        records = self._record_list(value)
        limit = min(profile.max_candidates, 4)
        selected = records[:limit]
        self._count_trimmed(trimmed, "candidates", len(records), len(selected))
        window_limit = {"smoke": 240, "standard": 300, "full": 450}.get(profile.execution_mode, 300)
        result = []
        for candidate in selected:
            windows = {
                str(key): self._text(child, window_limit)
                for key, child in self._mapping(candidate.get("bodyWindows")).items()
                if child
            }
            compact = self._pick(candidate, ("id", "title", "rhetoricalPlanId", "bodyChars", "paragraphCount"))
            compact["bodyWindows"] = windows
            compact["usedEvidence"] = self._identifiers(candidate.get("usedEvidence"), 8)
            compact["ruleCoverage"] = self._identifiers(candidate.get("ruleCoverage"), 8)
            compact["risks"] = [self._text(item, 180) for item in self._list(candidate.get("risks"))[:1]]
            compact["weaknesses"] = [self._text(item, 180) for item in self._list(candidate.get("weaknesses"))[:1]]
            result.append(self._drop_empty(compact))
        return result

    def _evidence(self, value: Mapping[str, Any]) -> dict[str, Any]:
        return self._drop_empty({
            **self._pick(value, ("id", "type", "confidence", "allowedUse", "sourceId", "sourceTitle", "sourceUrl")),
            "statement": self._text(value.get("statement"), 320),
            "summary": self._text(value.get("summary"), 260),
            "snippet": self._text(value.get("snippet"), 260),
        })

    def _rule(self, value: Mapping[str, Any]) -> dict[str, Any]:
        return self._drop_empty({
            **self._pick(value, ("id", "severity", "category", "source")),
            "statement": self._text(value.get("statement") or value.get("rule"), 280),
        })

    def _issue(self, value: Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(value.get("findings"), list):
            return self._drop_empty({
                **self._pick(value, ("candidateId", "findingCount")),
                "findings": [self._ranking_issue(item) for item in self._record_list(value.get("findings"))[:2]],
            })
        return self._drop_empty({
            **self._pick(value, ("id", "candidateId", "source", "validatorId", "severity")),
            "message": self._text(value.get("message"), 240),
            "repairGuidance": self._text(value.get("repairGuidance"), 240),
            "evidenceExcerpt": self._text(value.get("evidenceExcerpt"), 180),
            "ruleIds": self._identifiers(value.get("ruleIds"), 8),
            "claimIds": self._identifiers(value.get("claimIds"), 8),
        })

    def _ranking_issue(self, value: Mapping[str, Any]) -> dict[str, Any]:
        return self._drop_empty({
            **self._pick(value, ("id", "candidateId", "source", "validatorId", "severity")),
            "message": self._text(value.get("message"), 180),
            "repairGuidance": self._text(value.get("repairGuidance"), 180),
            "evidenceExcerpt": self._text(value.get("evidenceExcerpt"), 100),
            "ruleIds": self._identifiers(value.get("ruleIds"), 6),
            "claimIds": self._identifiers(value.get("claimIds"), 6),
        })

    def _post_contract(self, value: Any) -> dict[str, Any]:
        contract = self._mapping(value)
        result = {
            **self._pick(contract, ("title", "thesis", "audience", "cta", "platform", "publicationSizeContract")),
            "claims": self._bounded(contract.get("claims"), list_limit=4, text_limit=240),
            "forbiddenMoves": self._bounded(contract.get("forbiddenMoves"), list_limit=6, text_limit=180),
            "evidenceObligations": self._bounded(contract.get("evidenceObligations"), list_limit=4, text_limit=220),
            "fabulaObligations": self._bounded(contract.get("fabulaObligations"), list_limit=4, text_limit=220),
            "riskNotes": self._bounded(contract.get("riskNotes"), list_limit=4, text_limit=180),
        }
        return self._drop_empty(result)

    def _revision_instruction(self, value: Any, trimmed: dict[str, int]) -> dict[str, Any]:
        instruction = self._mapping(value)
        return self._drop_empty({
            **self._pick(instruction, ("candidateId", "status", "reason")),
            "repairGoals": self._bounded_list(instruction.get("repairGoals"), 4, 280, "revisionInstruction.repairGoals", trimmed),
            "sourceFindings": self._records(instruction.get("sourceFindings"), 3, self._issue, "revisionInstruction.sourceFindings", trimmed),
            "constraints": self._bounded(instruction.get("constraints"), list_limit=4, text_limit=240),
            "editorialGoals": self._bounded_list(instruction.get("editorialGoals"), 3, 260, "revisionInstruction.editorialGoals", trimmed),
            "rejectedMoves": self._bounded_list(instruction.get("rejectedMoves"), 2, 220, "revisionInstruction.rejectedMoves", trimmed),
        })

    def _records(self, value: Any, limit: int, mapper: Any, key: str, trimmed: dict[str, int]) -> list[dict[str, Any]]:
        records = self._record_list(value)
        selected = records[:limit]
        self._count_trimmed(trimmed, key, len(records), len(selected))
        return [mapper(item) for item in selected]

    def _bounded_list(self, value: Any, limit: int, text_limit: int, key: str, trimmed: dict[str, int]) -> list[Any]:
        items = self._list(value)
        selected = items[:limit]
        self._count_trimmed(trimmed, key, len(items), len(selected))
        return [self._bounded(item, list_limit=8, text_limit=text_limit) for item in selected]

    def _bounded(self, value: Any, *, list_limit: int, text_limit: int) -> Any:
        if isinstance(value, str):
            return self._text(value, text_limit)
        if isinstance(value, Mapping):
            return {str(key): self._bounded(child, list_limit=list_limit, text_limit=text_limit) for key, child in list(value.items())[:12]}
        if isinstance(value, list):
            return [self._bounded(child, list_limit=list_limit, text_limit=text_limit) for child in value[:list_limit]]
        return value

    def _evidence_limit(self, profile: PayloadBudgetProfile) -> int:
        return {"llmValidation": 2, "pairwiseRanking": 1, "directedRevision": 2, "finalQualityReviewRepair": 1}[profile.operation_id]

    def _rules_limit(self, profile: PayloadBudgetProfile) -> int:
        return {"llmValidation": 4, "pairwiseRanking": 0, "directedRevision": 4, "finalQualityReviewRepair": 0}[profile.operation_id]

    def _issue_limit(self, profile: PayloadBudgetProfile) -> int:
        return {"llmValidation": 6, "pairwiseRanking": 4, "directedRevision": 4, "finalQualityReviewRepair": 4}[profile.operation_id]

    def _identifiers(self, value: Any, limit: int) -> list[str]:
        result = []
        for item in self._list(value)[:limit]:
            if isinstance(item, Mapping):
                identity = item.get("id") or item.get("claimId") or item.get("ruleId")
            else:
                identity = item
            if identity not in (None, ""):
                result.append(self._text(identity, 120))
        return result

    def _replace(self, payload: dict[str, Any], key: str, value: Any) -> None:
        if key in payload:
            payload[key] = value

    def _pick(self, value: Mapping[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
        return {key: value.get(key) for key in keys if value.get(key) not in (None, [], {})}

    def _mapping(self, value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    def _list(self, value: Any) -> list[Any]:
        return list(value) if isinstance(value, list) else []

    def _record_list(self, value: Any) -> list[dict[str, Any]]:
        return [dict(item) for item in self._list(value) if isinstance(item, Mapping)]

    def _text(self, value: Any, limit: int) -> str:
        return str(value or "")[:limit]

    def _drop_empty(self, value: Mapping[str, Any]) -> dict[str, Any]:
        return {key: child for key, child in value.items() if child not in (None, "", [], {})}

    def _count_trimmed(self, trimmed: dict[str, int], key: str, total: int, sent: int) -> None:
        if total > sent:
            trimmed[key] = total - sent


__all__ = ("ReviewDossierPayloadCompactor",)
