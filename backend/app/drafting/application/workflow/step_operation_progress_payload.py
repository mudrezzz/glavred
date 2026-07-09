"""Owner: drafting.application.workflow

Used by: DraftRunStepOperationSink to build step progress payloads.
Does not own: repository writes, provider calls, validation budget policy, or API serialization.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from backend.app.drafting.application.operations.provider_operation_runtime import ProviderOperationRuntimePresenter
from backend.app.drafting.application.operations.validation_progress_runtime import ValidationProgressRuntimePresenter

if TYPE_CHECKING:
    from backend.app.drafting.application.operations.validation_runtime_budget import ValidationRuntimeGuard


class StepOperationProgressPayloadBuilder:
    def __init__(self, runtime_guard: "ValidationRuntimeGuard | None") -> None:
        self._runtime_guard = runtime_guard
        self._validation_runtime = ValidationProgressRuntimePresenter()
        self._provider_runtime = ProviderOperationRuntimePresenter()

    def start_provider_runtime(
        self,
        operation: dict[str, Any],
        *,
        operation_id: str,
        kind: str,
        model_role: str | None,
        selected_model: str | None,
        prompt_char_estimate: int | None,
        approx_token_estimate: int | None,
        stale_after_seconds: int | None,
    ) -> None:
        self._provider_runtime.start_operation(
            operation,
            operation_id=operation_id,
            kind=kind,
            model_role=model_role,
            selected_model=selected_model,
            prompt_char_estimate=prompt_char_estimate,
            approx_token_estimate=approx_token_estimate,
            stale_after_seconds=stale_after_seconds,
        )

    def start_validation_runtime(
        self,
        operation: dict[str, Any],
        *,
        operation_id: str,
        kind: str,
        notes: list[str] | None,
    ) -> bool:
        return self._validation_runtime.start_runtime_operation(
            self._runtime_guard,
            operation,
            operation_id=operation_id,
            kind=kind,
            notes=notes,
        )

    def payload(
        self,
        *,
        status: str,
        current_operation: dict[str, Any] | None,
        current_operation_id: str | None,
        operations: list[dict[str, Any]],
        total_operations: int | None,
    ) -> dict[str, Any]:
        budget_payload = self._validation_runtime.runtime_progress_budget(
            self._runtime_guard,
            operation_count=len(operations),
            expected_operation_count=total_operations,
        )
        base = {
            "status": status,
            "currentOperationId": current_operation_id,
            **self._provider_runtime.operation_progress_fields(
                current_operation,
                default_stale_after_seconds=int(budget_payload.get("staleAfterSeconds") or 300),
            ),
            "operations": [dict(operation) for operation in operations],
            "budget": budget_payload,
        }
        return self._validation_runtime.attach_runtime_budget(base, self._runtime_guard)


def aggregate_operation_status(operations: list[dict[str, Any]]) -> str:
    if not operations:
        return "running"
    if any(operation.get("status") == "failed" for operation in operations):
        return "failed"
    if all(operation.get("status") == "succeeded" for operation in operations):
        return "succeeded"
    return "running"
