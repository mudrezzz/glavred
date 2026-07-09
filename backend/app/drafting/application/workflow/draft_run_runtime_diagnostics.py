"""Owner: drafting.application.workflow

Used by: DraftRun reliability diagnostics and live proof scripts.
Does not own: DraftRun execution, provider transport, or quality/fidelity verdicts.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.domain.draft_run import DraftRun
from backend.app.drafting.application.workflow.draft_run_staleness import DraftRunStalenessInspector


class DraftRunRuntimeDiagnostics:
    """Builds a trace-safe runtime-health payload for one DraftRun."""

    def to_payload(self, run: DraftRun, *, now: datetime | None = None) -> dict[str, Any]:
        current_time = now or datetime.now(UTC)
        staleness = DraftRunStalenessInspector().inspect(run, now=current_time)
        diagnostics = dict(staleness.runtime_diagnostics)
        running_step = next((step for step in run.steps if step.status.value == "running"), None)
        return {
            "runId": run.id,
            "status": run.status.value,
            "state": diagnostics.get("state"),
            "isStale": staleness.is_stale,
            "staleReason": staleness.stale_reason,
            "lastProgressAt": staleness.last_progress_at.isoformat(),
            "queueWaitSeconds": diagnostics.get("queueWaitSeconds"),
            "runningStepKey": running_step.key.value if running_step else None,
            "currentOperationId": diagnostics.get("currentOperationId"),
            "operationKind": diagnostics.get("operationKind"),
            "currentOperationStartedAt": diagnostics.get("currentOperationStartedAt"),
            "selectedModel": diagnostics.get("selectedModel"),
            "modelRole": diagnostics.get("modelRole"),
            "providerWaitSeconds": diagnostics.get("providerWaitSeconds"),
            "staleAfterSeconds": diagnostics.get("staleAfterSeconds"),
            "promptCharEstimate": diagnostics.get("promptCharEstimate"),
            "approxTokenEstimate": diagnostics.get("approxTokenEstimate"),
            "slowButHealthy": diagnostics.get("slowButHealthy"),
        }
