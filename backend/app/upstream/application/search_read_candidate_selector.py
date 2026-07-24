"""Owner: upstream.application

Used by: SearchReadBudgetAllocator.
Does not own: budget size, decision trace, URL reading, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from backend.app.upstream.domain.search_triage_contracts import (
    SearchDuplicateGroup,
    SearchResultCandidate,
    SearchResultDimensionScores,
)


class SearchReadCandidateSelector:
    """Choose candidates with stable coverage and diversity tie-breaking."""

    def __init__(self, diversity_score_window: int) -> None:
        self._diversity_score_window = diversity_score_window

    def best(
        self,
        choices: list[SearchResultCandidate],
        scores: dict[str, SearchResultDimensionScores],
        groups: dict[str, SearchDuplicateGroup],
        selected: list[SearchResultCandidate],
    ) -> SearchResultCandidate:
        best_score = max(scores[item.id].total for item in choices)
        near = [
            item
            for item in choices
            if scores[item.id].total >= best_score - self._diversity_score_window
        ]
        used_domains = {item.domain for item in selected if item.domain}
        used_evidence = {
            evidence
            for item in selected
            for evidence in groups[item.id].evidence_types
        }
        return min(
            near,
            key=lambda item: (
                -int(bool(set(groups[item.id].evidence_types) - used_evidence)),
                -int(bool(item.domain and item.domain not in used_domains)),
                -scores[item.id].total,
                self.stable_key(item),
            ),
        )

    def best_requirement(
        self,
        choices: list[SearchResultCandidate],
        scores: dict[str, SearchResultDimensionScores],
        groups: dict[str, SearchDuplicateGroup],
        selected: list[SearchResultCandidate],
        uncovered_requirements: set[str],
    ) -> SearchResultCandidate:
        best_coverage = max(
            len(
                uncovered_requirements.intersection(
                    groups[item.id].supported_requirement_ids
                )
            )
            for item in choices
        )
        best_coverage_choices = [
            item
            for item in choices
            if len(
                uncovered_requirements.intersection(
                    groups[item.id].supported_requirement_ids
                )
            )
            == best_coverage
        ]
        return self.best(best_coverage_choices, scores, groups, selected)

    @staticmethod
    def supports(
        group: SearchDuplicateGroup,
        requirement_ids: list[str],
    ) -> bool:
        return bool(
            set(group.supported_requirement_ids).intersection(requirement_ids)
        )

    @staticmethod
    def stable_key(
        candidate: SearchResultCandidate,
    ) -> tuple[str, str, str, str]:
        return (
            candidate.canonical_url,
            candidate.title.casefold(),
            candidate.query_id,
            candidate.raw_result_id,
        )


__all__ = ("SearchReadCandidateSelector",)
