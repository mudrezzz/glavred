from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.openrouter_public_search_service import OpenRouterPublicSearchService
from backend.app.application.public_evidence_ports import PublicEvidenceSearchTask
from backend.app.infrastructure.openrouter_web_search_adapter import OpenRouterWebSearchCitation, OpenRouterWebSearchResult
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings


class FakeWebSearchAdapter:
    def __init__(self, error: Exception | None = None, title: str = "AI product trust report", snippet: str = "Teams need evals and rollback paths before AI adoption.") -> None:
        self.error = error
        self.title = title
        self.snippet = snippet
        self.query = ""

    def search(self, **kwargs: Any) -> OpenRouterWebSearchResult:
        self.query = str(kwargs.get("query") or "")
        if self.error:
            raise self.error
        return OpenRouterWebSearchResult(
            content="Opinion leaders say product trust depends on evals.",
            citations=[
                OpenRouterWebSearchCitation(
                    title=self.title,
                    url="https://example.com/trust",
                    snippet=self.snippet,
                )
            ],
            raw_response={"id": "or-search-1", "model": "test-model", "usage": {"total_tokens": 120}, "query": "opinion leaders"},
        )


def test_search_is_not_configured_when_web_tools_disabled(tmp_path) -> None:
    service = search_service(tmp_path, web_enabled=False)

    result = service.search(search_task("opinion leaders"))

    assert result.attempts[0].status.value == "notConfigured"
    assert result.items == []
    assert result.ai_run_ids == []


def test_search_creates_evidence_item_and_child_ai_run(tmp_path) -> None:
    ai_service = AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))
    service = search_service(tmp_path, ai_service=ai_service)

    task = search_task("find opinion leaders about AI product trust", target="target-1")
    result = service.search(task)

    assert result.attempts[0].status.value == "succeeded"
    assert result.items[0].source_url == "https://example.com/trust"
    assert result.items[0].provenance == "openrouterWebSearch"
    assert result.attempts[0].target == "target-1"
    assert result.attempts[0].metadata["builtQuery"] == "find opinion leaders about AI product trust"
    assert result.ai_run_ids
    run = ai_service.get_run(result.ai_run_ids[0])
    assert run is not None
    assert run.request_payload["draftRunStep"] == "publicEvidenceSearch"
    assert run.request_payload["builtQuery"] == "find opinion leaders about AI product trust"
    assert run.request_payload["originalTask"]["target"] == "target-1"
    assert run.request_payload["modelRole"] == "research"
    assert run.request_payload["modelSelectionSource"] == "webSearch"
    assert run.result_payload is not None
    assert run.result_payload["acceptedCitations"][0]["url"] == "https://example.com/trust"
    assert run.result_payload["citations"][0]["url"] == "https://example.com/trust"


def test_search_records_safe_failed_attempt_on_provider_error(tmp_path) -> None:
    service = search_service(tmp_path, adapter=FakeWebSearchAdapter(error=TimeoutError("slow")))

    result = service.search(search_task("opinion leaders"))

    assert result.attempts[0].status.value == "failed"
    assert result.items == []
    assert result.warnings[0].code == "openrouter-search-failed"
    assert result.ai_run_ids


def search_service(
    tmp_path,
    *,
    web_enabled: bool = True,
    ai_service: AiRunService | None = None,
    adapter: FakeWebSearchAdapter | None = None,
) -> OpenRouterPublicSearchService:
    return OpenRouterPublicSearchService(
        settings=BackendSettings(
            OPENROUTER_API_KEY="test-token",
            OPENROUTER_DEFAULT_MODEL="test-model",
            OPENROUTER_WEB_TOOLS_ENABLED=web_enabled,
            OPENROUTER_WEB_SEARCH_MODEL="test-model",
        ),
        ai_run_service=ai_service or AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3")),
        openrouter_validator=OpenRouterConfigValidator(),
        web_search_adapter=adapter or FakeWebSearchAdapter(),
    )


def search_task(query: str, *, target: str | None = None) -> PublicEvidenceSearchTask:
    return PublicEvidenceSearchTask(
        query=query,
        task_id="task-1",
        source_intent_item_id="source-1",
        kind="findPublicSources",
        technical_target=target,
        instruction=query,
        original_task={"id": "task-1", "kind": "findPublicSources", "target": target, "instruction": query},
    )
