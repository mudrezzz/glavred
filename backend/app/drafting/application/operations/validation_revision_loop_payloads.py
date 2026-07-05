"""Owner: drafting.application.operations

Used by: validation revision-loop runtime to build trace-safe loop payloads.
Does not own: provider calls, revision acceptance decisions, persistence, UI rendering.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from dataclasses import dataclass
from typing import Any

from backend.app.drafting.application.revision.draft_revision_loop_policy import RevisionLoopPolicy
from backend.app.domain.draft_revision_loop import RevisionLoopCycle, RevisionLoopReport


@dataclass(frozen=True)
class DraftRevisionLoopResult:
    report: RevisionLoopReport
    final_candidate: dict[str, Any] | None
    first_instruction: dict[str, Any] | None
    last_revision: dict[str, Any] | None
    last_regression: dict[str, Any] | None
    ai_run_ids: list[str]


def successful_cycle(
    *,
    cycle_number: int,
    current_id: str | None,
    revised: dict[str, Any],
    validation_before: dict[str, Any],
    validation_after: dict[str, Any],
    comparison: dict[str, Any],
    repair_goals: list[str],
    constraints: list[str],
    goal_result: dict[str, list[str]],
    editorial_goals: list[dict[str, Any]],
    editorial_result: dict[str, Any],
    new_rejected_moves: list[dict[str, Any]],
    accepted: bool,
    decision_reasons: list[str],
    stop_reason: str,
    ai_run_ids: list[str],
) -> RevisionLoopCycle:
    return RevisionLoopCycle(
        cycle_number=cycle_number,
        base_candidate_id=current_id,
        repair_goals=repair_goals,
        constraints=[*constraints],
        revised_candidate=revised,
        validation_before=validation_before,
        validation_after=validation_after,
        pairwise_comparison=comparison,
        resolved_goals=goal_result["resolved"],
        unresolved_goals=goal_result["unresolved"],
        editorial_goals=editorial_goals,
        editorial_dimension_scores=editorial_result["editorialDimensionScores"],
        resolved_editorial_goals=editorial_result["resolvedEditorialGoals"],
        unresolved_editorial_goals=editorial_result["unresolvedEditorialGoals"],
        new_rejected_moves=new_rejected_moves,
        acceptance_decision={"accepted": accepted, "reasons": decision_reasons},
        stop_reason=stop_reason,
        accepted=accepted,
        rejection_reasons=[] if accepted else decision_reasons,
        ai_run_ids=ai_run_ids,
    )


def revision_loop_report(
    *,
    current: dict[str, Any] | None,
    cycles: list[RevisionLoopCycle],
    max_iterations: int,
    stop_reason: str,
    constraints: list[str],
    detail_stop_reason: str | None,
    runtime_budget: dict[str, Any],
) -> RevisionLoopReport:
    return RevisionLoopReport(
        status="succeeded" if current else "blocked",
        max_iterations=max_iterations,
        cycles=cycles,
        final_candidate_id=RevisionLoopPolicy().candidate_id(current),
        final_source="revisionLoop" if any(cycle.accepted for cycle in cycles) else "originalCandidate",
        stop_reason=stop_reason,
        unresolved_goals=_unresolved_goals(cycles),
        constraints=constraints,
        detail_stop_reason=detail_stop_reason,
        runtime_budget=runtime_budget,
    )


def _unresolved_goals(cycles: list[RevisionLoopCycle]) -> list[str]:
    if not cycles:
        return []
    editorial_goals = [str(item.get("message")) for item in cycles[-1].unresolved_editorial_goals if item.get("message")]
    return [*cycles[-1].unresolved_goals, *editorial_goals]
