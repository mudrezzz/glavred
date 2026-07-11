"""Owner: backend.infrastructure.sqlite runtime.

Used by: local SQLite repositories, API storage diagnostics, and integrity scripts.
Does not own: repository schemas, domain mapping, product runtime semantics, or DB migrations.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

import sqlite3
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

SQLITE_TIMEOUT_SECONDS = 30.0
SQLITE_BUSY_TIMEOUT_MS = int(SQLITE_TIMEOUT_SECONDS * 1000)


@dataclass(frozen=True)
class SqliteStorageDiagnostic:
    code: str
    storage: str
    operation: str
    message: str


class SqliteStorageError(RuntimeError):
    def __init__(self, diagnostic: SqliteStorageDiagnostic) -> None:
        super().__init__(diagnostic.message)
        self.diagnostic = diagnostic

    def to_payload(self) -> dict[str, str]:
        return {
            "code": self.diagnostic.code,
            "storage": self.diagnostic.storage,
            "operation": self.diagnostic.operation,
            "message": self.diagnostic.message,
        }


class SqliteDatabaseCorruptionError(SqliteStorageError):
    pass


class SqliteDatabaseUnavailableError(SqliteStorageError):
    pass


@dataclass(frozen=True)
class SqliteIntegrityResult:
    storage: str
    path: str
    ok: bool
    result: str
    error: dict[str, str] | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "storage": self.storage,
            "path": self.path,
            "ok": self.ok,
            "result": self.result,
        }
        if self.error is not None:
            payload["error"] = self.error
        return payload


class SqliteConnectionFactory:
    def __init__(
        self,
        *,
        timeout_seconds: float = SQLITE_TIMEOUT_SECONDS,
        busy_timeout_ms: int = SQLITE_BUSY_TIMEOUT_MS,
        journal_mode: str | None = None,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._busy_timeout_ms = busy_timeout_ms
        configured_mode = str(journal_mode or os.getenv("SQLITE_JOURNAL_MODE") or "WAL").strip().upper()
        self._journal_mode = configured_mode if configured_mode in {"WAL", "DELETE"} else "WAL"

    @contextmanager
    def open(self, path: Path, *, operation: str) -> Iterator[sqlite3.Connection]:
        resolved_path = Path(path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(resolved_path, timeout=self._timeout_seconds)
            connection.row_factory = sqlite3.Row
            self._apply_pragmas(connection)
            yield connection
            connection.commit()
        except SqliteStorageError:
            if connection is not None:
                connection.rollback()
            raise
        except sqlite3.Error as exc:
            if connection is not None:
                connection.rollback()
            raise storage_error_from_sqlite(resolved_path, operation, exc) from exc
        finally:
            if connection is not None:
                connection.close()

    def integrity_check(self, path: Path, *, storage: str) -> SqliteIntegrityResult:
        resolved_path = Path(path)
        if not resolved_path.exists():
            return SqliteIntegrityResult(
                storage=storage,
                path=str(resolved_path),
                ok=False,
                result="missing",
                error={
                    "code": "sqliteStorageMissing",
                    "message": "SQLite storage file does not exist.",
                },
            )
        try:
            with sqlite3.connect(resolved_path, timeout=self._timeout_seconds) as connection:
                result = connection.execute("PRAGMA integrity_check").fetchone()
        except sqlite3.Error as exc:
            error = storage_error_from_sqlite(resolved_path, "integrityCheck", exc)
            return SqliteIntegrityResult(
                storage=storage,
                path=str(resolved_path),
                ok=False,
                result="error",
                error=error.to_payload(),
            )
        value = str(result[0]) if result else "empty integrity_check result"
        return SqliteIntegrityResult(
            storage=storage,
            path=str(resolved_path),
            ok=value.lower() == "ok",
            result=value,
        )

    def _apply_pragmas(self, connection: sqlite3.Connection) -> None:
        connection.execute(f"PRAGMA busy_timeout = {self._busy_timeout_ms}")
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA journal_mode = {self._journal_mode}")
        connection.execute("PRAGMA synchronous = NORMAL")


def storage_error_from_sqlite(path: Path, operation: str, exc: sqlite3.Error) -> SqliteStorageError:
    message = str(exc) or exc.__class__.__name__
    normalized = message.lower()
    diagnostic = SqliteStorageDiagnostic(
        code="sqliteStorageUnavailable",
        storage=Path(path).name,
        operation=operation,
        message=f"SQLite storage is unavailable during {operation}: {message}",
    )
    if "malformed" in normalized or "file is not a database" in normalized or "disk image" in normalized:
        return SqliteDatabaseCorruptionError(
            SqliteStorageDiagnostic(
                code="sqliteDatabaseMalformed",
                storage=Path(path).name,
                operation=operation,
                message=f"SQLite storage is malformed during {operation}: {message}",
            )
        )
    return SqliteDatabaseUnavailableError(diagnostic)
