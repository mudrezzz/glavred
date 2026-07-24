"""Owner: upstream.application

Used by: RadarRun triage to allocate a bounded, coverage-aware URL read plan.
Does not own: provider search, URL reading, score calculation, persistence, or benchmark grading.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from collections import Counter

from backend.app.upstream.application.search_read_candidate_selector import SearchReadCandidateSelector
from backend.app.upstream.application.search_read_coverage import SearchReadCoverageGapPolicy
from backend.app.upstream.application.search_read_decision_factory import SearchReadDecisionFactory
from backend.app.upstream.application.search_result_readability import SearchResultReadabilityPolicy
from backend.app.upstream.domain.search_triage_contracts import (
    SearchDuplicateGroup,
    SearchReadPlan,
    SearchResultCandidate,
    SearchResultDimensionScores,
)


class SearchReadBudgetAllocator:
    QUALITY_FLOOR = 45
    DIVERSITY_SCORE_WINDOW = 10

    def __init__(
        self,
        readability: SearchResultReadabilityPolicy | None = None,
        coverage_gaps: SearchReadCoverageGapPolicy | None = None,
    ) -> None:
        self._readability = readability or SearchResultReadabilityPolicy()
        self._coverage_gaps = coverage_gaps or SearchReadCoverageGapPolicy(self._readability)
        self._decision_factory = SearchReadDecisionFactory(self._readability)
        self._selector = SearchReadCandidateSelector(self.DIVERSITY_SCORE_WINDOW)

    def allocate(
        self,
        *,
        candidates: list[SearchResultCandidate],
        scores: dict[str, SearchResultDimensionScores],
        duplicate_groups: list[SearchDuplicateGroup],
        max_reads: int,
        required_families: list[str],
        required_requirement_ids: list[str] | None = None,
        corroboration_requirement_ids: list[str] | None = None,
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
            if item.source_language_allowed
            and scores[item.id].total >= self.QUALITY_FLOOR
            and self._readability.can_read(item)
        ]
        selected: list[SearchResultCandidate] = []
        selection_reasons: dict[str, str] = {}

        uncovered_requirements = set(self._unique(required_requirement_ids or []))
        while uncovered_requirements and len(selected) < max(0, max_reads):
            choices = [
                item
                for item in eligible
                if item not in selected
                and uncovered_requirements.intersection(
                    group_by_candidate[item.id].supported_requirement_ids
                )
            ]
            if not choices:
                break
            choice = self._selector.best_requirement(
                choices,
                scores,
                group_by_candidate,
                selected,
                uncovered_requirements,
            )
            selected.append(choice)
            selection_reasons[choice.id] = "required-evidence-priority"
            uncovered_requirements.difference_update(
                group_by_candidate[choice.id].supported_requirement_ids
            )

        if len(selected) < max(0, max_reads):
            corroboration_choices = [
                item
                for item in eligible
                if item not in selected
                and self._selector.supports(
                    group_by_candidate[item.id],
                    corroboration_requirement_ids or [],
                )
            ]
            if corroboration_choices:
                choice = self._selector.best(
                    corroboration_choices,
                    scores,
                    group_by_candidate,
                    selected,
                )
                selected.append(choice)
                selection_reasons[choice.id] = "independent-evidence-priority"

        for family in self._unique(required_families):
            if len(selected) >= max(0, max_reads):
                break
            if any(family in group_by_candidate[item.id].families for item in selected):
                continue
            choices = [
                item
                for item in eligible
                if item not in selected and family in group_by_candidate[item.id].families
            ]
            if choices:
                choice = self._selector.best(choices, scores, group_by_candidate, selected)
                selected.append(choice)
                selection_reasons[choice.id] = "required-family-priority"

        while len(selected) < max(0, max_reads):
            choices = [item for item in eligible if item not in selected]
            if not choices:
                break
            choice = self._selector.best(choices, scores, group_by_candidate, selected)
            selected.append(choice)
            selection_reasons[choice.id] = "coverage-aware-best-result"

        decisions = self._decision_factory.build(
            candidates=candidates,
            scores=scores,
            groups=group_by_candidate,
            selected=selected,
            selection_reasons=selection_reasons,
            quality_floor=self.QUALITY_FLOOR,
        )

        covered = self._unique(
            family
            for candidate in selected
            for family in group_by_candidate[candidate.id].families
        )
        gaps = self._coverage_gaps.explain(
            required_families=self._unique(required_families),
            candidates=candidates,
            duplicate_groups=duplicate_groups,
            scores=scores,
            covered_families=covered,
            quality_floor=self.QUALITY_FLOOR,
        )
        covered_requirements = self._unique(
            requirement_id
            for candidate in selected
            for requirement_id in group_by_candidate[candidate.id].supported_requirement_ids
        )
        gaps.extend(
            {
                "requirementId": requirement_id,
                "reason": "url-read-budget-or-no-eligible-result",
            }
            for requirement_id in self._unique(required_requirement_ids or [])
            if requirement_id not in covered_requirements
        )
        return SearchReadPlan(
            max_reads=max(0, max_reads),
            quality_floor=self.QUALITY_FLOOR,
            required_families=tuple(self._unique(required_families)),
            selected_candidate_ids=tuple(item.id for item in selected),
            decisions=tuple(decisions),
            covered_families=tuple(covered),
            coverage_gaps=tuple(gaps),
            required_requirement_ids=tuple(self._unique(required_requirement_ids or [])),
            covered_requirement_ids=tuple(covered_requirements),
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

    def _unique(self, values) -> list[str]:
        return list(dict.fromkeys(str(item) for item in values if item))


__all__ = ("SearchReadBudgetAllocator",)
