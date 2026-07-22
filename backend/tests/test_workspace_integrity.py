from pathlib import Path

from backend.app.infrastructure.sqlite_portfolio_repository import SQLitePortfolioRepository
from backend.app.portfolio.application.workspace_integrity import WorkspaceTextIntegrityInspector
from backend.tests.portfolio_test_helpers import login_portfolio, portfolio_client


def test_valid_russian_and_mixed_text_are_accepted() -> None:
    payload = {
        "title": "Опытный цех «Сборочная» — AI и ТОиР",
        "url": "https://example.test/report?q=надежность&lang=ru",
        "body": "Роль системы — объяснять ограничения, а не обещать магию.",
    }

    report = WorkspaceTextIntegrityInspector().inspect(payload, project_id="project-test")

    assert report.is_clean
    assert report.issues == ()


def test_mojibake_replacement_and_question_mark_runs_are_rejected() -> None:
    payload = {
        "latin": "ÃÂÃÂÃÂ¸ÃÂ²ÃÂµÃÂ",
        "cyrillic": "РџСЂРёРІРµС‚ РџСЂРёРІРµС‚ РџСЂРёРІРµС‚",
        "replacement": "данные \ufffd потеряны",
        "questions": "industrial ???? evidence",
        "observed": "Public industrial AI cases, вЮша/EAM materials",
    }

    report = WorkspaceTextIntegrityInspector().inspect(payload, project_id="project-test")

    assert not report.is_clean
    assert {issue.code for issue in report.issues} == {
        "probable-mojibake",
        "unicode-replacement-character",
        "question-mark-replacement-text",
    }
    assert all(len(issue.value_hash) == 20 for issue in report.issues)


def test_path_aware_limit_rejects_an_excessive_query_but_allows_long_body() -> None:
    payload = {
        "searchPlan": {"queries": [{"query": "q" * 1_001}]},
        "draftBody": "т" * 20_000,
    }

    report = WorkspaceTextIntegrityInspector().inspect(payload, project_id="project-test")

    assert [issue.path for issue in report.issues] == ["$.searchPlan.queries[0].query"]
    assert report.issues[0].code == "text-field-too-large"


def test_api_rejects_corrupt_save_without_creating_snapshot(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "founder@example.test")
    repository = SQLitePortfolioRepository(tmp_path / "portfolio.sqlite3")
    before = repository.latest_workspace_snapshot("project-ai-design-patterns")

    response = client.put(
        "/api/projects/project-ai-design-patterns/workspace",
        json={"workspace": {"title": "ÃÂÃÂÃÂ¸ÃÂ²ÃÂµÃÂ"}},
    )

    after = repository.latest_workspace_snapshot("project-ai-design-patterns")
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "workspace-text-integrity-failed"
    assert response.json()["detail"]["operation"] == "save"
    assert before is not None and after is not None and before.id == after.id
    assert response.headers["content-type"] == "application/json; charset=utf-8"


def test_api_returns_controlled_conflict_for_corrupt_stored_snapshot(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "founder@example.test")
    repository = SQLitePortfolioRepository(tmp_path / "portfolio.sqlite3")
    repository.save_workspace_snapshot(
        "project-ai-design-patterns",
        {"title": "РџСЂРёРІРµС‚ РџСЂРёРІРµС‚ РџСЂРёРІРµС‚"},
    )

    response = client.get("/api/projects/project-ai-design-patterns/workspace")

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "workspace-text-integrity-failed"
    assert detail["operation"] == "read"
    assert detail["snapshotId"].startswith("snapshot-project-ai-design-patterns-")
    assert "Рџ" not in response.text


def test_ten_api_roundtrips_preserve_russian_text(tmp_path: Path) -> None:
    client = portfolio_client(tmp_path)
    login_portfolio(client, "founder@example.test")
    payload = {
        "projectProfile": {"name": "Опытный цех «Сборочная»"},
        "note": "Проверяем ТОиР, AI, кавычки «ёлочки» и длинное тире — без потерь.",
    }

    for _ in range(10):
        saved = client.put(
            "/api/projects/project-ai-design-patterns/workspace",
            json={"workspace": payload},
        )
        assert saved.status_code == 200
        payload = client.get("/api/projects/project-ai-design-patterns/workspace").json()["workspace"]

    assert payload["projectProfile"]["name"] == "Опытный цех «Сборочная»"
    assert payload["note"] == "Проверяем ТОиР, AI, кавычки «ёлочки» и длинное тире — без потерь."
