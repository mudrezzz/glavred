from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.settings import BackendSettings


def make_client(tmp_path) -> TestClient:
    return TestClient(
        create_app(
            settings=BackendSettings(
                _env_file=None,
                OPENROUTER_API_KEY="secret-token",
                OPENROUTER_DEFAULT_MODEL="openrouter/test-model",
                AI_RUN_AUDIT_DB_PATH=str(tmp_path / "audit.sqlite3"),
            )
        )
    )


def test_create_and_read_ai_run_without_exposing_secret(tmp_path) -> None:
    client = make_client(tmp_path)

    create_response = client.post(
        "/api/ai-runs",
        json={
            "capability": "draftGeneration",
            "provider": "openrouter",
            "model": "openrouter/test-model",
            "requestPayload": {
                "brief": "Write from approved brief",
                "providerToken": "secret-token",
            },
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["status"] == "recorded"
    assert created["requestPayload"]["providerToken"] == "[redacted]"
    assert "secret-token" not in create_response.text

    read_response = client.get(f"/api/ai-runs/{created['id']}")

    assert read_response.status_code == 200
    assert read_response.json()["id"] == created["id"]


def test_list_ai_runs_with_capability_filter(tmp_path) -> None:
    client = make_client(tmp_path)
    client.post(
        "/api/ai-runs",
        json={
            "capability": "documentImport",
            "provider": "none",
            "model": None,
            "requestPayload": {"document": "archive"},
        },
    )
    draft_response = client.post(
        "/api/ai-runs",
        json={
            "capability": "draftGeneration",
            "provider": "deterministic",
            "model": None,
            "requestPayload": {"brief": "demo"},
        },
    )

    response = client.get("/api/ai-runs?limit=20&capability=draftGeneration")

    assert response.status_code == 200
    assert [run["id"] for run in response.json()] == [draft_response.json()["id"]]


def test_get_missing_ai_run_returns_404(tmp_path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/ai-runs/missing")

    assert response.status_code == 404


def test_health_reports_ai_run_audit_without_local_path(tmp_path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["aiRunAudit"] == {"configured": True, "storage": "sqlite"}
    assert str(tmp_path) not in response.text
