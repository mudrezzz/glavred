from backend.app.application.public_evidence_retrieval_service import (
    PublicEvidenceRetrievalService,
)
from backend.app.application.public_evidence_ports import PublicEvidenceSearchResult, PublicEvidenceSearchTask, PublicUrlReadResult
from backend.app.domain.draft_public_evidence import PublicEvidenceAllowedUse, PublicEvidenceAttempt, PublicEvidenceAttemptStatus, PublicEvidenceItem


class FakeUrlReader:
    def __init__(self, result: PublicUrlReadResult | None = None, error: Exception | None = None) -> None:
        self.result = result or PublicUrlReadResult(url="https://example.com/report", title="Report", text="Workflow evidence")
        self.error = error

    def read(self, url: str) -> PublicUrlReadResult:
        if self.error:
            raise self.error
        return self.result


class FakeSearchAdapter:
    def __init__(self) -> None:
        self.task: PublicEvidenceSearchTask | None = None

    def search(self, task: PublicEvidenceSearchTask) -> PublicEvidenceSearchResult:
        self.task = task
        return PublicEvidenceSearchResult(
            attempts=[PublicEvidenceAttempt(
                id="search-task-2",
                task_id=task.task_id,
                source_intent_item_id=task.source_intent_item_id,
                kind="search",
                target=task.technical_target or task.query,
                status=PublicEvidenceAttemptStatus.SUCCEEDED,
                metadata={"builtQuery": task.query, "originalTask": task.original_task},
            )],
            items=[PublicEvidenceItem(
                id="item-1",
                attempt_id="search-task-2",
                source_url="https://example.com/search",
                source_title="Search result",
                snippet="Search evidence",
                text_summary="Search evidence",
                provenance="openrouterWebSearch",
                confidence="medium",
                allowed_use=PublicEvidenceAllowedUse.NEEDS_QUALIFICATION,
            )],
            ai_run_ids=["ai-run-1"],
            metadata={"searchProvider": "openrouter:web_search"},
        )


def test_retrieval_reads_url_and_creates_evidence_item() -> None:
    result = PublicEvidenceRetrievalService(url_reader=FakeUrlReader()).retrieve(
        source_intent_artifact=artifact_with_tasks([
            {"id": "task-1", "kind": "readUrl", "sourceIntentItemId": "source-intent-1", "target": "https://example.com/report"}
        ])
    )

    payload = result.to_payload()
    assert payload["attempts"][0]["status"] == "succeeded"
    assert payload["items"][0]["sourceTitle"] == "Report"
    assert payload["items"][0]["allowedUse"] == "needsQualification"


def test_retrieval_records_failed_url_without_stopping_batch() -> None:
    result = PublicEvidenceRetrievalService(url_reader=FakeUrlReader(error=TimeoutError("slow"))).retrieve(
        source_intent_artifact=artifact_with_tasks([
            {"id": "task-1", "kind": "readUrl", "sourceIntentItemId": "source-intent-1", "target": "https://example.com/report"}
        ])
    )

    payload = result.to_payload()
    assert payload["attempts"][0]["status"] == "failed"
    assert payload["items"] == []
    assert payload["warnings"][0]["code"] == "url-read-failed"


def test_retrieval_marks_search_tasks_as_not_configured() -> None:
    result = PublicEvidenceRetrievalService(url_reader=FakeUrlReader()).retrieve(
        source_intent_artifact=artifact_with_tasks([
            {"id": "task-2", "kind": "findPublicSources", "sourceIntentItemId": "source-intent-2", "target": "opinion leaders"}
        ])
    )

    payload = result.to_payload()
    assert payload["attempts"][0]["status"] == "notConfigured"
    assert payload["items"] == []
    assert payload["metadata"]["searchProvider"] == "notConfigured"


def test_retrieval_merges_configured_search_results() -> None:
    adapter = FakeSearchAdapter()
    result = PublicEvidenceRetrievalService(url_reader=FakeUrlReader(), search_adapter=adapter).retrieve(
        source_intent_artifact=artifact_with_tasks([
            {"id": "task-2", "kind": "findPublicSources", "sourceIntentItemId": "source-intent-2", "target": "target-1", "instruction": "find opinion leaders about AI product trust"}
        ])
    )

    payload = result.to_payload()
    assert payload["attempts"][0]["status"] == "succeeded"
    assert payload["attempts"][0]["target"] == "target-1"
    assert payload["attempts"][0]["metadata"]["builtQuery"] == "find opinion leaders about AI product trust"
    assert payload["items"][0]["sourceTitle"] == "Search result"
    assert payload["metadata"]["searchProvider"] == "openrouter:web_search"
    assert payload["aiRunIds"] == ["ai-run-1"]
    assert adapter.task is not None
    assert adapter.task.query == "find opinion leaders about AI product trust"


def test_retrieval_handles_empty_plan() -> None:
    result = PublicEvidenceRetrievalService(url_reader=FakeUrlReader()).retrieve(source_intent_artifact={})

    payload = result.to_payload()
    assert payload["attempts"] == []
    assert payload["warnings"][0]["code"] == "no-public-retrieval-tasks"


def artifact_with_tasks(tasks: list[dict[str, str]]) -> dict:
    return {"researchPlan": {"verificationTasks": tasks}}
