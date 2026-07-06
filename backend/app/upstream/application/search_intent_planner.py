"""Owner: upstream.application

Used by: upstream RadarRun external execution before provider search.
Does not own: provider transport, API routing, UI rendering, signal scoring, or candidate assembly.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.search_campaign_trace import SearchCampaignTraceBuilder
from backend.app.upstream.application.search_planner_inputs import SearchPlannerInputPolicy
from backend.app.upstream.application.search_query_family_policy import SearchQueryFamilyPolicy
from backend.app.upstream.domain.search_campaign import (
    SearchIntent,
    SearchPlan,
    SearchQuery,
    SkippedSearchIntent,
)


class SearchIntentPlanner:
    def __init__(
        self,
        *,
        family_policy: SearchQueryFamilyPolicy | None = None,
        trace_builder: SearchCampaignTraceBuilder | None = None,
        input_policy: SearchPlannerInputPolicy | None = None,
    ) -> None:
        self._family_policy = family_policy or SearchQueryFamilyPolicy()
        self._trace_builder = trace_builder or SearchCampaignTraceBuilder()
        self._input_policy = input_policy or SearchPlannerInputPolicy()

    def build(
        self,
        *,
        radar: dict[str, Any],
        handles: list[dict[str, Any]],
        budget: dict[str, int],
        workspace: dict[str, Any],
    ) -> SearchPlan:
        language = self._input_policy.workspace_language(workspace)
        research_depth = self._input_policy.research_depth(radar=radar, workspace=workspace)
        families = self._family_policy.families(
            language=language,
            include_freshness=self._input_policy.needs_freshness(radar=radar, workspace=workspace, research_depth=research_depth),
        )
        source_eligibility = [self._input_policy.source_eligibility(handle) for handle in handles]
        intents: list[SearchIntent] = []
        queries: list[SearchQuery] = []
        skipped: list[SkippedSearchIntent] = []
        max_queries = max(0, int(budget.get("maxExternalQueries", 0)))

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

            base_query = self._input_policy.base_query(radar=radar, handle=handle, workspace=workspace)
            for family in families:
                intent = SearchIntent(
                    id=f"intent-{len(intents) + 1}",
                    intent_type=family.intent_type,
                    family=family.family,
                    evidence_type=family.evidence_type,
                    label=family.label,
                    source_handle_id=str(handle.get("id") or ""),
                    source_handle_title=str(handle.get("title") or handle.get("locator") or handle.get("id") or ""),
                    rationale=self._intent_rationale(radar=radar, family_label=family.label, language=language),
                    priority=family.priority,
                    query_terms=self._input_policy.query_terms(base_query, family.suffix),
                )
                intents.append(intent)
                if len(queries) >= max_queries:
                    skipped.append(
                        SkippedSearchIntent(
                            id=f"skip-intent-{len(skipped) + 1}",
                            source_handle_id=intent.source_handle_id,
                            intent_id=intent.id,
                            intent_type=intent.intent_type,
                            family=intent.family,
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
                        query=self._input_policy.clean_query(f"{base_query} {family.suffix}"),
                        rationale=intent.rationale,
                    )
                )

        if not intents and not skipped:
            skipped.append(
                SkippedSearchIntent(
                    id="skip-no-searchable-source",
                    reason="no-searchable-source",
                    rationale="No active searchable source handle was attached to the radar.",
                )
            )

        source_strategy = self._trace_builder.source_strategy(source_eligibility)
        trace = self._trace_builder.build(
            radar=radar,
            workspace=workspace,
            handles=handles,
            language=language,
            research_depth=research_depth,
            budget=budget,
            source_eligibility=source_eligibility,
            intents=intents,
            queries=queries,
            skipped=skipped,
        )
        return SearchPlan(
            strategy="deterministic-search-campaign-v2",
            language=language,
            intents=intents,
            queries=queries,
            skipped_intents=skipped,
            source_strategy=source_strategy,
            trace=trace,
        )

    def _intent_rationale(self, *, radar: dict[str, Any], family_label: str, language: str) -> str:
        title = radar.get("title") or radar.get("id") or "radar"
        if language == "ru":
            return f"Ищем {family_label.lower()} для радара \"{title}\"."
        return f"Find {family_label.lower()} for radar \"{title}\"."


__all__ = ("SearchIntentPlanner",)
