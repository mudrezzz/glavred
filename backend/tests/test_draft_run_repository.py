from datetime import UTC, datetime

from backend.app.domain.draft_run import (
    DraftRunStatus,
    DraftRunStepKey,
    DraftRunStepStatus,
    create_queued_draft_run,
)
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository


def test_draft_run_repository_creates_schema_and_persists_run(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    run = create_queued_draft_run(
        request_payload={"brief": {"id": "brief-1"}},
        input_summary={"title": "Demo"},
    )

    repository.save(run)
    loaded = repository.get(run.id)

    assert loaded is not None
    assert loaded.status == DraftRunStatus.QUEUED
    assert loaded.input_summary == {"title": "Demo"}
    assert [step.key for step in loaded.steps][0] == DraftRunStepKey.CONTEXT


def test_draft_run_repository_updates_step_and_final_draft(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    run = create_queued_draft_run(request_payload={"brief": {}}, input_summary={})
    repository.save(run)

    repository.set_run_status(run.id, DraftRunStatus.RUNNING)
    repository.set_step_status(run.id, DraftRunStepKey.CONTEXT, DraftRunStepStatus.RUNNING)
    repository.set_step_status(
        run.id,
        DraftRunStepKey.CONTEXT,
        DraftRunStepStatus.SUCCEEDED,
        artifact_payload={"summary": "ok", "at": datetime.now(UTC).isoformat()},
    )
    repository.set_run_status(
        run.id,
        DraftRunStatus.SUCCEEDED,
        final_draft={"id": "draft-1", "body": "done"},
    )

    loaded = repository.get(run.id)

    assert loaded is not None
    assert loaded.status == DraftRunStatus.SUCCEEDED
    assert loaded.final_draft == {"id": "draft-1", "body": "done"}
    assert loaded.steps[0].status == DraftRunStepStatus.SUCCEEDED
    assert loaded.steps[0].artifact_payload["summary"] == "ok"
