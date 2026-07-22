"""Owner: portfolio.application
Used by: local workspace recovery CLI after a confirmed semantic corruption incident.
Does not own: automatic text repair, product migrations, HTTP auth, or demo content semantics.
Architecture doc: docs/adr/2026-07-16-workspace-text-integrity-and-connected-ui-acceptance.md"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from backend.app.infrastructure.sqlite_portfolio_repository import SQLitePortfolioRepository
from backend.app.infrastructure.sqlite_portfolio_seed import seed_workspace
from backend.app.infrastructure.sqlite_runtime import SqliteConnectionFactory
from backend.app.portfolio.application.workspace_integrity import WorkspaceTextIntegrityInspector
@dataclass(frozen=True)
class WorkspaceRecoveryResult:
    database_path: str
    backup_path: str | None
    backup_sha256: str | None
    affected_project_id: str
    preserved_project_ids: tuple[str, ...]
    reset_project_ids: tuple[str, ...]
    source_integrity: str
    recovered_integrity: str
    applied: bool

    def to_payload(self) -> dict[str, object]:
        return {
            "databasePath": self.database_path,
            "backupPath": self.backup_path,
            "backupSha256": self.backup_sha256,
            "affectedProjectId": self.affected_project_id,
            "preservedProjectIds": list(self.preserved_project_ids),
            "resetProjectIds": list(self.reset_project_ids),
            "sourceIntegrity": self.source_integrity,
            "recoveredIntegrity": self.recovered_integrity,
            "applied": self.applied,
        }
class WorkspaceRecoveryService:
    _COPY_TABLES = ("users", "projects", "memberships")

    def __init__(self, inspector: WorkspaceTextIntegrityInspector | None = None) -> None:
        self._inspector = inspector or WorkspaceTextIntegrityInspector()

    def recover_demo_project(
        self,
        database_path: Path,
        *,
        project_id: str,
        backup_dir: Path,
        apply: bool,
    ) -> WorkspaceRecoveryResult:
        database_path = Path(database_path).resolve()
        if not database_path.exists():
            raise FileNotFoundError(database_path)
        source_integrity = self._integrity_check(database_path)
        if source_integrity.lower() != "ok":
            raise RuntimeError(f"source-sqlite-integrity-failed:{source_integrity}")

        project_rows, latest_snapshots = self._read_source(database_path)
        if project_id not in project_rows:
            raise ValueError(f"project-not-found:{project_id}")
        preserved: list[str] = []
        for candidate_id, snapshot in latest_snapshots.items():
            if candidate_id == project_id:
                continue
            report = self._inspector.inspect(
                snapshot["payload"],
                project_id=candidate_id,
                snapshot_id=snapshot["id"],
            )
            if not report.is_clean:
                raise RuntimeError(f"additional-corrupt-project:{candidate_id}")
            preserved.append(candidate_id)

        if not apply:
            return WorkspaceRecoveryResult(
                database_path=str(database_path),
                backup_path=None,
                backup_sha256=None,
                affected_project_id=project_id,
                preserved_project_ids=tuple(sorted(preserved)),
                reset_project_ids=(project_id,),
                source_integrity=source_integrity,
                recovered_integrity="not-run",
                applied=False,
            )

        backup_dir = Path(backup_dir).resolve()
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        backup_path = backup_dir / f"{database_path.stem}.{stamp}.corrupt{database_path.suffix}"
        shutil.copy2(database_path, backup_path)
        backup_hash = self._file_hash(backup_path)

        temporary_path = database_path.with_suffix(f"{database_path.suffix}.recovery.tmp")
        for path in (temporary_path, Path(f"{temporary_path}-wal"), Path(f"{temporary_path}-shm")):
            path.unlink(missing_ok=True)
        self._build_recovered_database(
            database_path,
            temporary_path,
            project_rows=project_rows,
            latest_snapshots=latest_snapshots,
            reset_project_id=project_id,
        )
        recovered_integrity = self._integrity_check(temporary_path)
        if recovered_integrity.lower() != "ok":
            temporary_path.unlink(missing_ok=True)
            raise RuntimeError(f"recovered-sqlite-integrity-failed:{recovered_integrity}")
        self._verify_recovered_workspaces(temporary_path)

        os.replace(temporary_path, database_path)
        Path(f"{database_path}-wal").unlink(missing_ok=True)
        Path(f"{database_path}-shm").unlink(missing_ok=True)
        return WorkspaceRecoveryResult(
            database_path=str(database_path),
            backup_path=str(backup_path),
            backup_sha256=backup_hash,
            affected_project_id=project_id,
            preserved_project_ids=tuple(sorted(preserved)),
            reset_project_ids=(project_id,),
            source_integrity=source_integrity,
            recovered_integrity=recovered_integrity,
            applied=True,
        )

    def _read_source(self, database_path: Path) -> tuple[dict[str, sqlite3.Row], dict[str, dict[str, Any]]]:
        uri = f"file:{database_path.as_posix()}?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as connection:
            connection.row_factory = sqlite3.Row
            project_rows = {row["id"]: row for row in connection.execute("SELECT * FROM projects")}
            latest_snapshots: dict[str, dict[str, Any]] = {}
            for project_id in project_rows:
                row = connection.execute(
                    "SELECT * FROM workspace_snapshots WHERE project_id = ? ORDER BY created_at DESC, id DESC LIMIT 1",
                    (project_id,),
                ).fetchone()
                if row:
                    latest_snapshots[project_id] = {
                        "id": row["id"],
                        "project_id": row["project_id"],
                        "payload": json.loads(row["payload"]),
                        "created_at": row["created_at"],
                    }
        return project_rows, latest_snapshots

    def _build_recovered_database(
        self,
        source_path: Path,
        target_path: Path,
        *,
        project_rows: dict[str, sqlite3.Row],
        latest_snapshots: dict[str, dict[str, Any]],
        reset_project_id: str,
    ) -> None:
        connection_factory = SqliteConnectionFactory(journal_mode="DELETE")
        SQLitePortfolioRepository(target_path, connection_factory=connection_factory)
        with connection_factory.open(target_path, operation="workspaceRecovery") as target, closing(sqlite3.connect(source_path)) as source:
            source.row_factory = sqlite3.Row
            for table in ("sessions", "workspace_snapshots", "memberships", "projects", "users"):
                target.execute(f"DELETE FROM {table}")
            for table in self._COPY_TABLES:
                rows = source.execute(f"SELECT * FROM {table}").fetchall()
                if not rows:
                    continue
                columns = tuple(rows[0].keys())
                placeholders = ", ".join("?" for _ in columns)
                target.executemany(
                    f"INSERT INTO {table}({', '.join(columns)}) VALUES ({placeholders})",
                    [tuple(row[column] for column in columns) for row in rows],
                )
            now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
            for project_id, project_row in project_rows.items():
                if project_id == reset_project_id:
                    payload = seed_workspace(project_id, str(project_row["title"]), now)
                    snapshot_id = f"snapshot-recovery-{project_id}-{now.replace(':', '').replace('.', '')}"
                    created_at = now
                else:
                    snapshot = latest_snapshots[project_id]
                    payload = snapshot["payload"]
                    snapshot_id = snapshot["id"]
                    created_at = snapshot["created_at"]
                target.execute(
                    "INSERT INTO workspace_snapshots(id, project_id, payload, created_at) VALUES (?, ?, ?, ?)",
                    (snapshot_id, project_id, json.dumps(payload, ensure_ascii=False), created_at),
                )

    def _verify_recovered_workspaces(self, database_path: Path) -> None:
        _, snapshots = self._read_source(database_path)
        for project_id, snapshot in snapshots.items():
            report = self._inspector.inspect(
                snapshot["payload"],
                project_id=project_id,
                snapshot_id=snapshot["id"],
            )
            if not report.is_clean:
                raise RuntimeError(f"recovered-workspace-integrity-failed:{project_id}")

    @staticmethod
    def _integrity_check(path: Path) -> str:
        with closing(sqlite3.connect(path)) as connection:
            row = connection.execute("PRAGMA integrity_check").fetchone()
        return str(row[0]) if row else "missing-result"

    @staticmethod
    def _file_hash(path: Path) -> str:
        digest = sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
