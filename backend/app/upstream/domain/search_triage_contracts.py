"""Owner: upstream.domain

Used by: deterministic RadarRun triage orchestration and trace serialization.
Does not own: provider transport, URL reading, persistence, benchmark grading, or signals.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.app.upstream.domain.search_read_contracts import (
    SearchReadDecision,
    SearchReadDecisionStatus,
    SearchReadOutcome,
    SearchReadOutcomeStatus,
    SearchReadPlan,
)
from backend.app.upstream.domain.search_result_contracts import (
    SearchDuplicateGroup,
    SearchResultCandidate,
    SearchResultDimensionScores,
)


@dataclass(frozen=True)
class SearchTriageReport:
    policy_version: str
    candidates: tuple[SearchResultCandidate, ...]
    scores: dict[str, SearchResultDimensionScores]
    duplicate_groups: tuple[SearchDuplicateGroup, ...]
    read_plan: SearchReadPlan
    read_outcomes: tuple[SearchReadOutcome, ...] = ()
    decision_counts: dict[str, int] = field(default_factory=dict)

    def with_read_outcomes(self, outcomes: list[SearchReadOutcome]) -> "SearchTriageReport":
        return SearchTriageReport(
            policy_version=self.policy_version,
            candidates=self.candidates,
            scores=self.scores,
            duplicate_groups=self.duplicate_groups,
            read_plan=self.read_plan,
            read_outcomes=tuple(outcomes),
            decision_counts=self.decision_counts,
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "policyVersion": self.policy_version,
            "candidates": [
                {
                    **candidate.to_payload(),
                    "scores": self.scores[candidate.id].to_payload() if candidate.id in self.scores else None,
                }
                for candidate in self.candidates
            ],
            "duplicateGroups": [item.to_payload() for item in self.duplicate_groups],
            "readPlan": self.read_plan.to_payload(),
            "readCoverage": {
                "requiredFamilies": list(self.read_plan.required_families),
                "coveredFamilies": list(self.read_plan.covered_families),
            },
            "readCoverageGaps": [dict(item) for item in self.read_plan.coverage_gaps],
            "readOutcomes": [item.to_payload() for item in self.read_outcomes],
            "decisionCounts": self.decision_counts,
        }


@dataclass(frozen=True)
class SearchTriageResult:
    report: SearchTriageReport
    raw_results: tuple[dict[str, Any], ...]
    selected_for_read: tuple[dict[str, Any], ...]
    rejected_before_read: tuple[dict[str, Any], ...]


__all__ = (
    "SearchDuplicateGroup",
    "SearchReadDecision",
    "SearchReadDecisionStatus",
    "SearchReadOutcome",
    "SearchReadOutcomeStatus",
    "SearchReadPlan",
    "SearchResultCandidate",
    "SearchResultDimensionScores",
    "SearchTriageReport",
    "SearchTriageResult",
)
