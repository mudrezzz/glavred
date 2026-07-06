"""Owner: upstream.application

Used by: upstream radar external run service and legacy search-plan imports.
Does not own: provider transport, API routing, UI rendering, signal scoring, or candidate assembly.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.search_intent_planner import SearchIntentPlanner


class UpstreamSearchPlanBuilder:
    """Compatibility builder preserving the previous dict payload boundary."""

    def __init__(self, *, planner: SearchIntentPlanner | None = None) -> None:
        self._planner = planner or SearchIntentPlanner()

    def build(
        self,
        *,
        radar: dict[str, Any],
        handles: list[dict[str, Any]],
        budget: dict[str, int],
        workspace: dict[str, Any],
    ) -> dict[str, Any]:
        return self._planner.build(
            radar=radar,
            handles=handles,
            budget=budget,
            workspace=workspace,
        ).to_payload()


def build_search_plan(
    *,
    radar: dict[str, Any],
    handles: list[dict[str, Any]],
    budget: dict[str, int],
    workspace: dict[str, Any],
) -> dict[str, Any]:
    return UpstreamSearchPlanBuilder().build(
        radar=radar,
        handles=handles,
        budget=budget,
        workspace=workspace,
    )


__all__ = ("SearchIntentPlanner", "UpstreamSearchPlanBuilder", "build_search_plan")
