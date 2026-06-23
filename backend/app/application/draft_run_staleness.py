from dataclasses import dataclass
from datetime import UTC, datetime

from backend.app.domain.draft_run import DraftRun, DraftRunStatus

STALE_AFTER_SECONDS = 300


@dataclass(frozen=True)
class DraftRunStaleness:
    is_stale: bool
    stale_reason: str | None
    last_progress_at: datetime


def inspect_draft_run_staleness(
    run: DraftRun,
    *,
    now: datetime | None = None,
) -> DraftRunStaleness:
    current_time = now or datetime.now(UTC)
    last_progress_at = run.updated_at
    if run.status not in {DraftRunStatus.QUEUED, DraftRunStatus.RUNNING}:
        return DraftRunStaleness(False, None, last_progress_at)
    elapsed_seconds = (current_time - last_progress_at).total_seconds()
    if elapsed_seconds <= STALE_AFTER_SECONDS:
        return DraftRunStaleness(False, None, last_progress_at)
    return DraftRunStaleness(
        True,
        "No DraftRun progress for more than 5 minutes.",
        last_progress_at,
    )
