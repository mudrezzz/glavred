from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.settings import BackendSettings


def _client(tmp_path: Path) -> TestClient:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="",
        OPENROUTER_DEFAULT_MODEL="",
        PORTFOLIO_DB_PATH=tmp_path / "portfolio.sqlite3",
        GLAVRED_DEV_AUTH_PASSWORD="secret-demo",
    )
    return TestClient(create_app(settings=settings))


def _login(client: TestClient, email: str) -> None:
    response = client.post("/api/auth/login", json={"email": email, "password": "secret-demo"})
    assert response.status_code == 200
    assert "glavred_session" in response.headers["set-cookie"]


def test_login_succeeds_for_seeded_user_and_sets_cookie(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.post(
        "/api/auth/login",
        json={"email": "founder@example.test", "password": "secret-demo"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "founder@example.test"
    assert "HttpOnly" in response.headers["set-cookie"]


def test_login_rejects_wrong_password_without_session(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.post(
        "/api/auth/login",
        json={"email": "founder@example.test", "password": "wrong"},
    )

    assert response.status_code == 401
    assert "set-cookie" not in response.headers


def test_me_requires_valid_session(tmp_path: Path) -> None:
    client = _client(tmp_path)

    assert client.get("/api/users/me").status_code == 401
    _login(client, "founder@example.test")

    response = client.get("/api/users/me")

    assert response.status_code == 200
    assert response.json()["user"]["id"] == "user-founder-editor"


def test_project_list_is_membership_scoped(tmp_path: Path) -> None:
    founder = _client(tmp_path)
    _login(founder, "founder@example.test")

    founder_projects = founder.get("/api/projects").json()["projects"]

    assert [item["project"]["id"] for item in founder_projects] == [
        "project-ai-design-patterns",
        "project-kasha-iz-topora",
    ]

    editor = _client(tmp_path)
    _login(editor, "glavred-editor@example.test")

    editor_projects = editor.get("/api/projects").json()["projects"]

    assert [item["project"]["id"] for item in editor_projects] == ["project-glavred-blog"]


def test_user_cannot_load_or_save_another_user_project(tmp_path: Path) -> None:
    client = _client(tmp_path)
    _login(client, "founder@example.test")

    assert client.get("/api/projects/project-glavred-blog/workspace").status_code == 403

    response = client.put(
        "/api/projects/project-glavred-blog/workspace",
        json={"workspace": {"projectProfile": {"name": "leak"}}},
    )

    assert response.status_code == 403


def test_workspace_snapshot_roundtrip_preserves_project_isolation(tmp_path: Path) -> None:
    client = _client(tmp_path)
    _login(client, "founder@example.test")

    payload = {"projectProfile": {"name": "AI Design Patterns edited"}, "authorNotes": []}
    save_response = client.put("/api/projects/project-ai-design-patterns/workspace", json={"workspace": payload})

    assert save_response.status_code == 200
    assert save_response.json()["workspace"] == payload
    assert client.get("/api/projects/project-ai-design-patterns/workspace").json()["workspace"] == payload

    other_workspace = client.get("/api/projects/project-kasha-iz-topora/workspace").json()["workspace"]
    assert other_workspace["projectProfile"]["name"] == "Каша из топора"


def test_seed_is_idempotent_and_logout_invalidates_session(tmp_path: Path) -> None:
    client = _client(tmp_path)
    _login(client, "founder@example.test")
    assert len(client.get("/api/projects").json()["projects"]) == 2
    assert len(client.get("/api/projects").json()["projects"]) == 2

    logout = client.post("/api/auth/logout")

    assert logout.status_code == 200
    assert client.get("/api/users/me").status_code == 401
