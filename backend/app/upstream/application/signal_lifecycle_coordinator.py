"""Owner: upstream.application

Used by: UpstreamRadarExternalRunService after retrieval and by retry endpoints.
Does not own: search, URL reading, provider transport, scoring semantics, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.radar_language_context import RadarLanguageContextFactory
from backend.app.upstream.application.signal_extraction_run_coordinator import SignalExtractionRunCoordinator
from backend.app.upstream.application.signal_utility_run_coordinator import SignalUtilityRunCoordinator


class RadarSignalLifecycleCoordinator:
    def __init__(
        self,
        *,
        extraction: SignalExtractionRunCoordinator,
        utility: SignalUtilityRunCoordinator,
        language_contexts: RadarLanguageContextFactory,
    ) -> None:
        self._extraction = extraction
        self._utility = utility
        self._language_contexts = language_contexts

    def process_materials(
        self,
        *,
        workspace: dict[str, Any],
        radar: dict[str, Any],
        run: dict[str, Any],
        materials: list[dict[str, Any]],
        language_context: Any,
        project_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        extraction = self._extraction.extract(
            workspace=workspace,
            radar=radar,
            run=run,
            materials=materials,
            language_context=language_context,
        )
        run["signalExtraction"] = extraction["signalExtractionReport"]
        run["operations"].append(extraction["operation"])
        scoring = self._utility.score(
            workspace=workspace,
            radar=radar,
            run=run,
            signals=extraction["sourceSignals"],
            project_context=project_context,
        )
        run["signalScoring"] = scoring["signalScoringReport"]
        run["operations"].append(scoring["operation"])
        run["budget"]["usedOperations"] = len(run["operations"])
        return {
            "sourceSignals": scoring["sourceSignals"],
            "signalExtractionReport": extraction["signalExtractionReport"],
            "signalScoringReport": scoring["signalScoringReport"],
        }

    def retry_extraction(
        self,
        *,
        workspace: dict[str, Any],
        run_id: str,
        force_retry: bool,
        project_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        run = self._find(workspace.get("radarRuns"), run_id)
        radar = self._find(workspace.get("radars"), str((run or {}).get("radarId") or ""))
        language_context = self._language_contexts.build(
            project_context=project_context,
            workspace=workspace,
            radar=radar or {},
        )
        extraction = self._extraction.retry(
            workspace=workspace,
            run_id=run_id,
            force_retry=force_retry,
            language_context=language_context,
        )
        scoring = self._utility.score(
            workspace=workspace,
            radar=radar or {},
            run=extraction["run"],
            signals=extraction["sourceSignals"],
            project_context=project_context,
            previous_report=(run or {}).get("signalScoring") if isinstance((run or {}).get("signalScoring"), dict) else None,
        )
        operations = [*list(extraction["run"].get("operations") or []), scoring["operation"]]
        updated_run = {
            **extraction["run"],
            "signalScoring": scoring["signalScoringReport"],
            "operations": operations,
            "budget": {**dict(extraction["run"].get("budget") or {}), "usedOperations": len(operations)},
        }
        return {
            "run": updated_run,
            "sourceSignals": scoring["sourceSignals"],
            "signalExtractionReport": extraction["signalExtractionReport"],
            "signalScoringReport": scoring["signalScoringReport"],
        }

    def retry_scoring(
        self,
        *,
        workspace: dict[str, Any],
        run_id: str,
        project_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return self._utility.retry(workspace=workspace, run_id=run_id, project_context=project_context)

    def _find(self, items: Any, item_id: str) -> dict[str, Any] | None:
        if not isinstance(items, list):
            return None
        return next((item for item in items if isinstance(item, dict) and item.get("id") == item_id), None)


__all__ = ("RadarSignalLifecycleCoordinator",)
