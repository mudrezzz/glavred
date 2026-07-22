import json
import sqlite3
from pathlib import Path

from backend.app.infrastructure.sqlite_portfolio_repository import SQLitePortfolioRepository
from backend.app.portfolio.application.workspace_recovery import WorkspaceRecoveryService
from backend.tests.portfolio_test_helpers import portfolio_client


def test_recovery_dry_run_reports_preserved_and_reset_projects(tmp_path: Path) -> None:
    portfolio_client(tmp_path)
    database_path = tmp_path / "portfolio.sqlite3"
    repository = SQLitePortfolioRepository(database_path)
    repository.ensure_seeded()
    repository.save_workspace_snapshot(
        "project-ai-design-patterns",
        {"title": "ÃÂÃÂÃÂ¸ÃÂ²ÃÂµÃÂ"},
    )

    result = WorkspaceRecoveryService().recover_demo_project(
        database_path,
        project_id="project-ai-design-patterns",
        backup_dir=tmp_path / "recovery",
        apply=False,
    )

    assert result.applied is False
    assert result.reset_project_ids == ("project-ai-design-patterns",)
    assert set(result.preserved_project_ids) == {"project-glavred-blog", "project-kasha-iz-topora"}
    assert result.backup_path is None


def test_recovery_atomically_resets_only_affected_project(tmp_path: Path) -> None:
    portfolio_client(tmp_path)
    database_path = tmp_path / "portfolio.sqlite3"
    repository = SQLitePortfolioRepository(database_path)
    repository.ensure_seeded()
    repository.save_workspace_snapshot("project-kasha-iz-topora", {"cleanNote": "Сохранить без изменений"})
    repository.save_workspace_snapshot(
        "project-ai-design-patterns",
        {"title": "РџСЂРёРІРµС‚ РџСЂРёРІРµС‚ РџСЂРёРІРµС‚"},
    )

    result = WorkspaceRecoveryService().recover_demo_project(
        database_path,
        project_id="project-ai-design-patterns",
        backup_dir=tmp_path / "recovery",
        apply=True,
    )

    assert result.applied is True
    assert result.source_integrity == "ok"
    assert result.recovered_integrity == "ok"
    assert result.backup_path and Path(result.backup_path).exists()
    assert result.backup_sha256 and len(result.backup_sha256) == 64

    recovered = SQLitePortfolioRepository(database_path)
    affected = recovered.latest_workspace_snapshot("project-ai-design-patterns")
    preserved = recovered.latest_workspace_snapshot("project-kasha-iz-topora")
    assert affected is not None and affected.payload["seedSource"] == "backend-dev-auth"
    assert affected.payload["projectProfile"]["name"] == "Опытный цех «Сборочная»"
    assert preserved is not None and preserved.payload == {"cleanNote": "Сохранить без изменений"}

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert connection.execute(
            "SELECT COUNT(*) FROM workspace_snapshots WHERE project_id = ?",
            ("project-ai-design-patterns",),
        ).fetchone()[0] == 1


def test_recovery_refuses_to_hide_another_corrupt_project(tmp_path: Path) -> None:
    portfolio_client(tmp_path)
    database_path = tmp_path / "portfolio.sqlite3"
    repository = SQLitePortfolioRepository(database_path)
    repository.ensure_seeded()
    repository.save_workspace_snapshot(
        "project-kasha-iz-topora",
        {"title": "ÃÂÃÂÃÂ¸ÃÂ²ÃÂµÃÂ"},
    )

    try:
        WorkspaceRecoveryService().recover_demo_project(
            database_path,
            project_id="project-ai-design-patterns",
            backup_dir=tmp_path / "recovery",
            apply=True,
        )
    except RuntimeError as exc:
        assert str(exc) == "additional-corrupt-project:project-kasha-iz-topora"
    else:
        raise AssertionError("Recovery must not discard an unlisted corrupt project.")

    with sqlite3.connect(database_path) as connection:
        payload = connection.execute(
            "SELECT payload FROM workspace_snapshots WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
            ("project-kasha-iz-topora",),
        ).fetchone()[0]
    assert "Ã" in json.loads(payload)["title"]
