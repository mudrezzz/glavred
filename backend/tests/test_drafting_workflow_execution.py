from typing import Any

from backend.app.application.draft_run_payloads import request_to_payload
from backend.app.domain.draft_run import DraftRunStatus, create_queued_draft_run
from backend.app.domain.draft_run_steps import DraftRunStepKey, DraftRunStepStatus
from backend.app.drafting.application.workflow.registry import DraftStepRegistry, DraftWorkflowPhase
from backend.app.drafting.application.workflow.state import DraftWorkflowState
from backend.app.drafting.application.workflow.workflow import DraftWorkflow
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_pipeline import make_request


def test_draft_workflow_executes_registered_phases_in_order(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    run = _save_run(repository)
    events: list[str] = []

    def context_phase(state: DraftWorkflowState) -> None:
        events.append(f"context:{state.request.brief.id}")
        state.progress.complete(DraftRunStepKey.CONTEXT, {"status": "ok"})

    def complete_phase(state: DraftWorkflowState) -> None:
        events.append("complete")
        state.progress.complete(DraftRunStepKey.COMPLETE, {"status": "succeeded"})
        repository.set_run_status(state.run_id, DraftRunStatus.SUCCEEDED)

    result = DraftWorkflow(
        repository,
        DraftStepRegistry(
            [
                DraftWorkflowPhase("context", (DraftRunStepKey.CONTEXT,), context_phase),
                DraftWorkflowPhase("complete", (DraftRunStepKey.COMPLETE,), complete_phase),
            ]
        ),
    ).execute(run.id)

    assert events == ["context:brief-demo", "complete"]
    assert result.status == DraftRunStatus.SUCCEEDED
    assert _step(result, DraftRunStepKey.CONTEXT).artifact_payload == {"status": "ok"}


def test_draft_workflow_stops_after_blocked_phase(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    run = _save_run(repository)
    events: list[str] = []

    def blocked_phase(state: DraftWorkflowState) -> None:
        events.append("blocked")
        state.progress.complete(DraftRunStepKey.COMPLETE, {"status": "blocked"})
        repository.set_run_status(state.run_id, DraftRunStatus.SUCCEEDED, ai_run_ids=[])
        state.stop("blocked")

    def should_not_run(_: DraftWorkflowState) -> None:
        events.append("unexpected")

    result = DraftWorkflow(
        repository,
        DraftStepRegistry(
            [
                DraftWorkflowPhase("blocked", (DraftRunStepKey.COMPLETE,), blocked_phase),
                DraftWorkflowPhase("later", (DraftRunStepKey.DRAFT,), should_not_run),
            ]
        ),
    ).execute(run.id)

    assert events == ["blocked"]
    assert result.status == DraftRunStatus.SUCCEEDED
    assert _step(result, DraftRunStepKey.COMPLETE).artifact_payload == {"status": "blocked"}


def test_draft_workflow_failure_marks_current_step_and_parent_run_failed(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    run = _save_run(repository)

    def failing_phase(state: DraftWorkflowState) -> None:
        state.progress.start(DraftRunStepKey.CONTEXT)
        raise RuntimeError("provider exploded")

    result = DraftWorkflow(
        repository,
        DraftStepRegistry(
            [DraftWorkflowPhase("context", (DraftRunStepKey.CONTEXT,), failing_phase)]
        ),
    ).execute(run.id)

    context_step = _step(result, DraftRunStepKey.CONTEXT)
    assert result.status == DraftRunStatus.FAILED
    assert result.error == "provider exploded"
    assert context_step.status == DraftRunStepStatus.FAILED
    assert context_step.error == "provider exploded"


def _save_run(repository: SqliteDraftRunRepository) -> Any:
    request = make_request()
    run = create_queued_draft_run(
        request_payload=request_to_payload(request),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)
    return run


def _step(run: Any, key: DraftRunStepKey) -> Any:
    return next(step for step in run.steps if step.key == key)
