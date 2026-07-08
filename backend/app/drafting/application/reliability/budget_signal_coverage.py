"""Owner: drafting.application.reliability

Used by: DraftRun reliability signal coverage reports.
Does not own: payload budget policy, runtime budget policy, event extraction, or remediation.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any

from backend.app.drafting.application.reliability.contracts import ReliabilitySignalCoverageRecord
from backend.app.drafting.application.reliability.signal_coverage_utils import _dict, _list, _record


class BudgetSignalCoverageComponent:
    """Audits payload and runtime budget incidents or stats-only payloads."""

    def records(
        self,
        *,
        run_id: str,
        step_key: str,
        path: str,
        payload: dict[str, Any],
        operation_id: str,
        operation_ids: set[str],
    ) -> list[ReliabilitySignalCoverageRecord]:
        records: list[ReliabilitySignalCoverageRecord] = []
        records.extend(
            self._payload_budget_records(
                run_id=run_id,
                step_key=step_key,
                path=path,
                payload_budget=_dict(payload.get("payloadBudget")),
                operation_id=operation_id,
                operation_ids=operation_ids,
            )
        )
        records.extend(
            self._runtime_budget_records(
                run_id=run_id,
                step_key=step_key,
                path=path,
                runtime_budget=_dict(payload.get("runtimeBudget")),
                operation_id=operation_id,
                operation_ids=operation_ids,
            )
        )
        return records

    def _payload_budget_records(
        self,
        *,
        run_id: str,
        step_key: str,
        path: str,
        payload_budget: dict[str, Any],
        operation_id: str,
        operation_ids: set[str],
    ) -> list[ReliabilitySignalCoverageRecord]:
        if not payload_budget:
            return []
        incident_type = _budget_incident(payload_budget)
        return [
            self._budget_record(
                run_id,
                step_key,
                f"{path}.payloadBudget" if path else "payloadBudget",
                "payloadBudgetIncident" if incident_type else "payloadBudgetStats",
                operation_id,
                operation_ids,
                incident_type=incident_type,
                ignored_reason="budgetStatsOnly",
            )
        ]

    def _runtime_budget_records(
        self,
        *,
        run_id: str,
        step_key: str,
        path: str,
        runtime_budget: dict[str, Any],
        operation_id: str,
        operation_ids: set[str],
    ) -> list[ReliabilitySignalCoverageRecord]:
        if not runtime_budget:
            return []
        incidents = _list(runtime_budget.get("incidents"))
        if incidents:
            return [
                self._budget_record(
                    run_id,
                    step_key,
                    f"{path}.runtimeBudget.incidents[{index}]" if path else f"runtimeBudget.incidents[{index}]",
                    "runtimeBudgetIncident",
                    operation_id,
                    operation_ids,
                    incident_type=str(_dict(incident).get("incidentType") or runtime_budget.get("stopReason") or "runtimeBudget"),
                    ignored_reason="runtimeBudgetStatsOnly",
                )
                for index, incident in enumerate(incidents)
            ]
        if runtime_budget.get("exhausted") or runtime_budget.get("stopReason") in {"budgetExhausted", "providerIncident"}:
            return [
                self._budget_record(
                    run_id,
                    step_key,
                    f"{path}.runtimeBudget" if path else "runtimeBudget",
                    "runtimeBudgetIncident",
                    operation_id,
                    operation_ids,
                    incident_type=str(runtime_budget.get("stopReason") or "budgetExhausted"),
                    ignored_reason="runtimeBudgetStatsOnly",
                )
            ]
        return [
            self._budget_record(
                run_id,
                step_key,
                f"{path}.runtimeBudget" if path else "runtimeBudget",
                "runtimeBudgetStats",
                operation_id,
                operation_ids,
                incident_type=None,
                ignored_reason="runtimeBudgetStatsOnly",
            )
        ]

    def _budget_record(
        self,
        run_id: str,
        step_key: str,
        path: str,
        signal_type: str,
        operation_id: str,
        operation_ids: set[str],
        *,
        incident_type: str | None,
        ignored_reason: str,
    ) -> ReliabilitySignalCoverageRecord:
        if incident_type:
            return _record(
                run_id,
                step_key,
                path,
                signal_type,
                operation_id,
                operation_ids,
                incident_type=incident_type,
                reason="countedByOperationSummary",
            )
        return ReliabilitySignalCoverageRecord(
            run_id=run_id,
            step_key=step_key,
            path=path,
            signal_type=signal_type,
            coverage_status="ignored",
            reason=ignored_reason,
            operation_id=operation_id,
            incident_type=None,
            ai_run_id=None,
        )


def _budget_incident(payload_budget: dict[str, Any]) -> str | None:
    incident = _dict(payload_budget.get("incident"))
    if incident.get("incidentType"):
        return str(incident["incidentType"])
    quality_risk = _dict(payload_budget.get("qualityRisk"))
    if quality_risk.get("incidentType"):
        return str(quality_risk["incidentType"])
    if payload_budget.get("overBudget") or payload_budget.get("contextOverBudget"):
        return "contextOverBudget"
    if payload_budget.get("payloadTooLarge"):
        return "payloadTooLarge"
    return None
