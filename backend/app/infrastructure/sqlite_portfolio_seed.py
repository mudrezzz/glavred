from __future__ import annotations

import json
import sqlite3
from typing import Any


FOUNDER_NAME = "\u0412\u043b\u0430\u0434\u0435\u043b\u0435\u0446 \u043f\u043e\u0440\u0442\u0444\u0435\u043b\u044f"
PRODUCT_EDITOR_NAME = "\u0420\u0435\u0434\u0430\u043a\u0442\u043e\u0440 \u0413\u043b\u0430\u0432\u0440\u0435\u0434\u0430"
AI_DESIGN_PATTERNS_DESCRIPTION = (
    "Industrial AI design patterns, "
    "\u0422\u041e\u0438\u0420"
    " and Decision Intelligence Telegram blog."
)
KASHA_TITLE = "\u041a\u0430\u0448\u0430 \u0438\u0437 \u0442\u043e\u043f\u043e\u0440\u0430"
GLAVRED_BLOG_TITLE = "\u0411\u043b\u043e\u0433 \u0413\u043b\u0430\u0432\u0440\u0435\u0434\u0430"


def ensure_seeded(conn: sqlite3.Connection, now: str) -> None:
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        return
    users = [
        ("user-founder-editor", FOUNDER_NAME, "founder@example.test", None, "active", now),
        ("user-product-editor", PRODUCT_EDITOR_NAME, "glavred-editor@example.test", None, "active", now),
    ]
    projects = [
        (
            "project-ai-design-patterns",
            "user-founder-editor",
            "AI Design Patterns",
            AI_DESIGN_PATTERNS_DESCRIPTION,
            "ru",
            "active",
            "demo",
            now,
            now,
        ),
        (
            "project-kasha-iz-topora",
            "user-founder-editor",
            KASHA_TITLE,
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
            GLAVRED_BLOG_TITLE,
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
