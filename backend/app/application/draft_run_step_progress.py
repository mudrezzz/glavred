from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Callable

from backend.app.application.draft_run_pipeline_ports import DraftRunPipelineRepository
from backend.app.application.draft_run_step_progress_payload import step_artifact, with_progress
from backend.app.domain.draft_run_steps import DraftRunStepKey, DraftRunStepStatus
from backend.app.drafting.application.operations.validation_progress_runtime import attach_runtime_budget, runtime_progress_budget, start_runtime_operation

if TYPE_CHECKING:
    from backend.app.drafting.application.operations.validation_runtime_budget import ValidationRuntimeGuard


class DraftRunStepOperationSink:
    def __init__(
        self,
        repository: DraftRunPipelineRepository,
        run_id: str,
        step_key: DraftRunStepKey,
        *,
        total_operations: int | None = None,
        on_ai_run_id: Callable[[str | None], None] | None = None,
        runtime_guard: "ValidationRuntimeGuard | None" = None,
    ) -> None:
        self._repository = repository
        self._run_id = run_id
        self._step_key = step_key
        self._current_operation_id: str | None = None
        self._operations: list[dict[str, Any]] = []
        self._total_operations = total_operations
        self._on_ai_run_id = on_ai_run_id
        self._runtime_guard = runtime_guard

    @property
    def runtime_guard(self) -> "ValidationRuntimeGuard | None":
        return self._runtime_guard

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
        allowed = start_runtime_operation(self._runtime_guard, operation, operation_id=operation_id, kind=kind, notes=notes)
        self._current_operation_id = operation_id if allowed else None
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
        if self._runtime_guard:
            self._runtime_guard.complete_operation(operation_id)
        if ai_run_id:
            operation["aiRunId"] = ai_run_id
            self._record_ai_run_id(ai_run_id)
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
        if self._runtime_guard:
            self._runtime_guard.fail_operation(operation_id, _safe(error))
        if ai_run_id:
            operation["aiRunId"] = ai_run_id
            self._record_ai_run_id(ai_run_id)
        if notes:
            operation["notes"] = notes
        if self._current_operation_id == operation_id:
            self._current_operation_id = None
        self._persist("running")

    def payload(self, status: str | None = None) -> dict[str, Any]:
        progress_status = status or ("running" if self._current_operation_id else _aggregate_status(self._operations))
        return attach_runtime_budget({
            "status": progress_status,
            "currentOperationId": self._current_operation_id,
            "operations": [dict(operation) for operation in self._operations],
            "budget": runtime_progress_budget(self._runtime_guard, operation_count=len(self._operations), expected_operation_count=self._total_operations),
        }, self._runtime_guard)

    def merge_artifact(self, artifact_payload: dict[str, Any]) -> None:
        if self._runtime_guard:
            self._runtime_guard.heartbeat()
        self._persist("running", artifact_payload)

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

    def _persist(self, status: str, artifact_payload: dict[str, Any] | None = None) -> None:
        base = step_artifact(self._repository.get(self._run_id), self._step_key)
        if artifact_payload:
            base.update(artifact_payload)
        self._repository.set_step_status(
            self._run_id,
            self._step_key,
            DraftRunStepStatus.RUNNING,
            artifact_payload=with_progress(base, self.payload(status)),
        )

    def _record_ai_run_id(self, ai_run_id: str | None) -> None:
        if self._on_ai_run_id:
            self._on_ai_run_id(ai_run_id)
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
