from __future__ import annotations

import json
import sqlite3
from typing import Any


def ensure_seeded(conn: sqlite3.Connection, now: str) -> None:
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        return
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
                json.dumps(seed_workspace(project[0], project[2], now), ensure_ascii=False),
                now,
            ),
        )


def seed_workspace(project_id: str, title: str, now: str) -> dict[str, Any]:
    return {
        "id": f"workspace-{project_id}",
        "projectProfile": {"name": title},
        "portfolioProjectId": project_id,
        "seedSource": "backend-dev-auth",
        "updatedAt": now,
    }
