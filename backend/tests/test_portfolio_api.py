from pathlib import Path
import sqlite3

from backend.tests.portfolio_test_helpers import login_portfolio, portfolio_client


def test_workspace_latest_snapshot_lookup_has_covering_index(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "founder@example.test")

    with sqlite3.connect(tmp_path / "portfolio.sqlite3") as connection:
        index = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'index' AND name = ?",
            ("idx_workspace_snapshots_project_latest",),
        ).fetchone()

    assert index is not None
    assert "project_id, created_at DESC, id DESC" in index[0]


def test_portfolio_components_are_reused_across_requests(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "founder@example.test")
    repository = client.app.state.portfolio_repository
    auth_service = client.app.state.portfolio_auth_service

    assert client.get("/api/users/me").status_code == 200
    assert client.get("/api/projects?includeArchived=true").status_code == 200

    assert client.app.state.portfolio_repository is repository
    assert client.app.state.portfolio_auth_service is auth_service
    assert client.app.state.portfolio_service is not None


def test_login_succeeds_for_seeded_user_and_sets_cookie(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)

    response = client.post(
        "/api/auth/login",
        json={"email": "founder@example.test", "password": "secret-demo"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "founder@example.test"
    assert "HttpOnly" in response.headers["set-cookie"]


def test_login_rejects_wrong_password_without_session(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)

    response = client.post(
        "/api/auth/login",
        json={"email": "founder@example.test", "password": "wrong"},
    )

    assert response.status_code == 401
    assert "set-cookie" not in response.headers


def test_me_requires_valid_session(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)

    assert client.get("/api/users/me").status_code == 401
    login_portfolio(client, "founder@example.test")

    response = client.get("/api/users/me")

    assert response.status_code == 200
    assert response.json()["user"]["id"] == "user-founder-editor"


def test_seed_is_idempotent_and_logout_invalidates_session(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "founder@example.test")
    assert len(client.get("/api/projects").json()["projects"]) == 2
    assert len(client.get("/api/projects").json()["projects"]) == 2

    logout = client.post("/api/auth/logout")

    assert logout.status_code == 200
    assert client.get("/api/users/me").status_code == 401


def test_seeded_ai_design_patterns_project_matches_current_industrial_baseline(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "founder@example.test")

    projects = client.get("/api/projects?includeArchived=true").json()["projects"]
    ai_project = next(item["project"] for item in projects if item["project"]["id"] == "project-ai-design-patterns")

    assert ai_project["title"] == "Опытный цех «Сборочная»"
    assert ai_project["language"] == "ru"
    assert "industrial AI patterns" in ai_project["description"]
    assert "ТОиР" in ai_project["description"]
    assert "Decision Intelligence" in ai_project["description"]


def test_seeded_severnaya_stena_project_matches_current_baseline(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "founder@example.test")

    projects = client.get("/api/projects?includeArchived=true").json()["projects"]
    project = next(item["project"] for item in projects if item["project"]["id"] == "project-kasha-iz-topora")

    assert project["title"] == "Северная стена"
    assert project["language"] == "ru"
    assert "complex B2B deal routes" in project["description"]
    assert "RevOps" in project["description"]
    assert "lost route analysis" in project["description"]


def test_seeded_glavred_blog_project_matches_current_baseline(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "glavred-editor@example.test")

    projects = client.get("/api/projects?includeArchived=true").json()["projects"]
    project = next(item["project"] for item in projects if item["project"]["id"] == "project-glavred-blog")

    assert project["title"] == "Главред: быть интересным"
    assert project["language"] == "ru"
    assert "author voice" in project["description"]
    assert "AI-assisted editorial systems" in project["description"]
    assert "practical content templates" in project["description"]
