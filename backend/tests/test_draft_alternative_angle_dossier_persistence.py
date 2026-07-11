from copy import deepcopy

from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_to_payload
from backend.app.drafting.application.workflow.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.domain.draft_run import create_queued_draft_run
from backend.app.domain.draft_run_steps import DraftRunStepKey, DraftRunStepStatus
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture
from backend.tests.test_draft_alternative_angle_tournament import (
    SequentialAdapter,
    candidate_payload,
    draft_artifact,
    initial_validation,
    route_payload,
    tournament_service,
)
from backend.tests.test_draft_planning_services import context_and_rule_pack
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_route_is_persisted_before_challenger_dossier_is_built(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, context_from_payload({"draftContext": make_context()})),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)
    snapshot = ProviderDossierTestFixture.snapshot()["steps"]
    for key in ("postContract", "publicEvidence", "rulePack", "materialPlan", "strategy", "rhetoricalPlans", "draft"):
        repository.set_step_status(run.id, DraftRunStepKey(key), DraftRunStepStatus.SUCCEEDED, artifact_payload=deepcopy(snapshot[key]))
    initial = deepcopy(snapshot["validation"])
    initial.pop("alternativeAngleTournament", None)
    repository.set_step_status(run.id, DraftRunStepKey.VALIDATION, DraftRunStepStatus.RUNNING, artifact_payload=initial)
    progress = DraftRunStepOperationSink(repository, run.id, DraftRunStepKey.VALIDATION)
    adapter = SequentialAdapter([route_payload(), candidate_payload()])
    context_summary, rule_pack = context_and_rule_pack()

    merged, tournament, ai_run_ids = tournament_service(tmp_path, adapter, configured=True).run(
        request=request,
        draft_artifact=draft_artifact(),
        validation_report=initial_validation(),
        context_summary=context_summary,
        context_artifact={},
        rule_pack=rule_pack,
        material_plan=snapshot["materialPlan"]["materialPlan"],
        draft_strategy=snapshot["strategy"]["draftStrategy"],
        progress=progress,
    )

    persisted = repository.get(run.id)
    validation = next(step for step in persisted.steps if step.key is DraftRunStepKey.VALIDATION).artifact_payload
    assert validation["alternativeAngleTournament"]["route"]["id"] == "challenger"
    assert tournament["status"] == "succeeded"
    assert merged["alternativeAngleCandidateId"]
    assert len(ai_run_ids) == 2
