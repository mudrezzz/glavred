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
from backend.app.upstream.application.external_read_operations import RadarUrlReadOperationRunner
from backend.app.upstream.application.external_run_budget import UpstreamRadarRunBudgetPolicy
from backend.app.upstream.application.external_run_payloads import UpstreamRadarPayloadFactory
from backend.app.upstream.application.external_run_result_policy import ExternalRunResultPolicy
from backend.app.upstream.application.external_search_operations import OpenWebQueryOperationRunner
from backend.app.upstream.application.radar_benchmark_reporter import RadarRunBenchmarkReporter
from backend.app.upstream.application.search_planner import build_search_plan
from backend.app.upstream.application.search_triage_service import SearchResultTriageService
from backend.app.upstream.domain.search_triage_contracts import SearchReadOutcome


class UpstreamRadarExternalRunService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        web_search_adapter: OpenRouterWebSearchAdapter,
        url_reader: PublicUrlReader,
        openrouter_validator: OpenRouterConfigValidator,
    ) -> None:
        self._settings = settings
        self._result_policy = ExternalRunResultPolicy()
        self._budget_policy = UpstreamRadarRunBudgetPolicy()
        self._payloads = UpstreamRadarPayloadFactory()
        self._read_runner = RadarUrlReadOperationRunner(url_reader=url_reader)
        self._search_runner = OpenWebQueryOperationRunner(
            settings=settings,
            web_search_adapter=web_search_adapter,
            openrouter_validator=openrouter_validator,
        )
        self._benchmark_reporter = RadarRunBenchmarkReporter()
        self._triage_service = SearchResultTriageService()

    def run(self, *, workspace: dict[str, Any], radar_id: str) -> dict[str, Any]:
        radar = _find_by_id(workspace.get("radars"), radar_id)
        if not radar:
            raise ValueError("Radar was not found in workspace.")
        handles = _resolve_handles(workspace, radar)
        started_at = self._payloads.now_iso()
        run_id = _run_id(workspace, radar_id)
        budget = self._budget_policy.for_mode(self._settings.draft_run_execution_mode)
        search_plan = build_search_plan(radar=radar, handles=handles, budget=budget, workspace=workspace)

        operations: list[dict[str, Any]] = []
        raw_results: list[dict[str, Any]] = []
        found_materials: list[dict[str, Any]] = []
        skipped_reasons: list[str] = []
        errors: list[str] = []

        self._read_direct_handles(run_id, handles, started_at, budget, operations, found_materials, errors)
        self._search_queries(run_id, search_plan, started_at, budget, operations, raw_results, skipped_reasons, errors)
        triage = self._triage_service.triage(
            raw_results=raw_results,
            search_plan=search_plan,
            workspace=workspace,
            radar=radar,
            max_reads=int(budget["maxUrlReads"]) - int(budget["usedUrlReads"]),
        )
        raw_results = list(triage.raw_results)
        selected = list(triage.selected_for_read)
        rejected = list(triage.rejected_before_read)
        read_outcomes = self._read_selected_results(
            run_id,
            selected,
            raw_results,
            started_at,
            budget,
            operations,
            found_materials,
        )
        triage_report = triage.report.with_read_outcomes(read_outcomes)

        completed_at = self._payloads.now_iso()
        found_ids = [material["id"] for material in found_materials]
        budget["usedOperations"] = len(operations)
        run = {
            "id": run_id,
            "radarId": radar_id,
            "status": self._result_policy.status(found_materials=found_materials, operations=operations, errors=errors),
            "startedAt": started_at,
            "completedAt": completed_at,
            "budget": budget,
            "operations": [{key: value for key, value in item.items() if key != "_rawResults"} for item in operations],
            "foundMaterialIds": found_ids,
            "skippedReasons": self._result_policy.unique(skipped_reasons + search_plan.get("skippedIntents", [])),
            "warnings": self._payloads.warnings_for(raw_results, found_materials),
            "errors": self._result_policy.unique(errors),
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
            found_materials=found_materials,
        )
        return {"radar": {**radar, "lastRunAt": completed_at}, "run": run, "foundMaterials": found_materials}

    def _read_direct_handles(
        self,
        run_id: str,
        handles: list[dict[str, Any]],
        started_at: str,
        budget: dict[str, int],
        operations: list[dict[str, Any]],
        found_materials: list[dict[str, Any]],
        errors: list[str],
    ) -> None:
        for handle in handles:
            if not _can_read_url(handle) or budget["usedUrlReads"] >= budget["maxUrlReads"]:
                continue
            material, read_operation = self._read_runner.read_direct_handle(
                run_id=run_id,
                handle=handle,
                started_at=started_at,
            )
            operations.append(read_operation)
            budget["usedUrlReads"] += 1
            if material:
                found_materials.append(material)
                budget["usedFoundMaterials"] += 1
            elif read_operation.get("error"):
                errors.append(str(read_operation["error"]))

    def _search_queries(
        self,
        run_id: str,
        search_plan: dict[str, Any],
        started_at: str,
        budget: dict[str, int],
        operations: list[dict[str, Any]],
        raw_results: list[dict[str, Any]],
        skipped_reasons: list[str],
        errors: list[str],
    ) -> None:
        for query in search_plan["queries"]:
            search_operation = self._search_runner.search(
                run_id=run_id,
                query=query,
                started_at=started_at,
                run_budget=budget,
            )
            operations.append(search_operation)
            if search_operation["status"] == "succeeded":
                raw_results.extend(search_operation.pop("_rawResults"))
                budget["usedExternalQueries"] += 1
            elif search_operation.get("skippedReason"):
                skipped_reasons.append(str(search_operation["skippedReason"]))
            elif search_operation.get("error"):
                errors.append(str(search_operation["error"]))

    def _read_selected_results(
        self,
        run_id: str,
        selected: list[dict[str, Any]],
        raw_results: list[dict[str, Any]],
        started_at: str,
        budget: dict[str, int],
        operations: list[dict[str, Any]],
        found_materials: list[dict[str, Any]],
    ) -> list[SearchReadOutcome]:
        outcomes: list[SearchReadOutcome] = []
        for selection in selected:
            material, read_operation, outcome = self._read_runner.read_selection(
                run_id=run_id,
                selection=selection,
                raw_results=raw_results,
                started_at=started_at,
            )
            operations.append(read_operation)
            found_materials.append(material)
            outcomes.append(outcome)
            budget["usedUrlReads"] += 1
            budget["usedFoundMaterials"] += 1
        return outcomes

def _resolve_handles(workspace: dict[str, Any], radar: dict[str, Any]) -> list[dict[str, Any]]:
    registry = workspace.get("sourceRegistry") if isinstance(workspace.get("sourceRegistry"), dict) else {}
    by_id = {str(handle.get("id")): handle for handle in registry.get("handles", []) if isinstance(handle, dict)}
    return [by_id[item] for item in radar.get("sourceHandleIds", []) if item in by_id]


def _can_read_url(handle: dict[str, Any]) -> bool:
    capabilities = handle.get("capabilities") if isinstance(handle.get("capabilities"), dict) else {}
    return bool(capabilities.get("canReadUrl")) or str(handle.get("type") or "") == "externalUrl"


def _find_by_id(items: Any, item_id: str) -> dict[str, Any] | None:
    return next((item for item in items if isinstance(item, dict) and item.get("id") == item_id), None) if isinstance(items, list) else None


def _run_id(workspace: dict[str, Any], radar_id: str) -> str:
    existing_runs = [run for run in workspace.get("radarRuns", []) if isinstance(run, dict) and run.get("radarId") == radar_id]
    return f"radar-run-{radar_id}-{len(existing_runs) + 1}"


__all__ = ("UpstreamRadarExternalRunService",)
