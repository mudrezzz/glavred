from datetime import UTC, datetime
from typing import Any

from backend.app.application.draft_run_pipeline_ports import DraftRunPipelineRepository
from backend.app.domain.draft_run_steps import DraftRunStepKey, DraftRunStepStatus


class DraftRunStepOperationSink:
    def __init__(
        self,
        repository: DraftRunPipelineRepository,
        run_id: str,
        step_key: DraftRunStepKey,
        *,
        total_operations: int | None = None,
    ) -> None:
        self._repository = repository
        self._run_id = run_id
        self._step_key = step_key
        self._current_operation_id: str | None = None
        self._operations: list[dict[str, Any]] = []
        self._total_operations = total_operations

    def start_operation(
        self,
        operation_id: str,
        *,
        kind: str,
        label: str,
        target: str | None = None,
        notes: list[str] | None = None,
    ) -> None:
        operation = self._find_or_create(operation_id, kind=kind, label=label, target=target)
        operation.update({
            "status": "running",
            "startedAt": operation.get("startedAt") or _now(),
            "completedAt": None,
        })
        if notes:
            operation["notes"] = notes
        self._current_operation_id = operation_id
        self._persist("running")

    def complete_operation(
        self,
        operation_id: str,
        *,
        ai_run_id: str | None = None,
        notes: list[str] | None = None,
    ) -> None:
        operation = self._find_or_create(operation_id, kind="operation", label=operation_id)
        operation.update({
            "status": "succeeded",
            "completedAt": _now(),
        })
        if ai_run_id:
            operation["aiRunId"] = ai_run_id
        if notes:
            operation["notes"] = notes
        if self._current_operation_id == operation_id:
            self._current_operation_id = None
        self._persist("running")

    def fail_operation(
        self,
        operation_id: str,
        error: str,
        *,
        ai_run_id: str | None = None,
        notes: list[str] | None = None,
    ) -> None:
        operation = self._find_or_create(operation_id, kind="operation", label=operation_id)
        operation.update({
            "status": "failed",
            "completedAt": _now(),
            "error": _safe(error),
        })
        if ai_run_id:
            operation["aiRunId"] = ai_run_id
        if notes:
            operation["notes"] = notes
        if self._current_operation_id == operation_id:
            self._current_operation_id = None
        self._persist("running")

    def payload(self, status: str | None = None) -> dict[str, Any]:
        progress_status = status or ("running" if self._current_operation_id else _aggregate_status(self._operations))
        return {
            "status": progress_status,
            "currentOperationId": self._current_operation_id,
            "operations": [dict(operation) for operation in self._operations],
            "budget": {
                "staleAfterSeconds": 300,
                "longOperationWarningSeconds": 120,
                "operationCount": len(self._operations),
                "expectedOperationCount": self._total_operations,
            },
        }

    def _find_or_create(self, operation_id: str, *, kind: str, label: str, target: str | None = None) -> dict[str, Any]:
        for operation in self._operations:
            if operation["id"] == operation_id:
                return operation
        operation = {
            "id": operation_id,
            "kind": kind,
            "label": label,
            "status": "pending",
            "startedAt": None,
            "completedAt": None,
        }
        if target:
            operation["target"] = _safe(target, 300)
        self._operations.append(operation)
        return operation

    def _persist(self, status: str) -> None:
        self._repository.set_step_status(
            self._run_id,
            self._step_key,
            DraftRunStepStatus.RUNNING,
            artifact_payload={"progress": self.payload(status)},
        )


def with_progress_payload(artifact_payload: dict[str, Any], progress: DraftRunStepOperationSink | None) -> dict[str, Any]:
    if progress is None:
        return artifact_payload
    return {**artifact_payload, "progress": progress.payload("succeeded")}


def _aggregate_status(operations: list[dict[str, Any]]) -> str:
    if not operations:
        return "running"
    if any(operation.get("status") == "failed" for operation in operations):
        return "failed"
    if all(operation.get("status") == "succeeded" for operation in operations):
        return "succeeded"
    return "running"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _safe(value: str, limit: int = 500) -> str:
    return " ".join(str(value).split())[:limit]
