"""Owner: drafting.application.operations

Used by: DraftRun staleness inspector to classify validation progress heartbeats.
Does not own: DraftRun API responses, repository updates, worker execution.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.domain.draft_run import DraftRun


class ValidationProgressStalenessInspector:
    def inspect(self, run: DraftRun, current_time: datetime, default_stale_after_seconds: int) -> tuple[bool, str | None, datetime] | None:
        for step in run.steps:
            if step.status.value != "running":
                continue
            if step.key.value != "validation":
                continue
            progress = step.artifact_payload.get("progress") if isinstance(step.artifact_payload, dict) else None
            if not isinstance(progress, dict):
                continue
            runtime_budget = progress.get("runtimeBudget") if isinstance(progress.get("runtimeBudget"), dict) else None
            budget = progress.get("budget") if isinstance(progress.get("budget"), dict) else {}
            stale_after = _int_value(
                (runtime_budget or {}).get("limits", {}).get("staleAfterSeconds") if isinstance((runtime_budget or {}).get("limits"), dict) else None,
                budget.get("staleAfterSeconds"),
                default_stale_after_seconds,
            )
            current_operation_id = progress.get("currentOperationId") or (runtime_budget or {}).get("currentOperationId")
            current_started = _parse_datetime((runtime_budget or {}).get("currentOperationStartedAt"))
            last_heartbeat = _parse_datetime((runtime_budget or {}).get("lastHeartbeatAt")) or current_started or run.updated_at
            if current_operation_id and current_started:
                operation_age = (current_time - current_started).total_seconds()
                if operation_age <= stale_after:
                    return False, None, last_heartbeat
                return True, f"Validation operation {current_operation_id} has no progress for more than {stale_after} seconds.", last_heartbeat
            if (current_time - last_heartbeat).total_seconds() <= stale_after:
                return False, None, last_heartbeat
        return None


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
