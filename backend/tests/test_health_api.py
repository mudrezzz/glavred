from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.settings import BackendSettings


def test_liveness_health_response() -> None:
    client = TestClient(
        create_app(
            settings=BackendSettings(
                _env_file=None,
                OPENROUTER_API_KEY="",
                OPENROUTER_DEFAULT_MODEL="",
            )
        )
    )

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "glavred-backend",
        "environment": "local",
    }


def test_api_health_reports_openrouter_without_exposing_secret() -> None:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="secret-token",
        OPENROUTER_DEFAULT_MODEL="openrouter/test-model",
    )
    client = TestClient(create_app(settings=settings))

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["openRouter"] == {
        "configured": True,
        "baseUrl": "https://openrouter.ai/api/v1",
        "defaultModelConfigured": True,
        "appNameConfigured": True,
        "httpRefererConfigured": True,
    }
    assert "secret-token" not in response.text


def test_api_health_handles_missing_openrouter_token() -> None:
    client = TestClient(
        create_app(
            settings=BackendSettings(
                _env_file=None,
                OPENROUTER_API_KEY="",
                OPENROUTER_DEFAULT_MODEL="",
            )
        )
    )

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["openRouter"]["configured"] is False
