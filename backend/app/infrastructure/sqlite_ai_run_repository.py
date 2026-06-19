import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.app.domain.ai_run import AiRun, AiRunCapability, AiRunProvider, AiRunStatus


class SqliteAiRunRepository:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._ensure_schema()

    def save(self, run: AiRun) -> AiRun:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO ai_runs (
                  id, capability, status, provider, model, request_payload,
                  result_payload, error, fallback_used, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.capability.value,
                    run.status.value,
                    run.provider.value,
                    run.model,
                    json.dumps(run.request_payload, ensure_ascii=False),
                    json.dumps(run.result_payload, ensure_ascii=False)
                    if run.result_payload is not None
                    else None,
                    run.error,
                    int(run.fallback_used),
                    run.created_at.isoformat(),
                    run.updated_at.isoformat(),
                ),
            )
        return run

    def get(self, run_id: str) -> AiRun | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM ai_runs WHERE id = ?", (run_id,)).fetchone()

        return self._row_to_run(row) if row is not None else None

    def list(self, *, limit: int, capability: AiRunCapability | None = None) -> list[AiRun]:
        query = "SELECT * FROM ai_runs"
        params: tuple[Any, ...]
        if capability is None:
            query += " ORDER BY created_at DESC, rowid DESC LIMIT ?"
            params = (limit,)
        else:
            query += " WHERE capability = ? ORDER BY created_at DESC, rowid DESC LIMIT ?"
            params = (capability.value, limit)

        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()

        return [self._row_to_run(row) for row in rows]

    def _ensure_schema(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_runs (
                  id TEXT PRIMARY KEY,
                  capability TEXT NOT NULL,
                  status TEXT NOT NULL,
                  provider TEXT NOT NULL,
                  model TEXT,
                  request_payload TEXT NOT NULL,
                  result_payload TEXT,
                  error TEXT,
                  fallback_used INTEGER NOT NULL,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_ai_runs_created_at ON ai_runs(created_at DESC)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_ai_runs_capability ON ai_runs(capability)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _row_to_run(self, row: sqlite3.Row) -> AiRun:
        return AiRun(
            id=row["id"],
            capability=AiRunCapability(row["capability"]),
            status=AiRunStatus(row["status"]),
            provider=AiRunProvider(row["provider"]),
            model=row["model"],
            request_payload=json.loads(row["request_payload"]),
            result_payload=json.loads(row["result_payload"]) if row["result_payload"] else None,
            error=row["error"],
            fallback_used=bool(row["fallback_used"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
