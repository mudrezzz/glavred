from backend.app.infrastructure.sqlite_runtime import (
    SqliteConnectionFactory,
    SqliteDatabaseCorruptionError,
)
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository


def test_sqlite_connection_factory_applies_runtime_pragmas(tmp_path) -> None:
    db_path = tmp_path / "runtime.sqlite3"
    factory = SqliteConnectionFactory()

    with factory.open(db_path, operation="test") as connection:
        busy_timeout = connection.execute("PRAGMA busy_timeout").fetchone()[0]
        foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()[0]
        journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
        synchronous = connection.execute("PRAGMA synchronous").fetchone()[0]

    assert busy_timeout == 30000
    assert foreign_keys == 1
    assert journal_mode.lower() == "wal"
    assert synchronous == 1


def test_integrity_check_reports_malformed_database(tmp_path) -> None:
    db_path = tmp_path / "broken.sqlite3"
    db_path.write_bytes(b"not a sqlite database")
    result = SqliteConnectionFactory().integrity_check(db_path, storage="draftRuns")

    assert result.ok is False
    assert result.error is not None
    assert result.error["code"] == "sqliteDatabaseMalformed"


def test_repository_raises_controlled_error_for_malformed_database(tmp_path) -> None:
    db_path = tmp_path / "draft-runs.sqlite3"
    db_path.write_bytes(b"not a sqlite database")

    try:
        SqliteDraftRunRepository(db_path)
    except SqliteDatabaseCorruptionError as exc:
        payload = exc.to_payload()
    else:  # pragma: no cover - test guard
        raise AssertionError("Repository accepted malformed database")

    assert payload["code"] == "sqliteDatabaseMalformed"
    assert payload["storage"] == "draft-runs.sqlite3"
    assert str(tmp_path) not in payload["message"]
