"""Owner: upstream.domain

Used by: post-scoring useful-yield diagnostics and RadarRun trace serialization.
Does not own: search planning, extraction, utility scoring, persistence, or UI.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


SearchOpportunityStatus = Literal["sufficient", "partial", "zeroYield", "inconclusive"]
SearchFailureStage = Literal["providerSearch", "triage", "read", "signalExtraction", "signalScoring"]
EvidenceDeliveryStage = Literal[
    "planned",
    "queryExecuted",
    "resultFound",
    "selectedForRead",
    "readableEvidence",
    "usedBySignal",
    "corroborated",
]


@dataclass(frozen=True)
class YieldMetric:
    count: int
    denominator: int

    def to_payload(self) -> dict[str, int | float]:
        return {
            "count": self.count,
            "denominator": self.denominator,
            "ratio": round(self.count / self.denominator, 4) if self.denominator else 0.0,
        }


@dataclass(frozen=True)
class SearchRequirementCoverage:
    requirement_id: str
    role: str
    mode: str
    title: str
    furthest_stage: EvidenceDeliveryStage
    delivered: bool
    stop_reason: str | None
    query_ids: tuple[str, ...] = ()
    raw_result_ids: tuple[str, ...] = ()
    supported_raw_result_ids: tuple[str, ...] = ()
    read_decision_raw_result_ids: tuple[str, ...] = ()
    material_ids: tuple[str, ...] = ()
    fragment_ids: tuple[str, ...] = ()
    signal_ids: tuple[str, ...] = ()
    corroborating_material_ids: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "requirementId": self.requirement_id,
            "role": self.role,
            "mode": self.mode,
            "title": self.title,
            "furthestStage": self.furthest_stage,
            "delivered": self.delivered,
            "stopReason": self.stop_reason,
            "queryIds": list(self.query_ids),
            "rawResultIds": list(self.raw_result_ids),
            "supportedRawResultIds": list(self.supported_raw_result_ids),
            "readDecisionRawResultIds": list(self.read_decision_raw_result_ids),
            "materialIds": list(self.material_ids),
            "fragmentIds": list(self.fragment_ids),
            "signalIds": list(self.signal_ids),
            "corroboratingMaterialIds": list(self.corroborating_material_ids),
        }


@dataclass(frozen=True)
class SearchOpportunityCoverageReport:
    status: SearchOpportunityStatus
    planned_requirement_ids: tuple[str, ...]
    executed_requirement_ids: tuple[str, ...]
    uncovered_requirements: tuple[dict[str, Any], ...]
    family_coverage: dict[str, list[str]]
    evidence_coverage: dict[str, list[str]]
    counts: dict[str, int]
    extracted_signal_yield: YieldMetric
    review_eligible_yield: YieldMetric
    rejected_yield: YieldMetric
    recommendation_distribution: dict[str, int]
    reason_distribution: dict[str, int]
    first_failure_stage: SearchFailureStage | None
    reason_codes: tuple[str, ...]
    remediation: tuple[str, ...]
    lineage: tuple[dict[str, Any], ...]
    requirement_coverage: tuple[SearchRequirementCoverage, ...] = ()
    delivered_requirement_ids: tuple[str, ...] = ()
    required_delivery_gaps: tuple[dict[str, Any], ...] = ()
    optional_delivery_gaps: tuple[dict[str, Any], ...] = ()
    corroboration_coverage: dict[str, Any] = field(default_factory=dict)
    unresolved_handles: dict[str, int] = field(default_factory=dict)
    version: str = "search-opportunity-coverage-v2"

    def to_payload(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "status": self.status,
            "plannedRequirementIds": list(self.planned_requirement_ids),
            "executedRequirementIds": list(self.executed_requirement_ids),
            "uncoveredRequiredSearchRequirements": [dict(item) for item in self.uncovered_requirements],
            "familyCoverage": self.family_coverage,
            "evidenceCoverage": self.evidence_coverage,
            "counts": dict(self.counts),
            "extractedSignalYield": self.extracted_signal_yield.to_payload(),
            "reviewEligibleYield": self.review_eligible_yield.to_payload(),
            "rejectedYield": self.rejected_yield.to_payload(),
            "recommendationDistribution": dict(self.recommendation_distribution),
            "reasonDistribution": dict(self.reason_distribution),
            "firstFailureStage": self.first_failure_stage,
            "reasonCodes": list(self.reason_codes),
            "remediation": list(self.remediation),
            "lineage": [dict(item) for item in self.lineage],
            "requirementCoverage": [item.to_payload() for item in self.requirement_coverage],
            "deliveredRequirementIds": list(self.delivered_requirement_ids),
            "requiredDeliveryGaps": [dict(item) for item in self.required_delivery_gaps],
            "optionalDeliveryGaps": [dict(item) for item in self.optional_delivery_gaps],
            "corroborationCoverage": dict(self.corroboration_coverage),
            "unresolvedHandles": dict(self.unresolved_handles),
        }


__all__ = (
    "EvidenceDeliveryStage",
    "SearchOpportunityCoverageReport",
    "SearchOpportunityStatus",
    "SearchRequirementCoverage",
    "YieldMetric",
)
