"""Owner: upstream.application

Used by: upstream RadarRun external execution before provider search.
Does not own: provider transport, API routing, UI rendering, signal scoring, or candidate assembly.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.search_campaign_trace import SearchCampaignTraceBuilder
from backend.app.upstream.application.radar_language_context import RadarLanguageContextFactory
from backend.app.upstream.application.search_planner_inputs import SearchPlannerInputPolicy
from backend.app.upstream.application.search_query_family_policy import SearchQueryFamilyPolicy
from backend.app.upstream.application.search_requirement_allocator import SearchRequirementQueryAllocator
from backend.app.upstream.application.search_requirement_profile import RadarSearchRequirementProfileFactory
from backend.app.upstream.domain.search_campaign import (
    SearchIntent,
    SearchPlan,
    SearchQuery,
    SkippedSearchIntent,
)
from backend.app.upstream.domain.radar_language import RadarLanguageContext


class SearchIntentPlanner:
    def __init__(
        self,
        *,
        family_policy: SearchQueryFamilyPolicy | None = None,
        trace_builder: SearchCampaignTraceBuilder | None = None,
        input_policy: SearchPlannerInputPolicy | None = None,
        language_factory: RadarLanguageContextFactory | None = None,
        requirement_factory: RadarSearchRequirementProfileFactory | None = None,
        requirement_allocator: SearchRequirementQueryAllocator | None = None,
    ) -> None:
        self._family_policy = family_policy or SearchQueryFamilyPolicy()
        self._trace_builder = trace_builder or SearchCampaignTraceBuilder()
        self._input_policy = input_policy or SearchPlannerInputPolicy()
        self._language_factory = language_factory or RadarLanguageContextFactory()
        self._requirement_factory = requirement_factory or RadarSearchRequirementProfileFactory()
        self._requirement_allocator = requirement_allocator or SearchRequirementQueryAllocator()

    def build(
        self,
        *,
        radar: dict[str, Any],
        handles: list[dict[str, Any]],
        budget: dict[str, int],
        workspace: dict[str, Any],
        language_context: RadarLanguageContext | None = None,
    ) -> SearchPlan:
        language_context = language_context or self._language_factory.build(
            project_context=None,
            workspace=workspace,
            radar=radar,
        )
        language = language_context.editorial_language
        research_depth = self._input_policy.research_depth(radar=radar, workspace=workspace)
        include_freshness = self._input_policy.needs_freshness(
            radar=radar,
            workspace=workspace,
            research_depth=research_depth,
        )
        profile = self._requirement_factory.build(radar)
        available_families = self._family_policy.families(
            language=language,
            include_freshness=include_freshness,
        )
        family_by_id = {item.family: item for item in available_families}
        ordered_family_ids = self._requirement_allocator.order_families(
            available_families=list(family_by_id),
            profile=profile,
        )
        source_eligibility = [self._input_policy.source_eligibility(handle) for handle in handles]
        intents: list[SearchIntent] = []
        queries: list[SearchQuery] = []
        skipped: list[SkippedSearchIntent] = []
        max_queries = max(0, int(budget.get("maxExternalQueries", 0)))
        normalized_query_texts: set[str] = set()

        for eligibility, handle in zip(source_eligibility, handles, strict=False):
            if eligibility["strategy"] == "skipped":
                skipped.append(
                    SkippedSearchIntent(
                        id=f"skip-source-{len(skipped) + 1}",
                        source_handle_id=str(handle.get("id") or ""),
                        reason=str(eligibility["reason"]),
                        rationale=f"Source handle {handle.get('title') or handle.get('id')} is not eligible for provider search.",
                    )
                )
                continue
            if eligibility["strategy"] == "directRead":
                skipped.append(
                    SkippedSearchIntent(
                        id=f"skip-source-{len(skipped) + 1}",
                        source_handle_id=str(handle.get("id") or ""),
                        reason="source-read-direct-only",
                        rationale="Readable URL sources are recorded in campaign trace and read directly outside provider query planning.",
                    )
                )
                continue

            for family_index, family_id in enumerate(ordered_family_ids):
                family = family_by_id[family_id]
                requirements = self._requirement_allocator.requirements_for_family(family.family, profile)
                requirement_ids = tuple(item.id for item in requirements)
                requirement_terms = list(dict.fromkeys(term for item in requirements for term in item.terms))[:16]
                source_hints = tuple(dict.fromkeys(hint for item in requirements for hint in item.source_hints))[:8]
                base_query = self._input_policy.base_query(
                    radar=radar,
                    handle=handle,
                    requirement_terms=requirement_terms,
                )
                query_language = language_context.query_language_for(family.family)
                query_family = self._family_policy.for_family(
                    family.family,
                    language=query_language,
                    include_freshness=include_freshness,
                )
                query_text = self._input_policy.query_for_language(
                    base_query=base_query,
                    suffix=query_family.suffix,
                    language=query_language,
                )
                intent = SearchIntent(
                    id=f"intent-{len(intents) + 1}",
                    intent_type=family.intent_type,
                    family=family.family,
                    evidence_type=family.evidence_type,
                    label=family.label,
                    source_handle_id=str(handle.get("id") or ""),
                    source_handle_title=str(handle.get("title") or handle.get("locator") or handle.get("id") or ""),
                    rationale=self._intent_rationale(radar=radar, family_label=family.label, language=language),
                    priority=family_index + 1,
                    query_terms=query_text.split()[:16],
                    query_language=query_language,
                    requirement_ids=requirement_ids,
                    evidence_target=family.evidence_type,
                    source_hints=source_hints,
                )
                intents.append(intent)
                normalized_query = " ".join(query_text.casefold().split())
                if normalized_query in normalized_query_texts:
                    skipped.append(
                        SkippedSearchIntent(
                            id=f"skip-intent-{len(skipped) + 1}",
                            source_handle_id=intent.source_handle_id,
                            intent_id=intent.id,
                            intent_type=intent.intent_type,
                            family=intent.family,
                            query_language=query_language,
                            requirement_ids=requirement_ids,
                            reason="duplicate-query-text",
                            rationale="Normalized query text duplicates an earlier planned query.",
                        )
                    )
                    continue
                if len(queries) >= max_queries:
                    skipped.append(
                        SkippedSearchIntent(
                            id=f"skip-intent-{len(skipped) + 1}",
                            source_handle_id=intent.source_handle_id,
                            intent_id=intent.id,
                            intent_type=intent.intent_type,
                            family=intent.family,
                            query_language=query_language,
                            requirement_ids=requirement_ids,
                            reason="budget-max-external-queries",
                            rationale=f"External query budget {max_queries} was exhausted before this intent could run.",
                        )
                    )
                    continue
                queries.append(
                    SearchQuery(
                        id=f"query-{len(queries) + 1}",
                        intent_id=intent.id,
                        source_handle_id=intent.source_handle_id,
                        intent=intent.intent_type,
                        family=intent.family,
                        evidence_type=intent.evidence_type,
                        priority=intent.priority,
                        label=intent.label,
                        query=query_text,
                        rationale=intent.rationale,
                        query_language=query_language,
                        requirement_ids=requirement_ids,
                        evidence_target=family.evidence_type,
                        source_hints=source_hints,
                    )
                )
                normalized_query_texts.add(normalized_query)

        if not intents and not skipped:
            skipped.append(
                SkippedSearchIntent(
                    id="skip-no-searchable-source",
                    reason="no-searchable-source",
                    rationale="No active searchable source handle was attached to the radar.",
                )
            )

        executed_languages = list(dict.fromkeys(item.query_language for item in queries))
        language_coverage_gaps = [
            {"language": item, "reason": "budget-max-external-queries"}
            for item in language_context.query_languages
            if item not in executed_languages
        ]
        source_strategy = self._trace_builder.source_strategy(source_eligibility)
        executed_requirement_ids = [
            requirement_id
            for query in queries
            for requirement_id in query.requirement_ids
        ]
        uncovered_required = [
            {
                "requirementId": requirement_id,
                "reason": "budget-max-external-queries" if max_queries > 0 else "external-query-budget-zero",
            }
            for requirement_id in self._requirement_allocator.uncovered_required_ids(
                profile=profile,
                executed_family_requirements=executed_requirement_ids,
            )
        ]
        trace = self._trace_builder.build(
            radar=radar,
            workspace=workspace,
            handles=handles,
            language=language,
            language_context=language_context,
            language_coverage_gaps=language_coverage_gaps,
            research_depth=research_depth,
            budget=budget,
            source_eligibility=source_eligibility,
            intents=intents,
            queries=queries,
            skipped=skipped,
        )
        return SearchPlan(
            strategy="deterministic-search-campaign-v3",
            language=language,
            intents=intents,
            queries=queries,
            skipped_intents=skipped,
            source_strategy=source_strategy,
            trace=trace,
            language_context=language_context.to_payload(),
            language_coverage_gaps=language_coverage_gaps,
            requirement_profile=profile.to_payload(),
            uncovered_required_search_requirements=uncovered_required,
        )

    def _intent_rationale(self, *, radar: dict[str, Any], family_label: str, language: str) -> str:
        title = radar.get("title") or radar.get("id") or "radar"
        if language == "ru":
            return f"Ищем {family_label.lower()} для радара \"{title}\"."
        return f"Find {family_label.lower()} for radar \"{title}\"."


__all__ = ("SearchIntentPlanner",)
