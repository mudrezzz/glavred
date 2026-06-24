from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.openrouter_public_search_service import OpenRouterPublicSearchService
from backend.app.application.public_evidence_ports import PublicEvidenceSearchTask
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_web_search_adapter import OpenRouterWebSearchCitation, OpenRouterWebSearchResult
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings


class OffTopicWebSearchAdapter:
    def search(self, **kwargs: Any) -> OpenRouterWebSearchResult:
        return OpenRouterWebSearchResult(
            content="TARGET2 is a Eurosystem payment system.",
            citations=[OpenRouterWebSearchCitation(
                title="TARGET Services",
                url="https://example.com/target",
                snippet="The Eurosystem payment infrastructure TARGET2 settles payments.",
            )],
            raw_response={"id": "or-search-1", "query": kwargs.get("query")},
        )


def test_search_rejects_off_topic_citations_without_creating_evidence(tmp_path) -> None:
    service = OpenRouterPublicSearchService(
        settings=BackendSettings(
            OPENROUTER_API_KEY="test-token",
            OPENROUTER_DEFAULT_MODEL="test-model",
            OPENROUTER_WEB_TOOLS_ENABLED=True,
            OPENROUTER_WEB_SEARCH_MODEL="test-model",
        ),
        ai_run_service=AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3")),
        openrouter_validator=OpenRouterConfigValidator(),
        web_search_adapter=OffTopicWebSearchAdapter(),
    )

    result = service.search(PublicEvidenceSearchTask(
        query="find opinion leaders about AI product trust",
        task_id="task-1",
        source_intent_item_id="source-1",
        kind="findPublicSources",
        technical_target="target-1",
        instruction="find opinion leaders about AI product trust",
        original_task={"id": "task-1", "target": "target-1"},
    ))

    assert result.attempts[0].status.value == "succeeded"
    assert result.items == []
    assert result.warnings[0].code == "search-no-relevant-evidence"
    assert result.attempts[0].metadata["rejectedCitations"][0]["reason"] == "search-result-drift"
