"""Owner: drafting.application.reliability

Used by: DraftRun reliability event extraction.
Does not own: quality/fidelity verdict construction, payload budgeting, provider execution, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any

from backend.app.drafting.application.reliability.contracts import OperationReliabilityEvent


class RawArtifactReliabilityEventComponent:
    """Creates events for fallback and runtime-budget signals absent from stage summaries."""

    def events(
        self,
        *,
        run_id: str,
        steps: list[dict[str, Any]],
        existing: list[OperationReliabilityEvent],
        execution_mode: str | None,
    ) -> list[OperationReliabilityEvent]:
        existing_ids = {event.operation_id for event in existing}
        events: list[OperationReliabilityEvent] = []
        for step in steps:
            step_key = str(step.get("key") or "unknown")
            for path, payload in _walk_dicts(_dict(step.get("artifact"))):
                operation_id = _operation_id(step_key, path, payload)
                if operation_id in existing_ids:
                    continue
                event = self._event_for_payload(run_id, step_key, operation_id, payload, execution_mode)
                if event is None:
                    continue
                events.append(event)
                existing_ids.add(operation_id)
        return events

    def _event_for_payload(
        self,
        run_id: str,
        step_key: str,
        operation_id: str,
        payload: dict[str, Any],
        execution_mode: str | None,
    ) -> OperationReliabilityEvent | None:
        if payload.get("fallbackUsed") is True:
            return self._raw_event(
                run_id=run_id,
                step_key=step_key,
                operation_id=operation_id,
                execution_mode=execution_mode,
                outcome="fallbackRecovered",
                incident_types=("deterministicFallback",),
                retry_path="fallbackRecovered",
                result_impact="fallbackRecovered",
                source="rawArtifact.fallbackUsed",
            )
        incident_types = self._runtime_budget_incidents(_dict(payload.get("runtimeBudget")))
        if not incident_types:
            return None
        return self._raw_event(
            run_id=run_id,
            step_key=step_key,
            operation_id=operation_id,
            execution_mode=execution_mode,
            outcome="degraded",
            incident_types=incident_types,
            retry_path="runtimeBudgetIncident",
            result_impact="providerIncident" if "providerIncident" in incident_types else "stepDegraded",
            source="rawArtifact.runtimeBudget",
        )

    def _runtime_budget_incidents(self, runtime_budget: dict[str, Any]) -> tuple[str, ...]:
        if not runtime_budget:
            return ()
        incidents: list[str] = []
        for item in _list(runtime_budget.get("incidents")):
            incident = _dict(item)
            incidents.append(str(incident.get("incidentType") or incident.get("stopReason") or "runtimeBudget"))
        stop_reason = str(runtime_budget.get("stopReason") or "")
        if runtime_budget.get("exhausted") and stop_reason:
            incidents.append(stop_reason)
        if stop_reason in {"budgetExhausted", "providerIncident"}:
            incidents.append(stop_reason)
        return tuple(_unique([item for item in incidents if item]))

    def _raw_event(
        self,
        *,
        run_id: str,
        step_key: str,
        operation_id: str,
        execution_mode: str | None,
        outcome: str,
        incident_types: tuple[str, ...],
        retry_path: str,
        result_impact: str,
        source: str,
    ) -> OperationReliabilityEvent:
        return OperationReliabilityEvent(
            run_id=run_id,
            step_key=step_key,
            operation_id=operation_id,
            operation_kind=operation_id.split(":", 1)[0] if ":" in operation_id else operation_id or "unknown",
            provider=None,
            model=None,
            model_role=None,
            execution_mode=execution_mode,
            attempt_count=0,
            retry_path=retry_path,
            result_impact=result_impact,
            outcome=outcome,  # type: ignore[arg-type]
            incident_types=incident_types,
            source=source,
        )


def _operation_id(step_key: str, path: str, payload: dict[str, Any]) -> str:
    return str(_dict(payload.get("operationEnvelope")).get("operationId") or payload.get("operationId") or path or step_key)


def _walk_dicts(value: dict[str, Any], path: str = "") -> list[tuple[str, dict[str, Any]]]:
    items = [(path, value)]
    for key, child in value.items():
        if isinstance(child, dict):
            items.extend(_walk_dicts(child, f"{path}.{key}" if path else str(key)))
        elif isinstance(child, list):
            for index, list_child in enumerate(child):
                if isinstance(list_child, dict):
                    items.extend(_walk_dicts(list_child, f"{path}.{key}[{index}]" if path else f"{key}[{index}]"))
    return items


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
