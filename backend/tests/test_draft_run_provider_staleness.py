import sqlite3
from datetime import UTC, datetime, timedelta

from backend.app.domain.draft_run import DraftRunStatus
from backend.app.domain.draft_run_steps import DraftRunStepKey, DraftRunStepStatus
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_api import RecordingDispatcher, make_client, make_payload


def test_get_draft_run_does_not_report_old_queued_run_as_generic_stale(tmp_path) -> None:
    db_path = tmp_path / "draft-runs.sqlite3"
    client = make_client(tmp_path, RecordingDispatcher())
    created = client.post("/api/draft-runs", json=make_payload()).json()
    stale_timestamp = (datetime.now(UTC) - timedelta(minutes=20)).isoformat()
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE draft_runs SET status = 'queued', updated_at = ? WHERE id = ?",
            (stale_timestamp, created["runId"]),
        )

    loaded = client.get(f"/api/draft-runs/{created['runId']}").json()

    assert loaded["isStale"] is False
    assert loaded["staleReason"] is None
    assert loaded["lastProgressAt"] == stale_timestamp


def test_get_draft_run_treats_provider_operation_inside_budget_as_fresh(tmp_path) -> None:
    db_path = tmp_path / "draft-runs.sqlite3"
    client = make_client(tmp_path, RecordingDispatcher())
    created = client.post("/api/draft-runs", json=make_payload()).json()
    current_started = (datetime.now(UTC) - timedelta(minutes=5)).isoformat()
    _set_provider_progress(db_path, created["runId"], current_started, stale_after_seconds=900)

    loaded = client.get(f"/api/draft-runs/{created['runId']}").json()

    assert loaded["isStale"] is False
    assert loaded["staleReason"] is None
    assert loaded["lastProgressAt"] == current_started


def test_get_draft_run_reports_provider_operation_over_budget_as_stale(tmp_path) -> None:
    db_path = tmp_path / "draft-runs.sqlite3"
    client = make_client(tmp_path, RecordingDispatcher())
    created = client.post("/api/draft-runs", json=make_payload()).json()
    old_started = (datetime.now(UTC) - timedelta(minutes=20)).isoformat()
    _set_provider_progress(db_path, created["runId"], old_started, stale_after_seconds=300)

    loaded = client.get(f"/api/draft-runs/{created['runId']}").json()

    assert loaded["isStale"] is True
    assert loaded["staleReason"] == "Provider operation materialPlan (z-ai/glm-5.2) has no progress for more than 300 seconds."
    assert loaded["lastProgressAt"] == old_started


def _set_provider_progress(db_path, run_id: str, started_at: str, *, stale_after_seconds: int) -> None:
    repository = SqliteDraftRunRepository(db_path)
    repository.set_run_status(run_id, DraftRunStatus.RUNNING)
    repository.set_step_status(
        run_id,
        DraftRunStepKey.MATERIAL_PLAN,
        DraftRunStepStatus.RUNNING,
        artifact_payload={
            "progress": {
                "status": "running",
                "currentOperationId": "materialPlan",
                "currentOperationStartedAt": started_at,
                "operationKind": "materialPlan",
                "modelRole": "strategy",
                "selectedModel": "z-ai/glm-5.2",
                "promptCharEstimate": 346264,
                "approxTokenEstimate": 86566,
                "staleAfterSeconds": stale_after_seconds,
                "operations": [{
                    "id": "materialPlan",
                    "kind": "materialPlan",
                    "status": "running",
                    "startedAt": started_at,
                    "selectedModel": "z-ai/glm-5.2",
                    "staleAfterSeconds": stale_after_seconds,
                }],
                "budget": {"staleAfterSeconds": stale_after_seconds},
            }
        },
    )
