import sqlite3

from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.application.ai_run_service import AiRunService


def test_repository_creates_schema_on_first_use(tmp_path) -> None:
    db_path = tmp_path / "audit.sqlite3"

    SqliteAiRunRepository(db_path)

    with sqlite3.connect(db_path) as connection:
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'ai_runs'"
        ).fetchone()

    assert table is not None


def test_repository_persists_and_reads_ai_run_payload(tmp_path) -> None:
    repository = SqliteAiRunRepository(tmp_path / "audit.sqlite3")
    service = AiRunService(repository)

    created = service.create_recorded_run(
        capability=AiRunCapability.DRAFT_GENERATION,
        provider=AiRunProvider.OPENROUTER,
        model="openrouter/test-model",
        request_payload={"title": "Draft", "nested": {"api_key": "secret"}},
    )

    loaded = repository.get(created.id)

    assert loaded is not None
    assert loaded.id == created.id
    assert loaded.request_payload == {"title": "Draft", "nested": {"api_key": "[redacted]"}}
    assert loaded.result_payload is None


def test_repository_lists_newest_runs_and_filters_by_capability(tmp_path) -> None:
    repository = SqliteAiRunRepository(tmp_path / "audit.sqlite3")
    service = AiRunService(repository)

    older = service.create_recorded_run(
        capability=AiRunCapability.DOCUMENT_IMPORT,
        provider=AiRunProvider.NONE,
        model=None,
        request_payload={"document": "first"},
    )
    newer = service.create_recorded_run(
        capability=AiRunCapability.DRAFT_GENERATION,
        provider=AiRunProvider.DETERMINISTIC,
        model=None,
        request_payload={"draft": "second"},
    )

    all_runs = repository.list(limit=10)
    draft_runs = repository.list(limit=10, capability=AiRunCapability.DRAFT_GENERATION)

    assert [run.id for run in all_runs] == [newer.id, older.id]
    assert [run.id for run in draft_runs] == [newer.id]
