from typing import Any, Protocol

from backend.app.domain.draft_run import DraftRun, DraftRunStatus, DraftRunStepKey, DraftRunStepStatus


class DraftRunPipelineRepository(Protocol):
    def get(self, run_id: str) -> DraftRun | None: ...

    def set_run_status(
        self,
        run_id: str,
        status: DraftRunStatus,
        *,
        error: str | None = None,
        final_draft: dict[str, Any] | None = None,
        ai_run_ids: list[str] | None = None,
    ) -> None: ...

    def set_step_status(
        self,
        run_id: str,
        key: DraftRunStepKey,
        status: DraftRunStepStatus,
        *,
        artifact_payload: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None: ...
