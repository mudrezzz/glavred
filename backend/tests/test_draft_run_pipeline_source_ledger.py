from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.domain.draft_run import create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_pipeline_writes_source_ledger_into_context_step(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, draft_context),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(repository, DeterministicDraftService()).execute(run.id)

    context_step = result.steps[0].artifact_payload
    source_ledger = context_step["sourceLedger"]
    claim_ids = {claim["id"] for claim in source_ledger["claims"]}

    assert source_ledger["metadata"]["version"] == "source-ledger-v1"
    assert source_ledger["metadata"]["claimCount"] > 0
    assert "signal-author-correction" in claim_ids
    assert len(result.steps) == 11
    assert result.steps[7].key.value == "rhetoricalPlans"


def test_pipeline_exposes_source_ledger_metadata_to_rule_pack(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, draft_context),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(repository, DeterministicDraftService()).execute(run.id)

    source_ledger_metadata = result.steps[0].artifact_payload["sourceLedger"]["metadata"]
    rule_pack_metadata = result.steps[4].artifact_payload["metadata"]

    assert rule_pack_metadata["sourceLedgerClaimCount"] == source_ledger_metadata["claimCount"]
    assert rule_pack_metadata["sourceLedgerWarningCount"] == source_ledger_metadata["warningCount"]
