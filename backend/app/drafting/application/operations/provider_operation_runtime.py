"""Owner: drafting.application.operations

Used by: DraftRun step progress sinks for provider operation runtime diagnostics.
Does not own: provider transport, retry policy, persistence, or staleness decisions.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class ProviderOperationRuntimePresenter:
    """Builds trace-safe runtime fields for a currently running provider operation."""

    def start_operation(
        self,
        operation: dict[str, Any],
        *,
        operation_id: str,
        kind: str,
        model_role: str | None = None,
        selected_model: str | None = None,
        prompt_char_estimate: int | None = None,
        approx_token_estimate: int | None = None,
        stale_after_seconds: int | None = None,
    ) -> None:
        operation.update(
            {
                "id": operation_id,
                "kind": kind,
                "operationKind": kind,
                "status": "running",
                "startedAt": operation.get("startedAt") or _now(),
                "completedAt": None,
            }
        )
        if model_role:
            operation["modelRole"] = model_role
        if selected_model:
            operation["selectedModel"] = selected_model
        if prompt_char_estimate is not None:
            operation["promptCharEstimate"] = max(0, int(prompt_char_estimate))
            operation["approxTokenEstimate"] = max(0, int(approx_token_estimate or prompt_char_estimate // 4))
        if stale_after_seconds is not None:
            operation["staleAfterSeconds"] = max(1, int(stale_after_seconds))

    def operation_progress_fields(
        self,
        operation: dict[str, Any] | None,
        *,
        default_stale_after_seconds: int,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        if not operation:
            return {}
        current_time = now or datetime.now(UTC)
        started = _parse_datetime(operation.get("startedAt"))
        stale_after = _int_value(operation.get("staleAfterSeconds"), default_stale_after_seconds)
        wait_seconds = int((current_time - started).total_seconds()) if started else 0
        return {
            "currentOperationStartedAt": started.isoformat() if started else operation.get("startedAt"),
            "operationKind": operation.get("operationKind") or operation.get("kind"),
            "modelRole": operation.get("modelRole"),
            "selectedModel": operation.get("selectedModel"),
            "promptCharEstimate": operation.get("promptCharEstimate"),
            "approxTokenEstimate": operation.get("approxTokenEstimate"),
            "staleAfterSeconds": stale_after,
            "providerWaitSeconds": max(0, wait_seconds),
            "slowButHealthy": bool(started and wait_seconds <= stale_after),
        }


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _int_value(*values: Any) -> int:
    for value in values:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            continue
        if parsed > 0:
            return parsed
    return 300


def _now() -> str:
    return datetime.now(UTC).isoformat()
