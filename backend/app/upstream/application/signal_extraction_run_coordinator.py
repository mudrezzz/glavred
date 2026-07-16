"""Owner: upstream.application

Used by: RadarRun orchestration for automatic extraction and explicit retries.
Does not own: provider calls, search, URL reading, project scoring, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.upstream.application.signal_extraction_retry_policy import SignalExtractionRetryPolicy
from backend.app.upstream.application.signal_extraction_service import SignalExtractionService


class SignalExtractionRunCoordinator:
    def __init__(self, service: SignalExtractionService | None) -> None:
        self._service = service
        self._retry_policy = SignalExtractionRetryPolicy()

    def extract(
        self,
        *,
        workspace: dict[str, Any],
        radar: dict[str, Any],
        run: dict[str, Any],
        materials: list[dict[str, Any]],
        previous_report: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if self._service is not None:
            return self._service.extract(
                workspace=workspace,
                radar=radar,
                run=run,
                materials=materials,
                previous_report=previous_report,
            )
        now = datetime.now(UTC).isoformat()
        return {
            "sourceSignals": [],
            "signalExtractionReport": {
                "status": "notRun",
                "revision": 1,
                "materialDecisions": [],
                "warnings": ["signal-extraction-service-unavailable"],
            },
            "operation": {
                "id": f"{run.get('id')}-signal-extraction-unavailable",
                "runId": run.get("id"),
                "sourceHandleId": str(run.get("radarId") or ""),
                "kind": "signalExtraction",
                "label": "Извлечение доказательных сигналов",
                "status": "skipped",
                "startedAt": now,
                "completedAt": now,
                "foundMaterialIds": [],
                "skippedReason": "signal-extraction-service-unavailable",
            },
        }

    def retry(
        self,
        *,
        workspace: dict[str, Any],
        run_id: str,
        force_retry: bool,
    ) -> dict[str, Any]:
        run = self._find(workspace.get("radarRuns"), run_id)
        if not run:
            raise ValueError("RadarRun was not found in workspace.")
        radar = self._find(workspace.get("radars"), str(run.get("radarId") or ""))
        if not radar:
            raise ValueError("Radar was not found in workspace.")
        existing = run.get("signalExtraction") if isinstance(run.get("signalExtraction"), dict) else None
        existing_signals = [
            item for item in workspace.get("sourceSignals", [])
            if isinstance(item, dict) and item.get("radarRunId") == run_id
        ]
        if existing and existing.get("status") == "succeeded" and not force_retry:
            return {"run": run, "signalExtractionReport": existing, "sourceSignals": existing_signals}
        found_ids = set(run.get("foundMaterialIds") or [])
        materials = [
            item for item in workspace.get("foundMaterials", [])
            if isinstance(item, dict) and (item.get("radarRunId") == run_id or item.get("id") in found_ids)
        ]
        extraction = self.extract(
            workspace=workspace,
            radar=radar,
            run=run,
            materials=materials,
            previous_report=existing,
        )
        extraction = self._retry_policy.resolve(
            existing_report=existing,
            existing_signals=existing_signals,
            extraction=extraction,
        )
        operations = [*list(run.get("operations") or []), extraction["operation"]]
        updated_run = {
            **run,
            "signalExtraction": extraction["signalExtractionReport"],
            "operations": operations,
            "budget": {**dict(run.get("budget") or {}), "usedOperations": len(operations)},
        }
        return {
            "run": updated_run,
            "signalExtractionReport": extraction["signalExtractionReport"],
            "sourceSignals": extraction["sourceSignals"],
        }

    def _find(self, items: Any, item_id: str) -> dict[str, Any] | None:
        if not isinstance(items, list):
            return None
        return next((item for item in items if isinstance(item, dict) and item.get("id") == item_id), None)


__all__ = ("SignalExtractionRunCoordinator",)
