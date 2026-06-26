from typing import Any

from backend.app.application.draft_editorial_revision_goals import EDITORIAL_DIMENSIONS


class DraftEditorialRevisionEvaluator:
    def evaluate(
        self,
        *,
        editorial_goals: list[dict[str, Any]],
        pairwise_comparison: dict[str, Any],
        current_id: str | None,
        revised_id: str | None,
    ) -> dict[str, Any]:
        scores = _dimension_scores(pairwise_comparison, current_id, revised_id)
        resolved: list[dict[str, Any]] = []
        unresolved: list[dict[str, Any]] = []
        regressed: list[dict[str, Any]] = []
        for goal in editorial_goals:
            dimension = str(goal.get("dimension") or "")
            score = next((item for item in scores if item.get("dimension") == dimension), None)
            winner = score.get("winnerCandidateId") if score else None
            if revised_id and winner == revised_id:
                resolved.append(goal)
            else:
                unresolved.append(goal)
                if current_id and winner == current_id and dimension != "validatorHealth":
                    regressed.append({"dimension": dimension, "goalId": goal.get("id"), "reason": score.get("reason") if score else "dimension-not-improved"})
        goal_dimensions = {str(goal.get("dimension") or "") for goal in editorial_goals}
        for score in scores:
            dimension = str(score.get("dimension") or "")
            if dimension not in goal_dimensions and current_id and score.get("winnerCandidateId") == current_id:
                regressed.append({"dimension": dimension, "goalId": None, "reason": score.get("reason") or "dimension-regressed"})
        return {
            "editorialDimensionScores": scores,
            "resolvedEditorialGoals": resolved,
            "unresolvedEditorialGoals": unresolved,
            "regressedEditorialDimensions": regressed,
        }


def _dimension_scores(comparison: dict[str, Any], current_id: str | None, revised_id: str | None) -> list[dict[str, Any]]:
    scores = _scores_from_attempts(comparison) or _scores_from_comparisons(comparison)
    normalized = [_normalize_score(item, current_id, revised_id) for item in scores]
    return [item for item in normalized if item.get("dimension") in EDITORIAL_DIMENSIONS]


def _scores_from_attempts(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    for attempt in reversed(_records(comparison.get("attempts"))):
        scores = attempt.get("editorialDimensionScores") or attempt.get("dimensionScores")
        if isinstance(scores, list):
            return _records(scores)
        if isinstance(scores, dict):
            return [{"dimension": key, **_record(value)} for key, value in scores.items()]
    return []


def _scores_from_comparisons(comparison: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in _records(comparison.get("comparisons")):
        scores = item.get("editorialDimensionScores") or item.get("dimensionScores")
        if isinstance(scores, list):
            result.extend(_records(scores))
    return result


def _normalize_score(score: dict[str, Any], current_id: str | None, revised_id: str | None) -> dict[str, Any]:
    winner = str(score.get("winnerCandidateId") or score.get("winner") or "")
    if winner == "revised" and revised_id:
        winner = revised_id
    if winner in {"current", "old", "base"} and current_id:
        winner = current_id
    return {
        "dimension": str(score.get("dimension") or score.get("name") or ""),
        "winnerCandidateId": winner or None,
        "reason": str(score.get("reason") or score.get("rationale") or ""),
        "currentScore": score.get("currentScore"),
        "revisedScore": score.get("revisedScore"),
    }


def _records(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
