"""Owner: drafting.application.reliability

Used by: DraftRun reliability signal coverage reports.
Does not own: child AiRun coverage, budget coverage, event extraction, or remediation policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any

from backend.app.drafting.application.reliability.contracts import ReliabilitySignalCoverageRecord
from backend.app.drafting.application.reliability.signal_coverage_utils import (
    _dict,
    _incident_from_error,
    _list,
    _optional_str,
    _record,
    _status,
)


class OperationSignalCoverageComponent:
    """Audits operation-envelope, attempt, retry, backup, and fallback signals."""

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
        envelope = _dict(payload.get("operationEnvelope"))
        if envelope:
            records.extend(
                self._operation_envelope_records(
                    run_id=run_id,
                    step_key=step_key,
                    path=f"{path}.operationEnvelope" if path else "operationEnvelope",
                    envelope=envelope,
                    operation_ids=operation_ids,
                )
            )
        records.extend(
            self._attempt_records(
                run_id=run_id,
                step_key=step_key,
                path=path,
                payload=payload,
                operation_id=operation_id,
                operation_ids=operation_ids,
            )
        )
        if payload.get("fallbackUsed") is True:
            records.append(
                _record(
                    run_id,
                    step_key,
                    f"{path}.fallbackUsed" if path else "fallbackUsed",
                    "fallback",
                    operation_id,
                    operation_ids,
                    incident_type="deterministicFallback",
                    reason="countedByOperationSummary",
                )
            )
        return records

    def _operation_envelope_records(
        self,
        *,
        run_id: str,
        step_key: str,
        path: str,
        envelope: dict[str, Any],
        operation_ids: set[str],
    ) -> list[ReliabilitySignalCoverageRecord]:
        operation_id = str(envelope.get("operationId") or path or step_key)
        incident = _dict(envelope.get("incident"))
        incident_type = _optional_str(incident.get("incidentType"))
        records: list[ReliabilitySignalCoverageRecord] = []
        if incident_type:
            records.append(
                _record(
                    run_id,
                    step_key,
                    f"{path}.incident",
                    "operationEnvelopeIncident",
                    operation_id,
                    operation_ids,
                    incident_type=incident_type,
                    reason="countedByOperationSummary",
                )
            )
        status = _status(envelope)
        if status in {"fallback", "backupaccepted", "failed", "notrun", "timeout", "cancelled", "stale"}:
            records.append(
                _record(
                    run_id,
                    step_key,
                    f"{path}.status",
                    _signal_type_from_status(status),
                    operation_id,
                    operation_ids,
                    incident_type=_incident_from_status(status, incident_type),
                    reason="countedByOperationSummary",
                )
            )
        return records

    def _attempt_records(
        self,
        *,
        run_id: str,
        step_key: str,
        path: str,
        payload: dict[str, Any],
        operation_id: str,
        operation_ids: set[str],
    ) -> list[ReliabilitySignalCoverageRecord]:
        attempts = [_dict(item) for item in _list(payload.get("attempts")) if isinstance(item, dict)]
        records: list[ReliabilitySignalCoverageRecord] = []
        if len(attempts) > 1:
            records.append(
                _record(
                    run_id,
                    step_key,
                    f"{path}.attempts" if path else "attempts",
                    "retry",
                    operation_id,
                    operation_ids,
                    reason="countedByOperationSummary",
                )
            )
        for index, attempt in enumerate(attempts):
            records.extend(self._single_attempt_records(run_id, step_key, path, operation_id, operation_ids, index, attempt))
        return records

    def _single_attempt_records(
        self,
        run_id: str,
        step_key: str,
        path: str,
        operation_id: str,
        operation_ids: set[str],
        index: int,
        attempt: dict[str, Any],
    ) -> list[ReliabilitySignalCoverageRecord]:
        attempt_path = f"{path}.attempts[{index}]" if path else f"attempts[{index}]"
        incident = _dict(attempt.get("incident"))
        incident_type = _optional_str(incident.get("incidentType"))
        status = _status(attempt)
        records: list[ReliabilitySignalCoverageRecord] = []
        if incident_type:
            records.append(
                _record(run_id, step_key, f"{attempt_path}.incident", "attemptIncident", operation_id, operation_ids, incident_type=incident_type, reason="countedByOperationSummary")
            )
        if attempt.get("error"):
            records.append(
                _record(run_id, step_key, f"{attempt_path}.error", "attemptError", operation_id, operation_ids, incident_type=_incident_from_error(str(attempt.get("error") or "")), reason="countedByOperationSummary")
            )
        if bool(attempt.get("backup")) or status == "backupaccepted":
            records.append(
                _record(run_id, step_key, attempt_path, "backup", operation_id, operation_ids, incident_type="backupAccepted", reason="countedByOperationSummary")
            )
        if status == "fallback":
            records.append(
                _record(run_id, step_key, attempt_path, "fallback", operation_id, operation_ids, incident_type="deterministicFallback", reason="countedByOperationSummary")
            )
        return records


def _signal_type_from_status(status: str) -> str:
    if status == "backupaccepted":
        return "backup"
    if status in {"failed", "notrun", "timeout", "cancelled", "stale"}:
        return "operationTerminalStatus"
    return status or "operationStatus"


def _incident_from_status(status: str, incident_type: str | None) -> str | None:
    if incident_type:
        return incident_type
    if status == "backupaccepted":
        return "backupAccepted"
    if status == "fallback":
        return "deterministicFallback"
    if status == "timeout":
        return "providerTimeout"
    if status == "notrun":
        return "notRun"
    return status if status in {"failed", "cancelled", "stale"} else None
