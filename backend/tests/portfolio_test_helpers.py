from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.settings import BackendSettings


def portfolio_client(tmp_path: Path) -> TestClient:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="",
        OPENROUTER_DEFAULT_MODEL="",
        PORTFOLIO_DB_PATH=tmp_path / "portfolio.sqlite3",
        GLAVRED_DEV_AUTH_PASSWORD="secret-demo",
    )
    return TestClient(create_app(settings=settings))


def login_portfolio(client: TestClient, email: str) -> None:
    response = client.post("/api/auth/login", json={"email": email, "password": "secret-demo"})
    assert response.status_code == 200
    assert "glavred_session" in response.headers["set-cookie"]
