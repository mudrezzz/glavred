from backend.app.application.public_evidence_retrieval_service import (
    PublicEvidenceRetrievalService,
    PublicUrlReadResult,
)


class FakeUrlReader:
    def __init__(self, result: PublicUrlReadResult | None = None, error: Exception | None = None) -> None:
        self.result = result or PublicUrlReadResult(url="https://example.com/report", title="Report", text="Workflow evidence")
        self.error = error

    def read(self, url: str) -> PublicUrlReadResult:
        if self.error:
            raise self.error
        return self.result


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


def test_retrieval_handles_empty_plan() -> None:
    result = PublicEvidenceRetrievalService(url_reader=FakeUrlReader()).retrieve(source_intent_artifact={})

    payload = result.to_payload()
    assert payload["attempts"] == []
    assert payload["warnings"][0]["code"] == "no-public-retrieval-tasks"


def artifact_with_tasks(tasks: list[dict[str, str]]) -> dict:
    return {"researchPlan": {"verificationTasks": tasks}}
