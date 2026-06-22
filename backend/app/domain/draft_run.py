from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from backend.app.domain.draft_run_steps import (
    DRAFT_RUN_STEP_ORDER,
    STEP_TITLES,
    DraftRunStepKey,
    DraftRunStepStatus,
)


class DraftRunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class DraftRunStep:
    id: str
    run_id: str
    key: DraftRunStepKey
    status: DraftRunStepStatus
    title: str
    artifact_payload: dict[str, Any] | None
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
    sort_order: int


@dataclass(frozen=True)
class DraftRun:
    id: str
    status: DraftRunStatus
    request_payload: dict[str, Any]
    input_summary: dict[str, Any]
    final_draft: dict[str, Any] | None
    error: str | None
    ai_run_ids: list[str]
    created_at: datetime
    updated_at: datetime
    steps: list[DraftRunStep] = field(default_factory=list)


def create_queued_draft_run(
    *,
    request_payload: dict[str, Any],
    input_summary: dict[str, Any],
) -> DraftRun:
    now = datetime.now(UTC)
    run_id = str(uuid4())
    steps = [
        DraftRunStep(
            id=str(uuid4()),
            run_id=run_id,
            key=step_key,
            status=DraftRunStepStatus.PENDING,
            title=STEP_TITLES[step_key],
            artifact_payload=None,
            error=None,
            started_at=None,
            completed_at=None,
            sort_order=index,
        )
        for index, step_key in enumerate(DRAFT_RUN_STEP_ORDER)
    ]
    return DraftRun(
        id=run_id,
        status=DraftRunStatus.QUEUED,
        request_payload=request_payload,
        input_summary=input_summary,
        final_draft=None,
        error=None,
        ai_run_ids=[],
        created_at=now,
        updated_at=now,
        steps=steps,
    )
