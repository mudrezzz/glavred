"""Owner: drafting.application.operations

Used by: DraftRun progress sink when validation runtime guard is attached.
Does not own: generic step progress persistence, repository writes, UI rendering.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from datetime import UTC, datetime
from typing import Any

from backend.app.drafting.application.operations.validation_runtime_budget import ValidationRuntimeGuard


class ValidationProgressRuntimePresenter:
    def start_runtime_operation(
        self,
        guard: ValidationRuntimeGuard | None,
        operation: dict[str, Any],
        *,
        operation_id: str,
        kind: str,
        notes: list[str] | None,
    ) -> bool:
        allowed = guard.start_operation(operation_id, kind) if guard else True
        operation.update({
            "status": "running" if allowed else "skipped",
            "startedAt": operation.get("startedAt") or _now(),
            "completedAt": None if allowed else _now(),
        })
        if notes:
            operation["notes"] = notes
        if not allowed:
            operation["notes"] = [*(operation.get("notes") or []), "runtime-budget-exhausted"]
        return allowed

    def runtime_progress_budget(
        self,
        guard: ValidationRuntimeGuard | None,
        *,
        operation_count: int,
        expected_operation_count: int | None,
    ) -> dict[str, Any]:
        return {
            "staleAfterSeconds": guard.profile.stale_after_seconds if guard else 300,
            "longOperationWarningSeconds": guard.profile.long_operation_warning_seconds if guard else 120,
            "operationCount": operation_count,
            "expectedOperationCount": expected_operation_count,
        }

    def attach_runtime_budget(self, payload: dict[str, Any], guard: ValidationRuntimeGuard | None) -> dict[str, Any]:
        if guard:
            payload["runtimeBudget"] = guard.snapshot()
        return payload


def _now() -> str:
    return datetime.now(UTC).isoformat()
