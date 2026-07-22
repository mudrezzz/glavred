"""Owner: upstream.application

Used by: external RadarRun orchestration to execute search and URL-read operations.
Does not own: search planning, triage policy, signal extraction, benchmarks, or persistence.
Architecture doc: docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.app.upstream.application.external_read_operations import RadarUrlReadOperationRunner
from backend.app.upstream.application.external_search_operations import OpenWebQueryOperationRunner
from backend.app.upstream.domain.search_triage_contracts import SearchReadOutcome


@dataclass
class ExternalOperationBatch:
    operations: list[dict[str, Any]] = field(default_factory=list)
    raw_results: list[dict[str, Any]] = field(default_factory=list)
    found_materials: list[dict[str, Any]] = field(default_factory=list)
    skipped_reasons: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class ExternalRadarOperationCoordinator:
    def __init__(
        self,
        *,
        read_runner: RadarUrlReadOperationRunner,
        search_runner: OpenWebQueryOperationRunner,
    ) -> None:
        self._read_runner = read_runner
        self._search_runner = search_runner

    def collect(
        self,
        *,
        run_id: str,
        handles: list[dict[str, Any]],
        search_plan: dict[str, Any],
        started_at: str,
        budget: dict[str, int],
    ) -> ExternalOperationBatch:
        batch = ExternalOperationBatch()
        for handle in handles:
            if not self._can_read_url(handle) or budget["usedUrlReads"] >= budget["maxUrlReads"]:
                continue
            material, operation = self._read_runner.read_direct_handle(
                run_id=run_id,
                handle=handle,
                started_at=started_at,
            )
            batch.operations.append(operation)
            budget["usedUrlReads"] += 1
            if material:
                batch.found_materials.append(material)
                budget["usedFoundMaterials"] += 1
            elif operation.get("error"):
                batch.errors.append(str(operation["error"]))

        for query in search_plan["queries"]:
            operation = self._search_runner.search(
                run_id=run_id,
                query=query,
                started_at=started_at,
                run_budget=budget,
            )
            batch.operations.append(operation)
            if operation["status"] == "succeeded":
                batch.raw_results.extend(operation.pop("_rawResults"))
                budget["usedExternalQueries"] += 1
            elif operation.get("skippedReason"):
                batch.skipped_reasons.append(str(operation["skippedReason"]))
            elif operation.get("error"):
                batch.errors.append(str(operation["error"]))
        return batch

    def read_selected(
        self,
        *,
        batch: ExternalOperationBatch,
        run_id: str,
        selected: list[dict[str, Any]],
        raw_results: list[dict[str, Any]],
        started_at: str,
        budget: dict[str, int],
    ) -> list[SearchReadOutcome]:
        outcomes: list[SearchReadOutcome] = []
        for selection in selected:
            material, operation, outcome = self._read_runner.read_selection(
                run_id=run_id,
                selection=selection,
                raw_results=raw_results,
                started_at=started_at,
            )
            batch.operations.append(operation)
            batch.found_materials.append(material)
            outcomes.append(outcome)
            budget["usedUrlReads"] += 1
            budget["usedFoundMaterials"] += 1
        return outcomes

    def _can_read_url(self, handle: dict[str, Any]) -> bool:
        capabilities = handle.get("capabilities") if isinstance(handle.get("capabilities"), dict) else {}
        return bool(capabilities.get("canReadUrl")) or str(handle.get("type") or "") == "externalUrl"


__all__ = ("ExternalOperationBatch", "ExternalRadarOperationCoordinator")
