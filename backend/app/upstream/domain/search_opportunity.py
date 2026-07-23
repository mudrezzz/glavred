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
    unresolved_handles: dict[str, int] = field(default_factory=dict)
    version: str = "search-opportunity-coverage-v1"

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
            "unresolvedHandles": dict(self.unresolved_handles),
        }


__all__ = ("SearchOpportunityCoverageReport", "SearchOpportunityStatus", "YieldMetric")
