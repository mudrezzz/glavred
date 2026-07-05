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
from backend.app.upstream.application.external_payloads import (
    budget_for_mode,
    material_from_raw,
    material_from_read,
    now_iso,
    operation,
    raw_result,
    safe_error,
    stable_slug,
    warnings_for,
)
from backend.app.upstream.application.search_planner import build_search_plan
from backend.app.upstream.application.search_triage import select_results_for_read


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
        self._web_search_adapter = web_search_adapter
        self._url_reader = url_reader
        self._openrouter_validator = openrouter_validator

    def run(self, *, workspace: dict[str, Any], radar_id: str) -> dict[str, Any]:
        radar = _find_by_id(workspace.get("radars"), radar_id)
        if not radar:
            raise ValueError("Radar was not found in workspace.")
        handles = _resolve_handles(workspace, radar)
        started_at = now_iso()
        run_id = _run_id(workspace, radar_id)
        budget = budget_for_mode(self._settings.draft_run_execution_mode)
        search_plan = build_search_plan(radar=radar, handles=handles, budget=budget, workspace=workspace)

        operations: list[dict[str, Any]] = []
        raw_results: list[dict[str, Any]] = []
        found_materials: list[dict[str, Any]] = []
        skipped_reasons: list[str] = []
        errors: list[str] = []

        self._read_direct_handles(run_id, handles, started_at, budget, operations, found_materials, errors)
        self._search_queries(run_id, search_plan, started_at, budget, operations, raw_results, skipped_reasons, errors)
        selected, rejected = select_results_for_read(raw_results, int(budget["maxUrlReads"]) - int(budget["usedUrlReads"]))
        self._read_selected_results(run_id, selected, raw_results, started_at, budget, operations, found_materials)

        completed_at = now_iso()
        found_ids = [material["id"] for material in found_materials]
        budget["usedOperations"] = len(operations)
        run = {
            "id": run_id,
            "radarId": radar_id,
            "status": _status(found_ids, operations, errors),
            "startedAt": started_at,
            "completedAt": completed_at,
            "budget": budget,
            "operations": [{key: value for key, value in item.items() if key != "_rawResults"} for item in operations],
            "foundMaterialIds": found_ids,
            "skippedReasons": _unique(skipped_reasons + search_plan.get("skippedIntents", [])),
            "warnings": warnings_for(raw_results, found_materials),
            "errors": _unique(errors),
            "searchPlan": search_plan,
            "rawResults": raw_results,
            "selectedForRead": selected,
            "rejectedBeforeRead": rejected,
        }
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
            material, read_operation = self._read_direct_handle(run_id, handle, started_at)
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
            search_operation = self._search_operation(run_id, query, started_at)
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
    ) -> None:
        for selection in selected:
            material, read_operation = self._read_selection(run_id, selection, raw_results, started_at)
            operations.append(read_operation)
            found_materials.append(material)
            budget["usedUrlReads"] += 1
            budget["usedFoundMaterials"] += 1

    def _read_direct_handle(self, run_id: str, handle: dict[str, Any], started_at: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        operation_id = f"{run_id}-read-{handle.get('id')}"
        title = str(handle.get("title") or handle.get("locator") or "URL")
        target = str(handle.get("locator") or "")
        try:
            read = self._url_reader.read(target)
            material_id = f"{run_id}-material-{stable_slug(str(handle.get('id') or 'url'))}"
            return material_from_read(material_id=material_id, run_id=run_id, source_handle_id=str(handle["id"]), title=title, read=read, provenance=title), operation(
                operation_id=operation_id,
                run_id=run_id,
                source_handle_id=str(handle["id"]),
                kind="readUrl",
                label=title,
                status="succeeded",
                started_at=started_at,
                target=target,
                found_material_ids=[material_id],
            )
        except Exception as exc:
            error = safe_error(exc)
            return None, operation(operation_id=operation_id, run_id=run_id, source_handle_id=str(handle["id"]), kind="readUrl", label=title, status="failed", started_at=started_at, target=target, error=error)

    def _search_operation(self, run_id: str, query: dict[str, Any], started_at: str) -> dict[str, Any]:
        operation_id = f"{run_id}-search-{query['id']}"
        if not self._settings.openrouter_web_tools_enabled:
            return _search_skip(operation_id, run_id, query, started_at, "openrouter-web-tools-disabled")
        if not self._openrouter_validator.evaluate(self._settings).configured:
            return _search_skip(operation_id, run_id, query, started_at, "openrouter-not-configured")
        try:
            result = self._web_search_adapter.search(settings=self._settings, query=query["query"], messages=_search_messages(query["query"]), max_results=int(self._settings.openrouter_web_search_max_results or 5))
            payload = _search_success(operation_id, run_id, query, started_at)
            payload["_rawResults"] = [raw_result(run_id, query, citation, index) for index, citation in enumerate(result.citations)]
            return payload
        except Exception as exc:
            return {**_search_fail(operation_id, run_id, query, started_at, safe_error(exc)), "_rawResults": []}

    def _read_selection(self, run_id: str, selection: dict[str, Any], raw_results: list[dict[str, Any]], started_at: str) -> tuple[dict[str, Any], dict[str, Any]]:
        raw = next(item for item in raw_results if item["id"] == selection["rawResultId"])
        material_id = f"{run_id}-material-{stable_slug(raw['duplicateKey'])}"
        operation_id = f"{run_id}-read-{material_id}"
        try:
            read = self._url_reader.read(raw["url"])
            material = material_from_read(material_id=material_id, run_id=run_id, source_handle_id=raw["sourceHandleId"], title=raw["title"], read=read, provenance=f"{raw['provider']} / {raw['domain']}")
        except Exception as exc:
            material = material_from_raw(material_id=material_id, run_id=run_id, raw=raw, warning=f"url-read-failed:{safe_error(exc)}")
        return material, operation(operation_id=operation_id, run_id=run_id, source_handle_id=raw["sourceHandleId"], kind="readUrl", label=raw["title"], status="succeeded", started_at=started_at, target=raw["url"], found_material_ids=[material_id])


def _search_messages(query: str) -> list[dict[str, str]]:
    return [{"role": "system", "content": "Use web search to find public source material. Return citations. Do not invent sources."}, {"role": "user", "content": query}]


def _search_success(operation_id: str, run_id: str, query: dict[str, Any], started_at: str) -> dict[str, Any]:
    return operation(operation_id=operation_id, run_id=run_id, source_handle_id=query["sourceHandleId"], kind="openWebQuery", label=query["label"], status="succeeded", started_at=started_at, target=query["query"])


def _search_skip(operation_id: str, run_id: str, query: dict[str, Any], started_at: str, reason: str) -> dict[str, Any]:
    return {**operation(operation_id=operation_id, run_id=run_id, source_handle_id=query["sourceHandleId"], kind="openWebQuery", label=query["label"], status="skipped", started_at=started_at, target=query["query"], skipped_reason=reason), "_rawResults": []}


def _search_fail(operation_id: str, run_id: str, query: dict[str, Any], started_at: str, error: str) -> dict[str, Any]:
    return operation(operation_id=operation_id, run_id=run_id, source_handle_id=query["sourceHandleId"], kind="openWebQuery", label=query["label"], status="failed", started_at=started_at, target=query["query"], error=error)


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


def _status(found_ids: list[str], operations: list[dict[str, Any]], errors: list[str]) -> str:
    if found_ids and not errors:
        return "succeeded"
    if found_ids or operations:
        return "partial"
    return "failed"


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


__all__ = ("UpstreamRadarExternalRunService",)
