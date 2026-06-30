from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.app.domain.portfolio import BlogProject, ProjectMembership, Session, UserAccount, WorkspaceSnapshot


class SQLitePortfolioRepository:
    def __init__(self, db_path: Path) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def ensure_seeded(self) -> None:
        with self._connect() as conn:
            if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
                return
            now = _now()
            users = [
                ("user-founder-editor", "Владелец портфеля", "founder@example.test", None, "active", now),
                ("user-product-editor", "Редактор Главреда", "glavred-editor@example.test", None, "active", now),
            ]
            projects = [
                (
                    "project-ai-design-patterns",
                    "user-founder-editor",
                    "AI Design Patterns",
                    "Research-heavy blog about durable AI engineering and product design patterns.",
                    "en",
                    "active",
                    "demo",
                    now,
                    now,
                ),
                (
                    "project-kasha-iz-topora",
                    "user-founder-editor",
                    "Каша из топора",
                    "RevOps and Product Marketing Telegram-native author blog.",
                    "ru",
                    "active",
                    "demo",
                    now,
                    now,
                ),
                (
                    "project-glavred-blog",
                    "user-product-editor",
                    "Блог Главреда",
                    "Product philosophy and practical AI-native editorial methods.",
                    "ru",
                    "active",
                    "demo",
                    now,
                    now,
                ),
            ]
            memberships = [
                ("membership-founder-ai-design-patterns", "user-founder-editor", "project-ai-design-patterns", "owner", "active"),
                ("membership-founder-kasha", "user-founder-editor", "project-kasha-iz-topora", "owner", "active"),
                ("membership-product-editor-glavred", "user-product-editor", "project-glavred-blog", "owner", "active"),
            ]
            conn.executemany(
                "INSERT INTO users(id, display_name, email, avatar_url, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                users,
            )
            conn.executemany(
                """
                INSERT INTO projects(
                    id, owner_user_id, title, description, language, status, benchmark_role, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                projects,
            )
            conn.executemany(
                "INSERT INTO memberships(id, user_id, project_id, role, status) VALUES (?, ?, ?, ?, ?)",
                memberships,
            )
            for project in projects:
                conn.execute(
                    "INSERT INTO workspace_snapshots(id, project_id, payload, created_at) VALUES (?, ?, ?, ?)",
                    (
                        f"snapshot-seed-{project[0]}",
                        project[0],
                        json.dumps(_seed_workspace(project[0], project[2]), ensure_ascii=False),
                        now,
                    ),
                )

    def get_user_by_email(self, email: str) -> UserAccount | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
        return _user(row) if row else None

    def get_user(self, user_id: str) -> UserAccount | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return _user(row) if row else None

    def list_projects_for_user(self, user_id: str) -> list[tuple[BlogProject, ProjectMembership]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT p.*, m.id AS membership_id, m.user_id, m.project_id, m.role, m.status AS membership_status
                FROM projects p
                JOIN memberships m ON m.project_id = p.id
                WHERE m.user_id = ? AND m.status = 'active' AND p.status = 'active'
                ORDER BY p.created_at, p.id
                """,
                (user_id,),
            ).fetchall()
        return [(_project(row), _membership_from_join(row)) for row in rows]

    def get_project_for_user(self, user_id: str, project_id: str) -> tuple[BlogProject, ProjectMembership] | None:
        projects = [item for item in self.list_projects_for_user(user_id) if item[0].id == project_id]
        return projects[0] if projects else None

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
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn


def _seed_workspace(project_id: str, title: str) -> dict[str, Any]:
    return {
        "id": f"workspace-{project_id}",
        "projectProfile": {"name": title},
        "portfolioProjectId": project_id,
        "seedSource": "backend-dev-auth",
        "updatedAt": _now(),
    }


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
