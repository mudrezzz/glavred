from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RevisionLoopCycle:
    cycle_number: int
    base_candidate_id: str | None
    repair_goals: list[str]
    constraints: list[str]
    revised_candidate: dict[str, Any] | None
    validation_before: dict[str, Any]
    validation_after: dict[str, Any] | None
    pairwise_comparison: dict[str, Any] | None
    resolved_goals: list[str] = field(default_factory=list)
    unresolved_goals: list[str] = field(default_factory=list)
    editorial_goals: list[dict[str, Any]] = field(default_factory=list)
    editorial_dimension_scores: list[dict[str, Any]] = field(default_factory=list)
    resolved_editorial_goals: list[dict[str, Any]] = field(default_factory=list)
    unresolved_editorial_goals: list[dict[str, Any]] = field(default_factory=list)
    new_rejected_moves: list[dict[str, Any]] = field(default_factory=list)
    acceptance_decision: dict[str, Any] = field(default_factory=dict)
    stop_reason: str | None = None
    accepted: bool = False
    rejection_reasons: list[str] = field(default_factory=list)
    ai_run_ids: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "cycleNumber": self.cycle_number,
            "baseCandidateId": self.base_candidate_id,
            "repairGoals": self.repair_goals,
            "constraints": self.constraints,
            "revisedCandidate": self.revised_candidate,
            "validationBefore": self.validation_before,
            "validationAfter": self.validation_after,
            "pairwiseComparison": self.pairwise_comparison,
            "resolvedGoals": self.resolved_goals,
            "unresolvedGoals": self.unresolved_goals,
            "editorialGoals": self.editorial_goals,
            "editorialDimensionScores": self.editorial_dimension_scores,
            "resolvedEditorialGoals": self.resolved_editorial_goals,
            "unresolvedEditorialGoals": self.unresolved_editorial_goals,
            "newRejectedMoves": self.new_rejected_moves,
            "acceptanceDecision": self.acceptance_decision,
            "stopReason": self.stop_reason,
            "accepted": self.accepted,
            "rejectionReasons": self.rejection_reasons,
            "aiRunIds": self.ai_run_ids,
        }


@dataclass(frozen=True)
class RevisionLoopReport:
    status: str
    max_iterations: int
    cycles: list[RevisionLoopCycle]
    final_candidate_id: str | None
    final_source: str
    stop_reason: str
    unresolved_goals: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    detail_stop_reason: str | None = None
    runtime_budget: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "maxIterations": self.max_iterations,
            "cycles": [cycle.to_payload() for cycle in self.cycles],
            "finalCandidateId": self.final_candidate_id,
            "finalSource": self.final_source,
            "stopReason": self.stop_reason,
            "detailStopReason": self.detail_stop_reason,
            "unresolvedGoals": self.unresolved_goals,
            "constraints": self.constraints,
            "runtimeBudget": self.runtime_budget,
        }
