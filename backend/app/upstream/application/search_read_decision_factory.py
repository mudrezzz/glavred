"""Owner: upstream.application

Used by: SearchReadBudgetAllocator.
Does not own: candidate selection, scoring, URL reading, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from backend.app.upstream.application.search_result_readability import SearchResultReadabilityPolicy
from backend.app.upstream.domain.search_triage_contracts import (
    SearchDuplicateGroup,
    SearchReadDecision,
    SearchResultCandidate,
    SearchResultDimensionScores,
)


class SearchReadDecisionFactory:
    """Convert a selected candidate set into one terminal decision per raw result."""

    def __init__(self, readability: SearchResultReadabilityPolicy) -> None:
        self._readability = readability

    def build(
        self,
        *,
        candidates: list[SearchResultCandidate],
        scores: dict[str, SearchResultDimensionScores],
        groups: dict[str, SearchDuplicateGroup],
        selected: list[SearchResultCandidate],
        selection_reasons: dict[str, str],
        quality_floor: int,
    ) -> tuple[SearchReadDecision, ...]:
        selected_ids = {item.id for item in selected}
        decisions: list[SearchReadDecision] = []
        for candidate in sorted(candidates, key=self._stable_key):
            group = groups.get(candidate.id)
            score = scores.get(candidate.id)
            total = score.total if score else 0
            status, reason = self._decision(
                candidate=candidate,
                group=group,
                selected_ids=selected_ids,
                selection_reasons=selection_reasons,
                total=total,
                quality_floor=quality_floor,
            )
            decisions.append(
                SearchReadDecision(
                    raw_result_id=candidate.raw_result_id,
                    candidate_id=candidate.id,
                    duplicate_group_id=group.id if group else None,
                    status=status,
                    reason=reason,
                    score=total,
                    url=candidate.url,
                    families=group.families if group else self._one(candidate.family),
                    evidence_types=(
                        group.evidence_types
                        if group
                        else self._one(candidate.evidence_type)
                    ),
                    domain=candidate.domain,
                    duplicate_raw_result_ids=(
                        group.raw_result_ids
                        if group
                        else (candidate.raw_result_id,)
                    ),
                    query_ids=group.query_ids if group else self._one(candidate.query_id),
                    intent_ids=(
                        group.intent_ids if group else self._one(candidate.intent_id)
                    ),
                    requirement_ids=(
                        group.requirement_ids if group else candidate.requirement_ids
                    ),
                    supported_requirement_ids=(
                        group.supported_requirement_ids
                        if group
                        else candidate.supported_requirement_ids
                    ),
                    source_language=candidate.source_language,
                    source_language_confidence=candidate.source_language_confidence,
                    source_language_mixed=candidate.source_language_mixed,
                    source_language_reason_codes=candidate.source_language_reason_codes,
                    source_language_eligibility_reason=(
                        candidate.source_language_eligibility_reason
                    ),
                )
            )
        return tuple(decisions)

    def _decision(
        self,
        *,
        candidate: SearchResultCandidate,
        group: SearchDuplicateGroup | None,
        selected_ids: set[str],
        selection_reasons: dict[str, str],
        total: int,
        quality_floor: int,
    ) -> tuple[str, str]:
        if not candidate.valid:
            return "invalid", candidate.invalid_reason or "invalid-result"
        if group and candidate.id != group.representative_candidate_id:
            reason = (
                "duplicate-url"
                if "canonical-url" in group.match_reasons
                else "duplicate-content"
            )
            return "duplicate", reason
        if not candidate.source_language_allowed:
            return (
                "rejected",
                candidate.source_language_eligibility_reason
                or "source-language-not-allowed",
            )
        if not self._readability.can_read(candidate):
            return "rejected", "unsupported-read-format"
        if candidate.id in selected_ids:
            return (
                "selected",
                selection_reasons.get(candidate.id, "coverage-aware-best-result"),
            )
        if total < quality_floor:
            return "rejected", "below-quality-floor"
        return "deferredByBudget", "url-read-budget"

    @staticmethod
    def _one(value: str | None) -> tuple[str, ...]:
        return (value,) if value else ()

    @staticmethod
    def _stable_key(candidate: SearchResultCandidate) -> tuple[str, str, str, str]:
        return (
            candidate.canonical_url,
            candidate.title.casefold(),
            candidate.query_id,
            candidate.raw_result_id,
        )


__all__ = ("SearchReadDecisionFactory",)
