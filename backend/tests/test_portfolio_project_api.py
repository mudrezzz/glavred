from pathlib import Path

from backend.tests.portfolio_test_helpers import login_portfolio, portfolio_client


def test_project_list_is_membership_scoped(tmp_path: Path) -> None:
    founder = portfolio_client(tmp_path)
    login_portfolio(founder, "founder@example.test")

    founder_projects = founder.get("/api/projects").json()["projects"]

    assert [item["project"]["id"] for item in founder_projects] == [
        "project-ai-design-patterns",
        "project-kasha-iz-topora",
    ]

    editor = portfolio_client(tmp_path)
    login_portfolio(editor, "glavred-editor@example.test")

    editor_projects = editor.get("/api/projects").json()["projects"]

    assert [item["project"]["id"] for item in editor_projects] == ["project-glavred-blog"]


def test_project_create_rename_archive_and_include_archived(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "founder@example.test")

    create_response = client.post(
        "/api/projects",
        json={"title": "New benchmark blog", "description": "Private draft", "language": "en"},
    )

    assert create_response.status_code == 200
    project = create_response.json()["project"]
    project_id = project["id"]
    assert project["title"] == "New benchmark blog"
    workspace = client.get(f"/api/projects/{project_id}/workspace").json()["workspace"]
    assert workspace["projectProfile"]["name"] == "New benchmark blog"

    rename_response = client.patch(
        f"/api/projects/{project_id}",
        json={"title": "Renamed benchmark blog", "description": "Updated"},
    )

    assert rename_response.status_code == 200
    assert rename_response.json()["project"]["title"] == "Renamed benchmark blog"

    archive_response = client.patch(f"/api/projects/{project_id}", json={"status": "archived"})

    assert archive_response.status_code == 200
    active_ids = [item["project"]["id"] for item in client.get("/api/projects").json()["projects"]]
    all_ids = [
        item["project"]["id"]
        for item in client.get("/api/projects?includeArchived=true").json()["projects"]
    ]
    assert project_id not in active_ids
    assert project_id in all_ids


def test_user_cannot_load_save_rename_or_archive_another_user_project(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "founder@example.test")

    assert client.get("/api/projects/project-glavred-blog/workspace").status_code == 403
    save = client.put(
        "/api/projects/project-glavred-blog/workspace",
        json={"workspace": {"projectProfile": {"name": "leak"}}},
    )
    rename = client.patch("/api/projects/project-glavred-blog", json={"title": "Leak"})
    archive = client.patch("/api/projects/project-glavred-blog", json={"status": "archived"})

    assert save.status_code == 403
    assert rename.status_code == 403
    assert archive.status_code == 403


def test_workspace_snapshot_roundtrip_preserves_project_isolation(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "founder@example.test")

    payload = {"projectProfile": {"name": "Сборочная edited"}, "authorNotes": []}
    save_response = client.put("/api/projects/project-ai-design-patterns/workspace", json={"workspace": payload})

    assert save_response.status_code == 200
    assert save_response.json()["workspace"] == payload
    assert client.get("/api/projects/project-ai-design-patterns/workspace").json()["workspace"] == payload

    other_workspace = client.get("/api/projects/project-kasha-iz-topora/workspace").json()["workspace"]
    assert other_workspace["projectProfile"]["name"] == "Северная стена"
