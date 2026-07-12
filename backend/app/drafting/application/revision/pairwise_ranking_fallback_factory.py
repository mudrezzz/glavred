"""Owner: drafting.application.revision

Used by: pairwise ranking orchestration when provider ranking is unavailable or invalid.
Does not own: provider attempts, candidate scoring, revision acceptance, or transport.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from typing import Any

from backend.app.domain.draft_ranking_revision import PairwiseRankingReport, RankingDecision
from backend.app.drafting.application.revision.deterministic_pairwise_ranking import DeterministicPairwiseRanker
from backend.app.drafting.application.revision.pairwise_comparison_identity import (
    EDITORIAL_DIMENSIONS,
    PairwiseComparisonIdentityPolicy,
)


class PairwiseRankingFallbackFactory:
    """Builds a deterministic report with the same identity trace as provider reports."""

    def __init__(self, ranker: DeterministicPairwiseRanker) -> None:
        self._ranker = ranker

    def build(
        self,
        *,
        draft_artifact: dict[str, Any],
        validation_report: dict[str, Any],
        attempts: list[dict[str, Any]],
        warning: str,
    ) -> PairwiseRankingReport:
        fallback = self._ranker.rank(draft_artifact=draft_artifact, validation_report=validation_report)
        decision = RankingDecision(
            winner_candidate_id=fallback.decision.winner_candidate_id,
            reason=fallback.decision.reason,
            source="deterministicFallback",
            fallback_used=True,
            warnings=[*fallback.decision.warnings, warning],
        )
        candidate_ids = [str(item.get("id")) for item in draft_artifact.get("candidates", []) if isinstance(item, dict) and item.get("id")]
        dimension_scores = [
            {"dimension": dimension, "winnerCandidateId": decision.winner_candidate_id, "reason": "Deterministic validation-aware fallback."}
            for dimension in EDITORIAL_DIMENSIONS
            if decision.winner_candidate_id
        ]
        identity = PairwiseComparisonIdentityPolicy().evaluate(
            {
                "winnerCandidateId": decision.winner_candidate_id,
                "comparisons": [item.to_payload() for item in fallback.comparisons],
                "editorialDimensionScores": dimension_scores,
            },
            candidate_ids,
        )
        return PairwiseRankingReport(
            decision=decision,
            comparisons=fallback.comparisons,
            attempts=[*attempts, {"label": "deterministic-fallback", "model": "deterministic", "status": "fallback", "backup": False, "validation": warning}],
            ai_run_ids=[str(item["aiRunId"]) for item in attempts if item.get("aiRunId")],
            comparison_identity=identity.to_payload(),
            editorial_dimension_scores=dimension_scores,
        )


__all__ = ("PairwiseRankingFallbackFactory",)
