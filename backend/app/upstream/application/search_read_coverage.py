"""Owner: upstream.application

Used by: search read allocation to explain uncovered required query families.
Does not own: result scoring, duplicate selection, URL reading, or provider execution.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from backend.app.upstream.application.search_result_readability import SearchResultReadabilityPolicy
from backend.app.upstream.domain.search_triage_contracts import (
    SearchDuplicateGroup,
    SearchResultCandidate,
    SearchResultDimensionScores,
)


class SearchReadCoverageGapPolicy:
    def __init__(self, readability: SearchResultReadabilityPolicy | None = None) -> None:
        self._readability = readability or SearchResultReadabilityPolicy()

    def explain(
        self,
        *,
        required_families: list[str],
        candidates: list[SearchResultCandidate],
        duplicate_groups: list[SearchDuplicateGroup],
        scores: dict[str, SearchResultDimensionScores],
        covered_families: list[str],
        quality_floor: int,
    ) -> list[dict[str, str]]:
        gaps: list[dict[str, str]] = []
        covered = set(covered_families)
        candidate_by_id = {item.id: item for item in candidates}
        for family in required_families:
            if family in covered:
                continue
            matching = [group for group in duplicate_groups if family in group.families]
            representatives = [candidate_by_id[group.representative_candidate_id] for group in matching]
            if not matching:
                reason = "no-candidate"
            elif all(not item.source_language_allowed for item in representatives):
                reason = "source-language-not-allowed"
            elif all(not self._readability.can_read(item) for item in representatives):
                reason = "unsupported-read-format"
            elif all(scores[item.id].total < quality_floor for item in representatives):
                reason = "below-quality-floor"
            else:
                reason = "read-budget"
            gaps.append({"family": family, "reason": reason})
        return gaps


__all__ = ("SearchReadCoverageGapPolicy",)
