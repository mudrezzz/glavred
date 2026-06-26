from typing import Any

from backend.app.application.json_step_retry_policy import JsonStepAttempt
from backend.app.domain.draft_ranking_revision import PairwiseComparison, PairwiseRankingReport, RankingDecision


def report_from_payload(payload: dict[str, Any], attempts: list[dict[str, Any]], ai_run_ids: list[str]) -> PairwiseRankingReport:
    return PairwiseRankingReport(
        decision=RankingDecision(winner_candidate_id=str(payload.get("winnerCandidateId") or ""), reason=str(payload.get("reason") or "Selected by provider pairwise ranking."), source="openrouter"),
        comparisons=[
            PairwiseComparison(
                left_candidate_id=str(item.get("leftCandidateId") or ""),
                right_candidate_id=str(item.get("rightCandidateId") or ""),
                winner_candidate_id=str(item.get("winnerCandidateId") or ""),
                reason=str(item.get("reason") or ""),
                decisive_factors=[str(value) for value in item.get("decisiveFactors", []) if str(value).strip()] if isinstance(item.get("decisiveFactors"), list) else [],
            )
            for item in payload.get("comparisons", [])
            if isinstance(item, dict)
        ],
        attempts=attempts,
        ai_run_ids=ai_run_ids,
    )


def validate_pairwise_payload(payload: dict[str, Any], draft_artifact: dict[str, Any]) -> None:
    candidate_ids = {str(candidate.get("id")) for candidate in draft_artifact.get("candidates", []) if isinstance(candidate, dict)}
    winner = str(payload.get("winnerCandidateId") or "")
    if winner not in candidate_ids:
        raise ValueError("Pairwise ranking winnerCandidateId is not a known candidate")
    if not isinstance(payload.get("comparisons"), list):
        raise ValueError("Pairwise ranking comparisons is not a list")


def attempt_record(
    attempt: JsonStepAttempt,
    ai_run_id: str,
    status: str,
    model_selection: dict[str, Any],
    validation: Any | None = None,
    editorial_dimension_scores: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    record = {"label": attempt.label, "model": attempt.model, "status": status, "aiRunId": ai_run_id, "backup": attempt.backup, **model_selection}
    if validation:
        record["validation"] = validation
    if editorial_dimension_scores:
        record["editorialDimensionScores"] = editorial_dimension_scores
    return record


def dimension_scores(payload: dict[str, Any]) -> list[dict[str, Any]]:
    direct = payload.get("editorialDimensionScores")
    if isinstance(direct, list):
        return [item for item in direct if isinstance(item, dict)]
    scores: list[dict[str, Any]] = []
    for comparison in payload.get("comparisons", []):
        if isinstance(comparison, dict) and isinstance(comparison.get("editorialDimensionScores"), list):
            scores.extend(item for item in comparison["editorialDimensionScores"] if isinstance(item, dict))
    return scores
