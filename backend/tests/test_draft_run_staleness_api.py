import sqlite3
from datetime import UTC, datetime, timedelta

from backend.tests.test_draft_run_api import RecordingDispatcher, make_client, make_payload


def test_get_draft_run_reports_fresh_running_run(tmp_path) -> None:
    client = make_client(tmp_path, RecordingDispatcher())
    created = client.post("/api/draft-runs", json=make_payload()).json()

    loaded = client.get(f"/api/draft-runs/{created['runId']}").json()

    assert loaded["isStale"] is False
    assert loaded["staleReason"] is None
    assert loaded["lastProgressAt"] == loaded["updatedAt"]


def test_get_draft_run_reports_stale_running_run(tmp_path) -> None:
    db_path = tmp_path / "draft-runs.sqlite3"
    client = make_client(tmp_path, RecordingDispatcher())
    created = client.post("/api/draft-runs", json=make_payload()).json()
    stale_timestamp = (datetime.now(UTC) - timedelta(minutes=7)).isoformat()
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "UPDATE draft_runs SET status = 'running', updated_at = ? WHERE id = ?",
            (stale_timestamp, created["runId"]),
        )

    loaded = client.get(f"/api/draft-runs/{created['runId']}").json()

    assert loaded["isStale"] is True
    assert loaded["staleReason"] == "No DraftRun progress for more than 5 minutes."
    assert loaded["lastProgressAt"] == stale_timestamp
