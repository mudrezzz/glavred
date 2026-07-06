"""Owner: upstream.application

Used by: SearchIntentPlanner to serialize campaign rationale for RadarRun traces.
Does not own: provider transport, API routing, UI rendering, or signal scoring.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from backend.app.upstream.domain.search_campaign import (
    SearchCampaignTrace,
    SearchIntent,
    SearchQuery,
    SkippedSearchIntent,
)


class SearchCampaignTraceBuilder:
    def build(
        self,
        *,
        radar: dict[str, Any],
        workspace: dict[str, Any],
        handles: list[dict[str, Any]],
        language: str,
        research_depth: str,
        budget: dict[str, int],
        source_eligibility: list[dict[str, Any]],
        intents: list[SearchIntent],
        queries: list[SearchQuery],
        skipped: list[SkippedSearchIntent],
    ) -> SearchCampaignTrace:
        return SearchCampaignTrace(
            planner_version="deterministic-search-campaign-v2",
            input_summary=self._input_summary(
                radar=radar,
                workspace=workspace,
                handles=handles,
                language=language,
                research_depth=research_depth,
            ),
            intent_coverage=self._intent_coverage(intents=intents, queries=queries, skipped=skipped),
            budget_limits={
                "maxExternalQueries": int(budget.get("maxExternalQueries", 0)),
                "maxUrlReads": int(budget.get("maxUrlReads", 0)),
                "maxFoundMaterials": int(budget.get("maxFoundMaterials", 0)),
            },
            source_eligibility=source_eligibility,
            skipped_reasons=self._unique([item.reason for item in skipped]),
            ownership_boundary="Search campaign may use topics and fabulas as context, but raw FoundMaterial does not own topic or fabula decisions.",
        )

    def source_strategy(self, source_eligibility: list[dict[str, Any]]) -> dict[str, Any]:
        searchable = [item["sourceHandleId"] for item in source_eligibility if item["strategy"] == "providerSearch"]
        readable = [item["sourceHandleId"] for item in source_eligibility if item["strategy"] == "directRead"]
        skipped = [item for item in source_eligibility if item["strategy"] == "skipped"]
        return {
            "searchableSourceHandleIds": searchable,
            "directReadSourceHandleIds": readable,
            "skippedSources": skipped,
            "strategy": "search-active-handles-read-readable-handles",
        }

    def _input_summary(
        self,
        *,
        radar: dict[str, Any],
        workspace: dict[str, Any],
        handles: list[dict[str, Any]],
        language: str,
        research_depth: str,
    ) -> dict[str, Any]:
        profile = workspace.get("projectProfile") if isinstance(workspace.get("projectProfile"), dict) else {}
        return {
            "radarId": radar.get("id"),
            "radarTitle": radar.get("title"),
            "language": language,
            "researchDepth": research_depth,
            "sourceHandleCount": len(handles),
            "topicCount": len(workspace.get("topics", [])) if isinstance(workspace.get("topics"), list) else 0,
            "fabulaCount": len(workspace.get("fabulas", [])) if isinstance(workspace.get("fabulas"), list) else 0,
            "publisherRuleCount": len(workspace.get("publisherRules", [])) if isinstance(workspace.get("publisherRules"), list) else 0,
            "benchmarkRole": profile.get("benchmarkRole") or workspace.get("benchmarkRole"),
        }

    def _intent_coverage(
        self,
        *,
        intents: list[SearchIntent],
        queries: list[SearchQuery],
        skipped: list[SkippedSearchIntent],
    ) -> list[dict[str, Any]]:
        queries_by_intent = Counter(item.intent_id for item in queries)
        skipped_by_intent = Counter(item.intent_id for item in skipped if item.intent_id)
        return [
            {
                "intentId": intent.id,
                "family": intent.family,
                "evidenceType": intent.evidence_type,
                "sourceHandleId": intent.source_handle_id,
                "queryCount": queries_by_intent[intent.id],
                "skippedCount": skipped_by_intent[intent.id],
                "status": "queryPlanned" if queries_by_intent[intent.id] else "skipped",
            }
            for intent in intents
        ]

    def _unique(self, items: list[str]) -> list[str]:
        return list(dict.fromkeys(item for item in items if item))


__all__ = ("SearchCampaignTraceBuilder",)
