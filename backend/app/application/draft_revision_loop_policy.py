from typing import Any

from backend.app.domain.draft_revision_loop import RevisionLoopCycle

def acceptance_decision(
    *,
    current_id: str | None,
    revised_id: str | None,
    regression_reasons: list[str],
    resolved_goals: list[str],
    resolved_editorial_goals: list[dict[str, Any]] | None = None,
    regressed_editorial_dimensions: list[dict[str, Any]] | None = None,
    pairwise_winner: str | None,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if regression_reasons and regression_reasons != ["revision-preserves-or-improves-deterministic-validation"]:
        reasons.extend(regression_reasons)
    for regression in regressed_editorial_dimensions or []:
        dimension = str(regression.get("dimension") or "editorial")
        if dimension in {"ideaStrength", "readerValue", "sourceIntegration", "authorStance"}:
            reasons.append(f"editorial-{dimension}-regressed")
    pairwise_wins = revised_id is not None and pairwise_winner == revised_id
    editorial_resolved = bool(resolved_editorial_goals)
    if not resolved_goals and not editorial_resolved and not pairwise_wins:
        reasons.append("revision-did-not-prove-improvement")
    if current_id and pairwise_winner == current_id and not resolved_goals and not editorial_resolved:
        reasons.append("previous-best-won-pairwise")
    return len(reasons) == 0, reasons

def combined_validation(current: dict[str, Any], revised: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidateReports": [*_list(current.get("candidateReports")), *_list(revised.get("candidateReports"))],
        "summary": {},
    }

def pairwise_winner(comparison: dict[str, Any]) -> str | None:
    return _dict(comparison.get("decision")).get("winnerCandidateId")


def failed_cycle(
    *,
    cycle_number: int,
    base_id: str | None,
    goals: list[str],
    editorial_goals: list[dict[str, Any]] | None = None,
    constraints: list[str],
    revision: dict[str, Any],
    ai_run_ids: list[str],
    validation_before: dict[str, Any],
) -> RevisionLoopCycle:
    return RevisionLoopCycle(
        cycle_number=cycle_number,
        base_candidate_id=base_id,
        repair_goals=goals,
        constraints=[*constraints],
        revised_candidate=None,
        validation_before=validation_before,
        validation_after=None,
        pairwise_comparison=None,
        unresolved_goals=goals,
        editorial_goals=editorial_goals or [],
        unresolved_editorial_goals=editorial_goals or [],
        stop_reason="provider-failed",
        accepted=False,
        rejection_reasons=[str(revision.get("reason") or "revision-provider-failed")],
        ai_run_ids=ai_run_ids,
    )


def constraints_from_unresolved(goals: list[str]) -> list[str]:
    return [f"Still unresolved: {goal}" for goal in goals[:8]]


def constraints_from_rejection(reasons: list[str], unresolved: list[str]) -> list[str]:
    return [f"Do not repeat failed move: {reason}" for reason in reasons[:4]] + constraints_from_unresolved(unresolved[:4])


def candidate_id(candidate: dict[str, Any] | None) -> str | None:
    return str(candidate.get("id")) if candidate and candidate.get("id") else None


def dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def string_list(value: Any) -> list[str]:
    return [str(item) for item in value if str(item)] if isinstance(value, list) else []


def last_value(values: list[str]) -> str | None:
    return values[-1] if values else None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
