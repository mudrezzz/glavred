from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PairwiseComparison:
    left_candidate_id: str
    right_candidate_id: str
    winner_candidate_id: str
    reason: str
    decisive_factors: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "leftCandidateId": self.left_candidate_id,
            "rightCandidateId": self.right_candidate_id,
            "winnerCandidateId": self.winner_candidate_id,
            "reason": self.reason,
            "decisiveFactors": self.decisive_factors,
        }


@dataclass(frozen=True)
class RankingDecision:
    winner_candidate_id: str | None
    reason: str
    source: str
    fallback_used: bool = False
    warnings: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "winnerCandidateId": self.winner_candidate_id,
            "reason": self.reason,
            "source": self.source,
            "fallbackUsed": self.fallback_used,
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class PairwiseRankingReport:
    decision: RankingDecision
    comparisons: list[PairwiseComparison] = field(default_factory=list)
    attempts: list[dict[str, Any]] = field(default_factory=list)
    ai_run_ids: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "decision": self.decision.to_payload(),
            "comparisons": [comparison.to_payload() for comparison in self.comparisons],
            "attempts": self.attempts,
            "aiRunIds": self.ai_run_ids,
        }


@dataclass(frozen=True)
class DirectedRevisionInstruction:
    candidate_id: str | None
    status: str
    repair_goals: list[str] = field(default_factory=list)
    source_findings: list[dict[str, Any]] = field(default_factory=list)
    reason: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "status": self.status,
            "repairGoals": self.repair_goals,
            "sourceFindings": self.source_findings,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class RevisionRegressionReport:
    accepted: bool
    reasons: list[str]
    original_counts: dict[str, int]
    revised_counts: dict[str, int]
    validation_report: dict[str, Any] | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "reasons": self.reasons,
            "originalCounts": self.original_counts,
            "revisedCounts": self.revised_counts,
            "validationReport": self.validation_report,
        }
