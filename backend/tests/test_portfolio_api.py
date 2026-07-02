from pathlib import Path

from backend.tests.portfolio_test_helpers import login_portfolio, portfolio_client


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

    assert ai_project["language"] == "ru"
    assert "Industrial AI" in ai_project["description"]
    assert "ТОиР" in ai_project["description"]
    assert "Decision Intelligence" in ai_project["description"]
