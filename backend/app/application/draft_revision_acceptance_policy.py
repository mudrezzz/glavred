from typing import Any


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
    rejection_reasons: list[str] = []
    if regression_reasons and regression_reasons != ["revision-preserves-or-improves-deterministic-validation"]:
        rejection_reasons.extend(regression_reasons)
    for regression in regressed_editorial_dimensions or []:
        dimension = str(regression.get("dimension") or "editorial")
        if dimension in {"ideaStrength", "readerValue", "sourceIntegration", "authorStance"}:
            rejection_reasons.append(f"editorial-{dimension}-regressed")
    pairwise_wins = revised_id is not None and pairwise_winner == revised_id
    editorial_resolved = bool(resolved_editorial_goals)
    if not resolved_goals and not editorial_resolved and not pairwise_wins:
        rejection_reasons.append("revision-did-not-prove-improvement")
    if current_id and pairwise_winner == current_id and not resolved_goals and not editorial_resolved:
        rejection_reasons.append("previous-best-won-pairwise")
    if rejection_reasons:
        return False, rejection_reasons
    return True, _acceptance_reasons(regression_reasons, resolved_goals, editorial_resolved, pairwise_wins)


def _acceptance_reasons(
    regression_reasons: list[str],
    resolved_goals: list[str],
    editorial_resolved: bool,
    pairwise_wins: bool,
) -> list[str]:
    reasons: list[str] = []
    if resolved_goals:
        reasons.append("resolved-validator-goals")
    if editorial_resolved:
        reasons.append("resolved-editorial-goals")
    if pairwise_wins:
        reasons.append("pairwise-selected-revised")
    if regression_reasons == ["revision-preserves-or-improves-deterministic-validation"] or not regression_reasons:
        reasons.append("no-deterministic-regression")
    return reasons
