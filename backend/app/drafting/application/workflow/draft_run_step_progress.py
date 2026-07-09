"""Owner: DraftRun workflow progress.

Used by: DraftRunProgress and provider-heavy DraftRun steps.
Does not own: provider calls, validation budget policy, or persisted run storage.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Callable

from backend.app.application.draft_run_pipeline_ports import DraftRunPipelineRepository
from backend.app.application.draft_run_step_progress_payload import step_artifact, with_progress
from backend.app.domain.draft_run_steps import DraftRunStepKey, DraftRunStepStatus
from backend.app.drafting.application.workflow.step_operation_progress_payload import (
    StepOperationProgressPayloadBuilder,
    aggregate_operation_status,
)

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
        self._payload_builder = StepOperationProgressPayloadBuilder(runtime_guard)

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
        model_role: str | None = None,
        selected_model: str | None = None,
        prompt_char_estimate: int | None = None,
        approx_token_estimate: int | None = None,
        stale_after_seconds: int | None = None,
    ) -> None:
        operation = self._find_or_create(operation_id, kind=kind, label=label, target=target)
        self._payload_builder.start_provider_runtime(
            operation,
            operation_id=operation_id,
            kind=kind,
            model_role=model_role,
            selected_model=selected_model,
            prompt_char_estimate=prompt_char_estimate,
            approx_token_estimate=approx_token_estimate,
            stale_after_seconds=stale_after_seconds,
        )
        allowed = self._payload_builder.start_validation_runtime(operation, operation_id=operation_id, kind=kind, notes=notes)
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
        progress_status = status or ("running" if self._current_operation_id else aggregate_operation_status(self._operations))
        current_operation = self._current_operation()
        return self._payload_builder.payload(
            status=progress_status,
            current_operation=current_operation,
            current_operation_id=self._current_operation_id,
            operations=self._operations,
            total_operations=self._total_operations,
        )

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

    def _current_operation(self) -> dict[str, Any] | None:
        if not self._current_operation_id:
            return None
        for operation in self._operations:
            if operation.get("id") == self._current_operation_id:
                return operation
        return None

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


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _safe(value: str, limit: int = 500) -> str:
    return " ".join(str(value).split())[:limit]
