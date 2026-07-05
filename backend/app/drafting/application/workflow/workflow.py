"""Owner: drafting.application.workflow

Used by: DraftRunPipeline compatibility facade and future DraftRun workflow registry.
Does not own: step business logic, provider adapters, API request parsing, SQLite persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from backend.app.drafting.application.artifacts.draft_run_payloads import request_from_payload
from backend.app.application.draft_run_pipeline_ports import DraftRunPipelineRepository
from backend.app.application.draft_run_progress import DraftRunProgress
from backend.app.domain.draft_run import DraftRun, DraftRunStatus
from backend.app.drafting.application.workflow.registry import DraftStepRegistry
from backend.app.drafting.application.workflow.state import DraftWorkflowState


class DraftWorkflow:
    def __init__(self, repository: DraftRunPipelineRepository, registry: DraftStepRegistry) -> None:
        self._repository = repository
        self._registry = registry

    def execute(self, run_id: str) -> DraftRun:
        run = self._repository.get(run_id)
        if run is None:
            raise ValueError(f"DraftRun {run_id} not found")
        self._repository.set_run_status(run_id, DraftRunStatus.RUNNING)
        progress = DraftRunProgress(self._repository, run_id)
        state = DraftWorkflowState(
            run=run,
            request=request_from_payload(run.request_payload),
            progress=progress,
        )
        try:
            for phase in self._registry.phases:
                phase.execute(state)
                if state.stop_requested:
                    break
        except Exception as exc:
            safe_error = str(exc)[:500] or "Draft run failed"
            progress.fail_current(safe_error)
            self._repository.set_run_status(run_id, DraftRunStatus.FAILED, error=safe_error)
        return self._loaded(run_id)

    def _loaded(self, run_id: str) -> DraftRun:
        loaded = self._repository.get(run_id)
        if loaded is None:
            raise ValueError(f"DraftRun {run_id} disappeared")
        return loaded
