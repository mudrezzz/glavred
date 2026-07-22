from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.app.domain.portfolio import BlogProject, ProjectMembership, Session, UserAccount, WorkspaceSnapshot
from backend.app.infrastructure.sqlite_portfolio_seed import ensure_seeded, seed_workspace
from backend.app.infrastructure.sqlite_runtime import SqliteConnectionFactory


class SQLitePortfolioRepository:
    def __init__(
        self,
        db_path: Path,
        connection_factory: SqliteConnectionFactory | None = None,
    ) -> None:
        self._db_path = Path(db_path)
        self._connection_factory = connection_factory or SqliteConnectionFactory()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def ensure_seeded(self) -> None:
        with self._connect() as conn:
            ensure_seeded(conn, _now())

    def get_user_by_email(self, email: str) -> UserAccount | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
        return _user(row) if row else None

    def get_user(self, user_id: str) -> UserAccount | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return _user(row) if row else None

    def list_projects_for_user(
        self,
        user_id: str,
        *,
        include_archived: bool = False,
    ) -> list[tuple[BlogProject, ProjectMembership]]:
        status_filter = "" if include_archived else "AND p.status = 'active'"
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT p.*, m.id AS membership_id, m.user_id, m.project_id, m.role, m.status AS membership_status
                FROM projects p
                JOIN memberships m ON m.project_id = p.id
                WHERE m.user_id = ? AND m.status = 'active' {status_filter}
                ORDER BY p.created_at, p.id
                """,
                (user_id,),
            ).fetchall()
        return [(_project(row), _membership_from_join(row)) for row in rows]

    def get_project_for_user(
        self,
        user_id: str,
        project_id: str,
        *,
        include_archived: bool = True,
    ) -> tuple[BlogProject, ProjectMembership] | None:
        projects = [
            item
            for item in self.list_projects_for_user(user_id, include_archived=include_archived)
            if item[0].id == project_id
        ]
        return projects[0] if projects else None

    def create_project_for_user(
        self,
        owner_user_id: str,
        *,
        title: str,
        description: str,
        language: str,
    ) -> tuple[BlogProject, ProjectMembership]:
        now = _now()
        project_id = f"project-{uuid.uuid4().hex[:12]}"
        membership_id = f"membership-{owner_user_id}-{project_id}"
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO projects(
                    id, owner_user_id, title, description, language, status, benchmark_role, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (project_id, owner_user_id, title, description, language, "active", "real", now, now),
            )
            conn.execute(
                "INSERT INTO memberships(id, user_id, project_id, role, status) VALUES (?, ?, ?, ?, ?)",
                (membership_id, owner_user_id, project_id, "owner", "active"),
            )
            conn.execute(
                "INSERT INTO workspace_snapshots(id, project_id, payload, created_at) VALUES (?, ?, ?, ?)",
                (
                    f"snapshot-seed-{project_id}",
                    project_id,
                    json.dumps(seed_workspace(project_id, title, now), ensure_ascii=False),
                    now,
                ),
            )
        item = self.get_project_for_user(owner_user_id, project_id, include_archived=True)
        if item is None:
            raise RuntimeError("created-project-not-readable")
        return item

    def update_project(
        self,
        project_id: str,
        *,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> None:
        assignments: list[str] = []
        values: list[str] = []
        if title is not None and title:
            assignments.append("title = ?")
            values.append(title)
        if description is not None:
            assignments.append("description = ?")
            values.append(description)
        if status is not None:
            assignments.append("status = ?")
            values.append(status)
        if not assignments:
            return
        now = _now()
        assignments.append("updated_at = ?")
        values.extend([now, project_id])
        with self._connect() as conn:
            conn.execute(f"UPDATE projects SET {', '.join(assignments)} WHERE id = ?", values)

    def latest_workspace_snapshot(self, project_id: str) -> WorkspaceSnapshot | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM workspace_snapshots WHERE project_id = ? ORDER BY created_at DESC, id DESC LIMIT 1",
                (project_id,),
            ).fetchone()
        return _snapshot(row) if row else None

    def save_workspace_snapshot(self, project_id: str, payload: dict[str, Any]) -> WorkspaceSnapshot:
        now = _now()
        snapshot_id = f"snapshot-{project_id}-{now.replace(':', '').replace('.', '')}"
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO workspace_snapshots(id, project_id, payload, created_at) VALUES (?, ?, ?, ?)",
                (snapshot_id, project_id, json.dumps(payload, ensure_ascii=False), now),
            )
            conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (now, project_id))
        return WorkspaceSnapshot(id=snapshot_id, project_id=project_id, payload=payload, created_at=_parse_dt(now))

    def create_session(self, token: str, user_id: str, expires_at: datetime) -> Session:
        now = _now()
        expires = _format_dt(expires_at)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO sessions(token, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
                (token, user_id, expires, now),
            )
        return Session(token=token, user_id=user_id, expires_at=expires_at, created_at=_parse_dt(now))

    def get_session(self, token: str) -> Session | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE token = ?", (token,)).fetchone()
            if not row:
                return None
            session = _session(row)
            if session.expires_at <= datetime.now(UTC):
                conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
                return None
            return session

    def delete_session(self, token: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    avatar_url TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    owner_user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    language TEXT NOT NULL,
                    status TEXT NOT NULL,
                    benchmark_role TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS memberships (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    UNIQUE(user_id, project_id)
                );
                CREATE TABLE IF NOT EXISTS workspace_snapshots (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_workspace_snapshots_project_latest
                    ON workspace_snapshots(project_id, created_at DESC, id DESC);
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def _connect(self):
        return self._connection_factory.open(self._db_path, operation="portfolioRepository")


def _now() -> str:
    return _format_dt(datetime.now(UTC))


def _format_dt(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _user(row: sqlite3.Row) -> UserAccount:
    return UserAccount(
        id=row["id"],
        display_name=row["display_name"],
        email=row["email"],
        avatar_url=row["avatar_url"],
        status=row["status"],
        created_at=_parse_dt(row["created_at"]),
    )


def _project(row: sqlite3.Row) -> BlogProject:
    return BlogProject(
        id=row["id"],
        owner_user_id=row["owner_user_id"],
        title=row["title"],
        description=row["description"],
        language=row["language"],
        status=row["status"],
        benchmark_role=row["benchmark_role"],
        created_at=_parse_dt(row["created_at"]),
        updated_at=_parse_dt(row["updated_at"]),
    )


def _membership_from_join(row: sqlite3.Row) -> ProjectMembership:
    return ProjectMembership(
        id=row["membership_id"],
        user_id=row["user_id"],
        project_id=row["project_id"],
        role=row["role"],
        status=row["membership_status"],
    )


def _snapshot(row: sqlite3.Row) -> WorkspaceSnapshot:
    return WorkspaceSnapshot(
        id=row["id"],
        project_id=row["project_id"],
        payload=json.loads(row["payload"]),
        created_at=_parse_dt(row["created_at"]),
    )


def _session(row: sqlite3.Row) -> Session:
    return Session(
        token=row["token"],
        user_id=row["user_id"],
        expires_at=_parse_dt(row["expires_at"]),
        created_at=_parse_dt(row["created_at"]),
    )
