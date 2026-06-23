from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.domain.draft_run import DraftRunStatus, create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_feasible_run_writes_gate_contract_and_continues_to_draft(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, draft_context),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(repository, DeterministicDraftService()).execute(run.id)

    assert result.status == DraftRunStatus.SUCCEEDED
    assert result.final_draft is not None
    assert [step.key.value for step in result.steps] == [
        "context",
        "sourceIntent",
        "feasibility",
        "postContract",
        "rulePack",
        "materialPlan",
        "strategy",
        "rhetoricalPlans",
        "draft",
        "validation",
        "complete",
    ]
    assert result.steps[2].artifact_payload["status"] == "feasible_with_constraints"
    assert result.steps[3].artifact_payload["status"] == "created"
    assert result.steps[4].artifact_payload["metadata"]["feasibilityStatus"] == "feasible_with_constraints"


def test_blocked_run_succeeds_without_final_draft_or_fallback(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    run = create_queued_draft_run(
        request_payload=request_to_payload(request),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(repository, DeterministicDraftService()).execute(run.id)

    assert result.status == DraftRunStatus.SUCCEEDED
    assert result.final_draft is None
    assert result.steps[2].artifact_payload["status"] == "needs_human_decision"
    assert result.steps[3].artifact_payload["status"] == "notCreated"
    assert result.steps[4].status.value == "pending"
    assert result.steps[-1].artifact_payload["status"] == "blocked"
    assert result.steps[-1].artifact_payload["blockedBy"] == "feasibility"


def test_missing_candidate_link_with_source_evidence_continues_to_draft(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    context = make_context()
    context.pop("candidate")
    draft_context = context_from_payload({"draftContext": context})
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, draft_context),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(repository, DeterministicDraftService()).execute(run.id)

    assert result.status == DraftRunStatus.SUCCEEDED
    assert result.final_draft is not None
    assert result.steps[2].artifact_payload["status"] == "feasible_with_constraints"
    assert result.steps[3].artifact_payload["status"] == "created"
