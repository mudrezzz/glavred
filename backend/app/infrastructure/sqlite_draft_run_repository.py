import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.app.domain.draft_run import (
    DraftRun,
    DraftRunStatus,
    DraftRunStep,
    DraftRunStepKey,
    DraftRunStepStatus,
)


class SqliteDraftRunRepository:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._ensure_schema()

    def save(self, run: DraftRun) -> DraftRun:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO draft_runs (
                  id, status, request_payload, input_summary, final_draft,
                  error, ai_run_ids, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self._run_params(run),
            )
            connection.executemany(
                """
                INSERT INTO draft_run_steps (
                  id, run_id, step_key, status, title, artifact_payload,
                  error, started_at, completed_at, sort_order
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [self._step_params(step) for step in run.steps],
            )
        return run

    def get(self, run_id: str) -> DraftRun | None:
        with self._connect() as connection:
            run_row = connection.execute(
                "SELECT * FROM draft_runs WHERE id = ?",
                (run_id,),
            ).fetchone()
            step_rows = connection.execute(
                "SELECT * FROM draft_run_steps WHERE run_id = ? ORDER BY sort_order",
                (run_id,),
            ).fetchall()

        return self._row_to_run(run_row, step_rows) if run_row is not None else None

    def set_run_status(
        self,
        run_id: str,
        status: DraftRunStatus,
        *,
        error: str | None = None,
        final_draft: dict[str, Any] | None = None,
        ai_run_ids: list[str] | None = None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE draft_runs
                SET status = ?, error = ?, final_draft = COALESCE(?, final_draft),
                    ai_run_ids = COALESCE(?, ai_run_ids), updated_at = ?
                WHERE id = ?
                """,
                (
                    status.value,
                    error,
                    json.dumps(final_draft, ensure_ascii=False) if final_draft is not None else None,
                    json.dumps(ai_run_ids, ensure_ascii=False) if ai_run_ids is not None else None,
                    datetime.now(UTC).isoformat(),
                    run_id,
                ),
            )

    def set_step_status(
        self,
        run_id: str,
        key: DraftRunStepKey,
        status: DraftRunStepStatus,
        *,
        artifact_payload: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        now = datetime.now(UTC).isoformat()
        started_at = now if status == DraftRunStepStatus.RUNNING else None
        completed_at = now if status in {DraftRunStepStatus.SUCCEEDED, DraftRunStepStatus.FAILED} else None
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE draft_run_steps
                SET status = ?, artifact_payload = COALESCE(?, artifact_payload), error = ?,
                    started_at = COALESCE(started_at, ?), completed_at = COALESCE(?, completed_at)
                WHERE run_id = ? AND step_key = ?
                """,
                (
                    status.value,
                    json.dumps(artifact_payload, ensure_ascii=False)
                    if artifact_payload is not None
                    else None,
                    error,
                    started_at,
                    completed_at,
                    run_id,
                    key.value,
                ),
            )
            connection.execute(
                "UPDATE draft_runs SET updated_at = ? WHERE id = ?",
                (now, run_id),
            )

    def _ensure_schema(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS draft_runs (
                  id TEXT PRIMARY KEY,
                  status TEXT NOT NULL,
                  request_payload TEXT NOT NULL,
                  input_summary TEXT NOT NULL,
                  final_draft TEXT,
                  error TEXT,
                  ai_run_ids TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS draft_run_steps (
                  id TEXT PRIMARY KEY,
                  run_id TEXT NOT NULL,
                  step_key TEXT NOT NULL,
                  status TEXT NOT NULL,
                  title TEXT NOT NULL,
                  artifact_payload TEXT,
                  error TEXT,
                  started_at TEXT,
                  completed_at TEXT,
                  sort_order INTEGER NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_draft_run_steps_run_id ON draft_run_steps(run_id)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _run_params(self, run: DraftRun) -> tuple[Any, ...]:
        return (
            run.id,
            run.status.value,
            json.dumps(run.request_payload, ensure_ascii=False),
            json.dumps(run.input_summary, ensure_ascii=False),
            json.dumps(run.final_draft, ensure_ascii=False) if run.final_draft is not None else None,
            run.error,
            json.dumps(run.ai_run_ids, ensure_ascii=False),
            run.created_at.isoformat(),
            run.updated_at.isoformat(),
        )

    def _step_params(self, step: DraftRunStep) -> tuple[Any, ...]:
        return (
            step.id,
            step.run_id,
            step.key.value,
            step.status.value,
            step.title,
            json.dumps(step.artifact_payload, ensure_ascii=False)
            if step.artifact_payload is not None
            else None,
            step.error,
            step.started_at.isoformat() if step.started_at is not None else None,
            step.completed_at.isoformat() if step.completed_at is not None else None,
            step.sort_order,
        )

    def _row_to_run(self, row: sqlite3.Row, step_rows: list[sqlite3.Row]) -> DraftRun:
        return DraftRun(
            id=row["id"],
            status=DraftRunStatus(row["status"]),
            request_payload=json.loads(row["request_payload"]),
            input_summary=json.loads(row["input_summary"]),
            final_draft=json.loads(row["final_draft"]) if row["final_draft"] else None,
            error=row["error"],
            ai_run_ids=json.loads(row["ai_run_ids"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            steps=[self._row_to_step(step_row) for step_row in step_rows],
        )

    def _row_to_step(self, row: sqlite3.Row) -> DraftRunStep:
        return DraftRunStep(
            id=row["id"],
            run_id=row["run_id"],
            key=DraftRunStepKey(row["step_key"]),
            status=DraftRunStepStatus(row["status"]),
            title=row["title"],
            artifact_payload=json.loads(row["artifact_payload"])
            if row["artifact_payload"]
            else None,
            error=row["error"],
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"])
            if row["completed_at"]
            else None,
            sort_order=row["sort_order"],
        )
