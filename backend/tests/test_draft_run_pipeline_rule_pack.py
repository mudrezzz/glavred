from backend.app.application.deterministic_draft_service import DeterministicDraftService
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_pipeline import DraftRunPipeline
from backend.app.domain.draft_run import DraftRunStatus, create_queued_draft_run
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


class FailingRulePackCompiler:
    def compile(self, context_summary: dict) -> object:
        raise RuntimeError("compiler exploded")


def test_draft_run_pipeline_marks_run_failed_when_rule_pack_compiler_fails(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, draft_context),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(
        repository,
        DeterministicDraftService(),
        rule_pack_compiler=FailingRulePackCompiler(),
    ).execute(run.id)

    assert result.status == DraftRunStatus.FAILED
    assert result.error == "compiler exploded"


def test_draft_run_pipeline_writes_rule_registry_inside_rule_pack_step(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, draft_context),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(repository, DeterministicDraftService()).execute(run.id)
    rule_pack = result.steps[5].artifact_payload

    assert result.status == DraftRunStatus.SUCCEEDED
    assert rule_pack["metadata"]["registryVersion"] == "rule-registry-v2"
    assert rule_pack["ruleRegistrySnapshot"]["version"] == "rule-registry-v2"
    assert rule_pack["ruleRegistrySnapshot"]["metadata"]["ruleCount"] > 0
    assert rule_pack["ruleRegistrySnapshot"]["rules"][0]["binding"]["validatorType"]
