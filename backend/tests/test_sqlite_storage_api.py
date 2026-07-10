from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.settings import BackendSettings


def test_draft_run_malformed_storage_returns_controlled_diagnostic(tmp_path) -> None:
    db_path = tmp_path / "draft-runs.sqlite3"
    db_path.write_bytes(b"not a sqlite database")
    client = TestClient(
        create_app(settings=BackendSettings(_env_file=None, DRAFT_RUN_DB_PATH=str(db_path)))
    )

    response = client.get("/api/draft-runs/missing")

    assert response.status_code == 503
    payload = response.json()["detail"]
    assert payload["code"] == "sqliteDatabaseMalformed"
    assert payload["storage"] == "draft-runs.sqlite3"
    assert str(tmp_path) not in response.text


def test_ai_run_malformed_storage_returns_controlled_diagnostic(tmp_path) -> None:
    db_path = tmp_path / "audit.sqlite3"
    db_path.write_bytes(b"not a sqlite database")
    client = TestClient(
        create_app(settings=BackendSettings(_env_file=None, AI_RUN_AUDIT_DB_PATH=str(db_path)))
    )

    response = client.get("/api/ai-runs/missing")

    assert response.status_code == 503
    payload = response.json()["detail"]
    assert payload["code"] == "sqliteDatabaseMalformed"
    assert payload["storage"] == "audit.sqlite3"
    assert str(tmp_path) not in response.text
