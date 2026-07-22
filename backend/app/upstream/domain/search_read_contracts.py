"""Owner: upstream.domain

Used by: deterministic RadarRun read allocation, URL read outcomes, and trace serialization.
Does not own: provider transport, result scoring, URL reading, persistence, or signals.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


SearchReadDecisionStatus = Literal[
    "selected",
    "rejected",
    "duplicate",
    "invalid",
    "deferredByBudget",
]
SearchReadOutcomeStatus = Literal["succeeded", "failed", "notRun"]


@dataclass(frozen=True)
class SearchReadDecision:
    raw_result_id: str
    candidate_id: str
    duplicate_group_id: str | None
    status: SearchReadDecisionStatus
    reason: str
    score: int
    url: str
    families: tuple[str, ...] = ()
    evidence_types: tuple[str, ...] = ()
    domain: str = ""
    duplicate_raw_result_ids: tuple[str, ...] = ()
    query_ids: tuple[str, ...] = ()
    intent_ids: tuple[str, ...] = ()
    source_language: str = "unknown"
    source_language_confidence: str = "low"
    source_language_mixed: bool = False
    source_language_reason_codes: tuple[str, ...] = ()
    source_language_eligibility_reason: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "rawResultId": self.raw_result_id,
            "candidateId": self.candidate_id,
            "duplicateGroupId": self.duplicate_group_id,
            "status": self.status,
            "reason": self.reason,
            "score": self.score,
            "url": self.url,
            "families": list(self.families),
            "evidenceTypes": list(self.evidence_types),
            "domain": self.domain,
            "duplicateRawResultIds": list(self.duplicate_raw_result_ids),
            "queryIds": list(self.query_ids),
            "intentIds": list(self.intent_ids),
            "sourceLanguage": {
                "language": self.source_language,
                "confidence": self.source_language_confidence,
                "mixed": self.source_language_mixed,
                "reasonCodes": list(self.source_language_reason_codes),
                "eligibilityReason": self.source_language_eligibility_reason,
            },
        }


@dataclass(frozen=True)
class SearchReadPlan:
    max_reads: int
    quality_floor: int
    required_families: tuple[str, ...]
    selected_candidate_ids: tuple[str, ...]
    decisions: tuple[SearchReadDecision, ...]
    covered_families: tuple[str, ...]
    coverage_gaps: tuple[dict[str, str], ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "maxReads": self.max_reads,
            "qualityFloor": self.quality_floor,
            "requiredFamilies": list(self.required_families),
            "selectedCandidateIds": list(self.selected_candidate_ids),
            "decisions": [item.to_payload() for item in self.decisions],
            "coveredFamilies": list(self.covered_families),
            "readCoverageGaps": [dict(item) for item in self.coverage_gaps],
        }


@dataclass(frozen=True)
class SearchReadOutcome:
    raw_result_id: str
    candidate_id: str
    duplicate_group_id: str | None
    status: SearchReadOutcomeStatus
    material_id: str | None
    readable: bool
    reason: str | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "rawResultId": self.raw_result_id,
            "candidateId": self.candidate_id,
            "duplicateGroupId": self.duplicate_group_id,
            "status": self.status,
            "materialId": self.material_id,
            "readable": self.readable,
        }
        if self.reason:
            payload["reason"] = self.reason
        return payload


__all__ = (
    "SearchReadDecision",
    "SearchReadDecisionStatus",
    "SearchReadOutcome",
    "SearchReadOutcomeStatus",
    "SearchReadPlan",
)
