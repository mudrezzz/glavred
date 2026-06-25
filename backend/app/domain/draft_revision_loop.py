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

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "maxIterations": self.max_iterations,
            "cycles": [cycle.to_payload() for cycle in self.cycles],
            "finalCandidateId": self.final_candidate_id,
            "finalSource": self.final_source,
            "stopReason": self.stop_reason,
            "unresolvedGoals": self.unresolved_goals,
            "constraints": self.constraints,
        }
