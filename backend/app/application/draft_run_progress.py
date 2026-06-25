from typing import Any

from backend.app.application.draft_run_pipeline_ports import DraftRunPipelineRepository
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.domain.draft_run import DraftRunStatus
from backend.app.domain.draft_run_steps import DraftRunStepKey, DraftRunStepStatus


class DraftRunProgress:
    def __init__(self, repository: DraftRunPipelineRepository, run_id: str) -> None:
        self._repository = repository
        self._run_id = run_id
        self.ai_run_ids: list[str] = []
        self._current_step: DraftRunStepKey | None = None

    def complete(self, key: DraftRunStepKey, artifact_payload: dict[str, Any]) -> None:
        self.start(key)
        self.succeed(key, artifact_payload)

    def start(self, key: DraftRunStepKey) -> None:
        self._current_step = key
        self._repository.set_step_status(self._run_id, key, DraftRunStepStatus.RUNNING)

    def succeed(self, key: DraftRunStepKey, artifact_payload: dict[str, Any]) -> None:
        self._repository.set_step_status(
            self._run_id,
            key,
            DraftRunStepStatus.SUCCEEDED,
            artifact_payload=artifact_payload,
        )
        if self._current_step == key:
            self._current_step = None

    def add_ai_run_id(self, ai_run_id: str | None) -> None:
        if not ai_run_id or ai_run_id in self.ai_run_ids:
            return
        self.ai_run_ids.append(ai_run_id)
        self._repository.set_run_status(
            self._run_id,
            DraftRunStatus.RUNNING,
            ai_run_ids=self.ai_run_ids,
        )

    def add_ai_run_ids(self, ai_run_ids: list[str]) -> None:
        for ai_run_id in ai_run_ids:
            self.add_ai_run_id(ai_run_id)

    def operation_sink(
        self,
        key: DraftRunStepKey,
        *,
        total_operations: int | None = None,
    ) -> DraftRunStepOperationSink:
        return DraftRunStepOperationSink(
            self._repository,
            self._run_id,
            key,
            total_operations=total_operations,
        )

    def fail_current(self, error: str) -> None:
        if self._current_step is None:
            return
        self._repository.set_step_status(
            self._run_id,
            self._current_step,
            DraftRunStepStatus.FAILED,
            error=error,
        )
        self._current_step = None
