"""Owner: upstream.application

Used by: RadarRun triage to allocate a bounded, coverage-aware URL read plan.
Does not own: provider search, URL reading, score calculation, persistence, or benchmark grading.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from collections import Counter

from backend.app.upstream.application.search_result_readability import SearchResultReadabilityPolicy
from backend.app.upstream.domain.search_triage_contracts import (
    SearchDuplicateGroup,
    SearchReadDecision,
    SearchReadPlan,
    SearchResultCandidate,
    SearchResultDimensionScores,
)


class SearchReadBudgetAllocator:
    QUALITY_FLOOR = 45
    DIVERSITY_SCORE_WINDOW = 10

    def __init__(self, readability: SearchResultReadabilityPolicy | None = None) -> None:
        self._readability = readability or SearchResultReadabilityPolicy()

    def allocate(
        self,
        *,
        candidates: list[SearchResultCandidate],
        scores: dict[str, SearchResultDimensionScores],
        duplicate_groups: list[SearchDuplicateGroup],
        max_reads: int,
        required_families: list[str],
    ) -> SearchReadPlan:
        candidate_by_id = {item.id: item for item in candidates}
        group_by_candidate = {
            candidate_id: group
            for group in duplicate_groups
            for candidate_id in group.candidate_ids
        }
        representatives = [
            candidate_by_id[group.representative_candidate_id]
            for group in duplicate_groups
        ]
        eligible = [
            item
            for item in representatives
            if scores[item.id].total >= self.QUALITY_FLOOR and self._readability.can_read(item)
        ]
        selected: list[SearchResultCandidate] = []

        for family in self._unique(required_families):
            if len(selected) >= max(0, max_reads):
                break
            choices = [
                item
                for item in eligible
                if item not in selected and family in group_by_candidate[item.id].families
            ]
            if choices:
                selected.append(self._best_choice(choices, scores, group_by_candidate, selected))

        while len(selected) < max(0, max_reads):
            choices = [item for item in eligible if item not in selected]
            if not choices:
                break
            selected.append(self._best_choice(choices, scores, group_by_candidate, selected))

        selected_ids = {item.id for item in selected}
        decisions: list[SearchReadDecision] = []
        for candidate in sorted(candidates, key=self._stable_key):
            group = group_by_candidate.get(candidate.id)
            score = scores.get(candidate.id)
            total = score.total if score else 0
            if not candidate.valid:
                status, reason = "invalid", candidate.invalid_reason or "invalid-result"
            elif group and candidate.id != group.representative_candidate_id:
                status = "duplicate"
                reason = "duplicate-url" if "canonical-url" in group.match_reasons else "duplicate-content"
            elif not self._readability.can_read(candidate):
                status, reason = "rejected", "unsupported-read-format"
            elif candidate.id in selected_ids:
                status, reason = "selected", "coverage-aware-best-result"
            elif total < self.QUALITY_FLOOR:
                status, reason = "rejected", "below-quality-floor"
            else:
                status, reason = "deferredByBudget", "url-read-budget"
            decisions.append(
                SearchReadDecision(
                    raw_result_id=candidate.raw_result_id,
                    candidate_id=candidate.id,
                    duplicate_group_id=group.id if group else None,
                    status=status,
                    reason=reason,
                    score=total,
                    url=candidate.url,
                    families=group.families if group else ((candidate.family,) if candidate.family else ()),
                    evidence_types=group.evidence_types if group else ((candidate.evidence_type,) if candidate.evidence_type else ()),
                    domain=candidate.domain,
                    duplicate_raw_result_ids=group.raw_result_ids if group else (candidate.raw_result_id,),
                    query_ids=group.query_ids if group else ((candidate.query_id,) if candidate.query_id else ()),
                    intent_ids=group.intent_ids if group else ((candidate.intent_id,) if candidate.intent_id else ()),
                )
            )

        covered = self._unique(
            family
            for candidate in selected
            for family in group_by_candidate[candidate.id].families
        )
        gaps = self._coverage_gaps(
            required_families=self._unique(required_families),
            candidates=candidates,
            duplicate_groups=duplicate_groups,
            scores=scores,
            covered_families=covered,
        )
        return SearchReadPlan(
            max_reads=max(0, max_reads),
            quality_floor=self.QUALITY_FLOOR,
            required_families=tuple(self._unique(required_families)),
            selected_candidate_ids=tuple(item.id for item in selected),
            decisions=tuple(decisions),
            covered_families=tuple(covered),
            coverage_gaps=tuple(gaps),
        )

    def decision_counts(self, plan: SearchReadPlan) -> dict[str, int]:
        counts = Counter(item.status for item in plan.decisions)
        return {
            "selected": counts["selected"],
            "rejected": counts["rejected"],
            "duplicate": counts["duplicate"],
            "invalid": counts["invalid"],
            "deferredByBudget": counts["deferredByBudget"],
            "total": len(plan.decisions),
        }

    def _best_choice(
        self,
        choices: list[SearchResultCandidate],
        scores: dict[str, SearchResultDimensionScores],
        groups: dict[str, SearchDuplicateGroup],
        selected: list[SearchResultCandidate],
    ) -> SearchResultCandidate:
        best_score = max(scores[item.id].total for item in choices)
        near = [item for item in choices if scores[item.id].total >= best_score - self.DIVERSITY_SCORE_WINDOW]
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
                self._stable_key(item),
            ),
        )

    def _coverage_gaps(
        self,
        *,
        required_families: list[str],
        candidates: list[SearchResultCandidate],
        duplicate_groups: list[SearchDuplicateGroup],
        scores: dict[str, SearchResultDimensionScores],
        covered_families: list[str],
    ) -> list[dict[str, str]]:
        gaps: list[dict[str, str]] = []
        covered = set(covered_families)
        for family in required_families:
            if family in covered:
                continue
            matching = [group for group in duplicate_groups if family in group.families]
            if not matching:
                reason = "no-candidate"
            elif all(
                not self._readability.can_read(
                    next(item for item in candidates if item.id == group.representative_candidate_id)
                )
                for group in matching
            ):
                reason = "unsupported-read-format"
            elif all(scores[group.representative_candidate_id].total < self.QUALITY_FLOOR for group in matching):
                reason = "below-quality-floor"
            else:
                reason = "read-budget"
            gaps.append({"family": family, "reason": reason})
        return gaps

    def _stable_key(self, candidate: SearchResultCandidate) -> tuple[str, str, str, str]:
        return (
            candidate.canonical_url,
            candidate.title.casefold(),
            candidate.query_id,
            candidate.raw_result_id,
        )

    def _unique(self, values) -> list[str]:
        return list(dict.fromkeys(str(item) for item in values if item))


__all__ = ("SearchReadBudgetAllocator",)
