"""Owner: upstream.application

Used by: SearchIntentPlanner to allocate bounded query families against radar requirements.
Does not own: requirement projection, query wording, provider execution, or result triage.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from backend.app.upstream.domain.search_requirements import RadarSearchRequirementProfile, SearchRequirement


class SearchRequirementQueryAllocator:
    _TIE_ORDER = {
        "broadDiscovery": 0,
        "caseExample": 1,
        "benchmarkPaper": 2,
        "limitationCritique": 3,
        "ossTooling": 4,
        "freshness": 5,
    }
    _EVIDENCE_DIVERSITY_BONUS = {"benchmarkPaper": 70, "limitationCritique": 30}

    def order_families(
        self,
        *,
        available_families: list[str],
        profile: RadarSearchRequirementProfile,
    ) -> list[str]:
        remaining = list(dict.fromkeys(available_families))
        covered: set[str] = set()
        ordered: list[str] = []
        while remaining:
            selected = min(
                remaining,
                key=lambda family: (
                    -self._marginal_score(family, profile.requirements, covered),
                    self._TIE_ORDER.get(family, 99),
                    family,
                ),
            )
            ordered.append(selected)
            covered.update(item.id for item in profile.requirements if selected in item.query_families)
            remaining.remove(selected)
        return ordered

    def requirements_for_family(
        self,
        family: str,
        profile: RadarSearchRequirementProfile,
    ) -> tuple[SearchRequirement, ...]:
        return tuple(item for item in profile.requirements if family in item.query_families)

    def uncovered_required_ids(
        self,
        *,
        profile: RadarSearchRequirementProfile,
        executed_family_requirements: list[str],
    ) -> tuple[str, ...]:
        executed = set(executed_family_requirements)
        return tuple(item.id for item in profile.requirements if item.role == "required" and item.id not in executed)

    def _marginal_score(
        self,
        family: str,
        requirements: tuple[SearchRequirement, ...],
        covered: set[str],
    ) -> int:
        score = sum(item.priority for item in requirements if item.id not in covered and family in item.query_families)
        if any(family in item.query_families for item in requirements):
            score += self._EVIDENCE_DIVERSITY_BONUS.get(family, 0)
        return score


__all__ = ("SearchRequirementQueryAllocator",)
