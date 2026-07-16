"""Owner: upstream.application

Used by: API radar-run route and future upstream campaign slices.
Does not own: API routing, SQLite persistence, provider transport, or DraftRun.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.application.public_evidence_ports import PublicUrlReader
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_web_search_adapter import OpenRouterWebSearchAdapter
from backend.app.settings import BackendSettings
from backend.app.upstream.application.external_operation_coordinator import ExternalRadarOperationCoordinator
from backend.app.upstream.application.external_read_operations import RadarUrlReadOperationRunner
from backend.app.upstream.application.external_run_budget import UpstreamRadarRunBudgetPolicy
from backend.app.upstream.application.external_run_payloads import UpstreamRadarPayloadFactory
from backend.app.upstream.application.external_run_result_policy import ExternalRunResultPolicy
from backend.app.upstream.application.external_search_operations import OpenWebQueryOperationRunner
from backend.app.upstream.application.radar_benchmark_reporter import RadarRunBenchmarkReporter
from backend.app.upstream.application.search_planner import build_search_plan
from backend.app.upstream.application.search_triage_service import SearchResultTriageService
from backend.app.upstream.application.signal_extraction_run_coordinator import SignalExtractionRunCoordinator
from backend.app.upstream.application.signal_extraction_service import SignalExtractionService


class UpstreamRadarExternalRunService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        web_search_adapter: OpenRouterWebSearchAdapter,
        url_reader: PublicUrlReader,
        openrouter_validator: OpenRouterConfigValidator,
        signal_extraction_service: SignalExtractionService | None = None,
    ) -> None:
        self._settings = settings
        self._result_policy = ExternalRunResultPolicy()
        self._budget_policy = UpstreamRadarRunBudgetPolicy()
        self._payloads = UpstreamRadarPayloadFactory()
        search_runner = OpenWebQueryOperationRunner(
            settings=settings,
            web_search_adapter=web_search_adapter,
            openrouter_validator=openrouter_validator,
        )
        self._operations = ExternalRadarOperationCoordinator(
            read_runner=RadarUrlReadOperationRunner(url_reader=url_reader),
            search_runner=search_runner,
        )
        self._benchmark_reporter = RadarRunBenchmarkReporter()
        self._triage_service = SearchResultTriageService()
        self._signal_extraction = SignalExtractionRunCoordinator(signal_extraction_service)

    def run(self, *, workspace: dict[str, Any], radar_id: str) -> dict[str, Any]:
        radar = _find_by_id(workspace.get("radars"), radar_id)
        if not radar:
            raise ValueError("Radar was not found in workspace.")
        handles = _resolve_handles(workspace, radar)
        started_at = self._payloads.now_iso()
        run_id = _run_id(workspace, radar_id)
        budget = self._budget_policy.for_mode(self._settings.draft_run_execution_mode)
        search_plan = build_search_plan(radar=radar, handles=handles, budget=budget, workspace=workspace)

        batch = self._operations.collect(
            run_id=run_id,
            handles=handles,
            search_plan=search_plan,
            started_at=started_at,
            budget=budget,
        )
        triage = self._triage_service.triage(
            raw_results=batch.raw_results,
            search_plan=search_plan,
            workspace=workspace,
            radar=radar,
            max_reads=int(budget["maxUrlReads"]) - int(budget["usedUrlReads"]),
        )
        raw_results = list(triage.raw_results)
        selected = list(triage.selected_for_read)
        rejected = list(triage.rejected_before_read)
        read_outcomes = self._operations.read_selected(
            batch=batch,
            run_id=run_id,
            selected=selected,
            raw_results=raw_results,
            started_at=started_at,
            budget=budget,
        )
        triage_report = triage.report.with_read_outcomes(read_outcomes)

        completed_at = self._payloads.now_iso()
        found_ids = [material["id"] for material in batch.found_materials]
        budget["usedOperations"] = len(batch.operations)
        run = {
            "id": run_id,
            "radarId": radar_id,
            "status": self._result_policy.status(
                found_materials=batch.found_materials,
                operations=batch.operations,
                errors=batch.errors,
            ),
            "startedAt": started_at,
            "completedAt": completed_at,
            "budget": budget,
            "operations": [{key: value for key, value in item.items() if key != "_rawResults"} for item in batch.operations],
            "foundMaterialIds": found_ids,
            "skippedReasons": self._result_policy.unique(batch.skipped_reasons + search_plan.get("skippedIntents", [])),
            "warnings": self._payloads.warnings_for(raw_results, batch.found_materials),
            "errors": self._result_policy.unique(batch.errors),
            "searchPlan": search_plan,
            "rawResults": raw_results,
            "selectedForRead": selected,
            "rejectedBeforeRead": rejected,
            "searchTriage": triage_report.to_payload(),
        }
        self._benchmark_reporter.attach_if_matching(
            workspace=workspace,
            radar_id=radar_id,
            run=run,
            found_materials=batch.found_materials,
        )
        extraction = self._signal_extraction.extract(
            workspace=workspace,
            radar=radar,
            run=run,
            materials=batch.found_materials,
        )
        run["signalExtraction"] = extraction["signalExtractionReport"]
        run["operations"].append(extraction["operation"])
        run["budget"]["usedOperations"] = len(run["operations"])
        run["completedAt"] = self._payloads.now_iso()
        return {
            "radar": {**radar, "lastRunAt": run["completedAt"]},
            "run": run,
            "foundMaterials": batch.found_materials,
            "sourceSignals": extraction["sourceSignals"],
            "signalExtractionReport": extraction["signalExtractionReport"],
        }

    def retry_signal_extraction(
        self,
        *,
        workspace: dict[str, Any],
        run_id: str,
        force_retry: bool,
    ) -> dict[str, Any]:
        return self._signal_extraction.retry(
            workspace=workspace,
            run_id=run_id,
            force_retry=force_retry,
        )

def _resolve_handles(workspace: dict[str, Any], radar: dict[str, Any]) -> list[dict[str, Any]]:
    registry = workspace.get("sourceRegistry") if isinstance(workspace.get("sourceRegistry"), dict) else {}
    by_id = {str(handle.get("id")): handle for handle in registry.get("handles", []) if isinstance(handle, dict)}
    return [by_id[item] for item in radar.get("sourceHandleIds", []) if item in by_id]


def _find_by_id(items: Any, item_id: str) -> dict[str, Any] | None:
    return next((item for item in items if isinstance(item, dict) and item.get("id") == item_id), None) if isinstance(items, list) else None


def _run_id(workspace: dict[str, Any], radar_id: str) -> str:
    existing_runs = [run for run in workspace.get("radarRuns", []) if isinstance(run, dict) and run.get("radarId") == radar_id]
    return f"radar-run-{radar_id}-{len(existing_runs) + 1}"


__all__ = ("UpstreamRadarExternalRunService",)
