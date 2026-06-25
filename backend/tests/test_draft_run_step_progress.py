from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_progress import DraftRunProgress
from backend.app.application.public_evidence_retrieval_service import PublicEvidenceRetrievalService
from backend.app.domain.draft_run import create_queued_draft_run
from backend.app.domain.draft_run_steps import DraftRunStepKey
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request
from backend.tests.test_public_evidence_retrieval import FakeUrlReader, artifact_with_tasks


def test_operation_progress_persists_artifact_and_updates_run_progress_time(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, context_from_payload({"draftContext": make_context()})),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)
    original_updated_at = repository.get(run.id).updated_at
    sink = DraftRunProgress(repository, run.id).operation_sink(DraftRunStepKey.PUBLIC_EVIDENCE)

    PublicEvidenceRetrievalService(url_reader=FakeUrlReader()).retrieve(
        source_intent_artifact=artifact_with_tasks([
            {"id": "task-1", "kind": "readUrl", "sourceIntentItemId": "source-intent-1", "target": "https://example.com/report"}
        ]),
        progress=sink,
    )

    loaded = repository.get(run.id)
    step = next(item for item in loaded.steps if item.key == DraftRunStepKey.PUBLIC_EVIDENCE)
    progress = step.artifact_payload["progress"]
    assert loaded.updated_at != original_updated_at
    assert progress["operations"][0]["kind"] == "readUrl"
    assert progress["operations"][0]["status"] == "succeeded"
    assert progress["budget"]["staleAfterSeconds"] == 300
