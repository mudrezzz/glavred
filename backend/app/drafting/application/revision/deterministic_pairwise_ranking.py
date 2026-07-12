"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from itertools import combinations
from typing import Any

from backend.app.domain.draft_ranking_revision import PairwiseComparison, PairwiseRankingReport, RankingDecision


class DeterministicPairwiseRanker:
    def rank(self, *, draft_artifact: dict[str, Any], validation_report: dict[str, Any]) -> PairwiseRankingReport:
        candidates = [_dict(item) for item in _list(draft_artifact.get("candidates"))]
        scorecard = {str(row.get("candidateId")): _dict(row) for row in _list(_dict(draft_artifact.get("selection")).get("scorecard"))}
        metrics = {
            str(candidate.get("id")): _candidate_metric(candidate, scorecard, validation_report)
            for candidate in candidates
            if str(candidate.get("id") or "")
        }
        eligible = [candidate_id for candidate_id, metric in metrics.items() if metric["eligible"]]
        if not eligible:
            return PairwiseRankingReport(
                decision=RankingDecision(
                    winner_candidate_id=None,
                    reason="No publishable candidate available after validation-aware ranking.",
                    source="deterministicFallback",
                    fallback_used=True,
                    warnings=["no-eligible-candidates"],
                )
            )
        winner = min(eligible, key=lambda candidate_id: _sort_key(metrics[candidate_id]))
        return PairwiseRankingReport(
            decision=RankingDecision(
                winner_candidate_id=winner,
                reason="Selected by deterministic validation-aware fallback: fewer critical/warning findings, then old scorecard.",
                source="deterministicFallback",
                fallback_used=True,
            ),
            comparisons=_comparisons(list(metrics), metrics),
        )


def _candidate_metric(candidate: dict[str, Any], scorecard: dict[str, dict[str, Any]], validation_report: dict[str, Any]) -> dict[str, Any]:
    candidate_id = str(candidate.get("id") or "")
    row = scorecard.get(candidate_id, {})
    deterministic = _report_for(validation_report, candidate_id)
    llm = _report_for(_dict(validation_report.get("llmValidationReport")), candidate_id)
    return {
        "eligible": row.get("selectionStatus") != "excluded" and row.get("publishable") is not False,
        "critical": _int(deterministic.get("criticalCount")) + _int(llm.get("criticalCount")),
        "warning": _int(deterministic.get("warningCount")) + _int(llm.get("warningCount")),
        "oldTotal": _int(row.get("total")),
        "candidateId": candidate_id,
    }


def _comparisons(candidate_ids: list[str], metrics: dict[str, dict[str, Any]]) -> list[PairwiseComparison]:
    rows: list[PairwiseComparison] = []
    for left, right in combinations(candidate_ids, 2):
        winner = min((left, right), key=lambda candidate_id: _comparison_sort_key(metrics[candidate_id]))
        loser = right if winner == left else left
        rows.append(PairwiseComparison(
            left_candidate_id=left,
            right_candidate_id=right,
            winner_candidate_id=winner,
            reason=f"{winner} has better validation/ranking metric than {loser}.",
            decisive_factors=[
                f"critical {metrics[winner]['critical']} vs {metrics[loser]['critical']}",
                f"warning {metrics[winner]['warning']} vs {metrics[loser]['warning']}",
                f"old score {metrics[winner]['oldTotal']} vs {metrics[loser]['oldTotal']}",
            ],
        ))
    return rows


def _sort_key(metric: dict[str, Any]) -> tuple[int, int, int, str]:
    return (_int(metric.get("critical")), _int(metric.get("warning")), -_int(metric.get("oldTotal")), str(metric.get("candidateId") or ""))


def _comparison_sort_key(metric: dict[str, Any]) -> tuple[int, int, int, int, str]:
    return (0 if metric.get("eligible") else 1, *_sort_key(metric))


def _report_for(report: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    for item in _list(report.get("candidateReports")):
        row = _dict(item)
        if row.get("candidateId") == candidate_id:
            return row
    return {}


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _int(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) else 0
