"""Owner: drafting.application.workflow

Used by: DraftRun API serialization and diagnostics to classify run freshness.
Does not own: worker execution, provider transport, queue architecture, or UI polling.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from backend.app.domain.draft_run import DraftRun, DraftRunStatus
from backend.app.drafting.application.operations.validation_staleness import ValidationProgressStalenessInspector

STALE_AFTER_SECONDS = 300


@dataclass(frozen=True)
class DraftRunStaleness:
    is_stale: bool
    stale_reason: str | None
    last_progress_at: datetime
    runtime_diagnostics: dict[str, Any]


class DraftRunStalenessInspector:
    """Classifies DraftRun queue/runtime freshness from structured artifacts."""

    def inspect(
        self,
        run: DraftRun,
        *,
        now: datetime | None = None,
    ) -> DraftRunStaleness:
        current_time = now or datetime.now(UTC)
        last_progress_at = run.updated_at
        if run.status not in {DraftRunStatus.QUEUED, DraftRunStatus.RUNNING}:
            return DraftRunStaleness(False, None, last_progress_at, {"state": "terminal"})
        if run.status == DraftRunStatus.QUEUED:
            return DraftRunStaleness(
                False,
                None,
                last_progress_at,
                {
                    "state": "queued",
                    "queueWaitSeconds": _elapsed_seconds(current_time, run.created_at),
                    "reason": "waiting-for-worker",
                },
            )

        progress_staleness = ValidationProgressStalenessInspector().inspect(run, current_time, STALE_AFTER_SECONDS)
        if progress_staleness is not None:
            is_stale, reason, progress_time = progress_staleness
            return DraftRunStaleness(
                is_stale,
                reason,
                progress_time,
                {
                    "state": "validation-runtime",
                    "slowButHealthy": not is_stale,
                    "staleReason": reason,
                },
            )

        provider_progress = self._provider_progress(run, current_time)
        if provider_progress is not None:
            is_stale = bool(provider_progress["isStale"])
            reason = str(provider_progress["staleReason"]) if is_stale else None
            return DraftRunStaleness(
                is_stale,
                reason,
                provider_progress["lastProgressAt"],
                provider_progress["diagnostics"],
            )

        elapsed_seconds = _elapsed_seconds(current_time, last_progress_at)
        if elapsed_seconds <= STALE_AFTER_SECONDS:
            return DraftRunStaleness(
                False,
                None,
                last_progress_at,
                {"state": "running", "secondsSinceLastProgress": elapsed_seconds},
            )
        return DraftRunStaleness(
            True,
            "No DraftRun progress for more than 5 minutes.",
            last_progress_at,
            {
                "state": "stale",
                "secondsSinceLastProgress": elapsed_seconds,
                "staleReason": "no-draftrun-progress",
            },
        )

    def _provider_progress(self, run: DraftRun, current_time: datetime) -> dict[str, Any] | None:
        running_step = next((step for step in run.steps if step.status.value == "running"), None)
        if running_step is None or not isinstance(running_step.artifact_payload, dict):
            return None
        progress = running_step.artifact_payload.get("progress")
        if not isinstance(progress, dict):
            return None
        operation_id = _str_value(progress.get("currentOperationId"))
        operation_started = _parse_datetime(progress.get("currentOperationStartedAt"))
        if not operation_id or operation_started is None:
            return None
        stale_after = _int_value(progress.get("staleAfterSeconds"), _dict(progress.get("budget")).get("staleAfterSeconds"), STALE_AFTER_SECONDS)
        provider_wait = _elapsed_seconds(current_time, operation_started)
        is_stale = provider_wait > stale_after
        operation_kind = _str_value(progress.get("operationKind")) or operation_id
        selected_model = _str_value(progress.get("selectedModel"))
        reason = (
            f"Provider operation {operation_id} ({selected_model or 'unknown model'}) has no progress for more than {stale_after} seconds."
            if is_stale
            else None
        )
        diagnostics = {
            "state": "provider-operation-stale" if is_stale else "provider-operation-running",
            "stepKey": running_step.key.value,
            "currentOperationId": operation_id,
            "operationKind": operation_kind,
            "currentOperationStartedAt": operation_started.isoformat(),
            "selectedModel": selected_model,
            "modelRole": _str_value(progress.get("modelRole")),
            "promptCharEstimate": progress.get("promptCharEstimate"),
            "approxTokenEstimate": progress.get("approxTokenEstimate"),
            "providerWaitSeconds": provider_wait,
            "staleAfterSeconds": stale_after,
            "slowButHealthy": not is_stale,
            "staleReason": reason,
        }
        return {
            "isStale": is_stale,
            "staleReason": reason,
            "lastProgressAt": operation_started,
            "diagnostics": diagnostics,
        }


def inspect_draft_run_staleness(
    run: DraftRun,
    *,
    now: datetime | None = None,
) -> DraftRunStaleness:
    return DraftRunStalenessInspector().inspect(run, now=now)


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
    return STALE_AFTER_SECONDS


def _elapsed_seconds(current_time: datetime, previous_time: datetime) -> int:
    return max(0, int((current_time - previous_time).total_seconds()))


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _str_value(value: Any) -> str | None:
    if value in {None, ""}:
        return None
    return str(value)
