"""Owner: upstream.application

Used by: RadarRun orchestration for automatic and manual signal scoring.
Does not own: search, extraction, provider semantics, review transitions, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.upstream.application.signal_relationships import SignalRelationshipPolicy
from backend.app.upstream.application.signal_utility_service import SignalUtilityScoringService


class SignalUtilityRunCoordinator:
    def __init__(self, service: SignalUtilityScoringService | None) -> None:
        self._service = service
        self._relationships = SignalRelationshipPolicy()

    def score(
        self,
        *,
        workspace: dict[str, Any],
        radar: dict[str, Any],
        run: dict[str, Any],
        signals: list[dict[str, Any]],
        project_context: dict[str, Any] | None,
        previous_report: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if self._service is None:
            revision = int((previous_report or {}).get("revision") or 0) + 1
            relationships = self._relationships.reports(signals)
            updated = [
                {
                    **item,
                    "utilityRevision": revision,
                    "utilityReport": {
                        "version": 2,
                        "revision": revision,
                        "status": "inconclusive",
                        "recommendation": "inconclusive",
                        "dimensions": [],
                        "blockingReasons": [],
                        "warnings": ["signal-scoring-service-unavailable"],
                        "evaluationPlanVersion": 2,
                        "radarCriteria": [],
                        "projectCriteria": [],
                        "qualityChecks": [],
                        "notApplicableSettings": [],
                        "relationshipReport": relationships.get(str(item.get("id") or "")).to_payload()
                        if relationships.get(str(item.get("id") or ""))
                        else None,
                    },
                    "relationshipReport": relationships.get(str(item.get("id") or "")).to_payload()
                    if relationships.get(str(item.get("id") or ""))
                    else None,
                }
                for item in signals
            ]
            now = datetime.now(UTC).isoformat()
            report = {
                "version": 2,
                "runId": run.get("id"),
                "status": "inconclusive",
                "revision": revision,
                "signalIds": [str(item.get("id") or "") for item in signals],
                "evaluations": [{"signalId": item.get("id"), **item["utilityReport"]} for item in updated],
                "providerAttempts": [],
                "warnings": ["signal-scoring-service-unavailable"],
                "decisionCoverageComplete": True,
            }
            operation = {
                "id": f"{run.get('id')}-signal-scoring-r{revision}",
                "runId": run.get("id"),
                "sourceHandleId": "signal-utility",
                "kind": "signalScoring",
                "label": "Оценка редакционной полезности сигналов",
                "status": "skipped",
                "startedAt": now,
                "completedAt": now,
                "skippedReason": "signal-scoring-service-unavailable",
            }
            return {"sourceSignals": updated, "signalScoringReport": report, "operation": operation}
        return self._service.score(
            workspace=workspace,
            radar=radar,
            run=run,
            signals=signals,
            project_context=project_context,
            previous_report=previous_report,
        )

    def retry(
        self,
        *,
        workspace: dict[str, Any],
        run_id: str,
        project_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        run = self._find(workspace.get("radarRuns"), run_id)
        if not run:
            raise ValueError("RadarRun was not found in workspace.")
        radar = self._find(workspace.get("radars"), str(run.get("radarId") or ""))
        if not radar:
            raise ValueError("Radar was not found in workspace.")
        signals = [
            item for item in workspace.get("sourceSignals", [])
            if isinstance(item, dict) and item.get("radarRunId") == run_id
        ]
        result = self.score(
            workspace=workspace,
            radar=radar,
            run=run,
            signals=signals,
            project_context=project_context,
            previous_report=run.get("signalScoring") if isinstance(run.get("signalScoring"), dict) else None,
        )
        operations = [*list(run.get("operations") or []), result["operation"]]
        updated_run = {
            **run,
            "signalScoring": result["signalScoringReport"],
            "operations": operations,
            "budget": {**dict(run.get("budget") or {}), "usedOperations": len(operations)},
        }
        return {**result, "run": updated_run}

    def _find(self, items: Any, item_id: str) -> dict[str, Any] | None:
        if not isinstance(items, list):
            return None
        return next((item for item in items if isinstance(item, dict) and item.get("id") == item_id), None)


__all__ = ("SignalUtilityRunCoordinator",)
