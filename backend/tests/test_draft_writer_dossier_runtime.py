import json
from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.dossiers.provider_dossier_factories import (
    AlternativeAngleDossierFactory,
    WriterDossierFactory,
)
from backend.app.drafting.application.generation.deterministic_draft_candidate_service import DeterministicDraftCandidateService
from backend.app.drafting.application.generation.draft_candidate_provider_service import DraftCandidateProviderService
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.app.domain.draft_candidates import DraftCandidateDirection
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings
from backend.app.drafting.domain.provider_dossier import DossierReadinessStatus, HandleResolutionStatus
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture
from backend.tests.test_draft_planning_services import context_and_rule_pack
from backend.tests.test_draft_run_pipeline import make_request


FORBIDDEN_FIELDS = {
    "sourceLedger",
    "rulePack",
    "articleDossier",
    "contextPacks",
    "candidatePool",
    "validationReport",
    "operationEnvelope",
    "payloadBudget",
    "runtimeBudget",
}


@dataclass
class FakeResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class RecordingAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeResult:
        self.calls.append(kwargs)
        return FakeResult(
            {
                "title": "Dossier candidate",
                "body": "A grounded maintenance decision with evidence and a clear limitation.",
                "rationale": "Uses one route and its evidence handles.",
                "usedEvidence": ["claim-1"],
                "ruleCoverage": ["rule-1"],
                "risks": [],
                "weaknesses": [],
            },
            {"id": "provider-result"},
        )


def test_writer_and_alternative_angle_profiles_preserve_required_context() -> None:
    access = ProviderDossierTestFixture.access()
    writer = WriterDossierFactory(access).build(plan_id="plan-1", operation_id="draftCandidate")
    route = AlternativeAngleDossierFactory(access).build("alternativeAngleRoute")
    challenger = WriterDossierFactory(access).build(plan_id=None, operation_id="alternativeAngleCandidate")

    assert writer.readiness_status is DossierReadinessStatus.DEGRADED
    assert route.readiness_status is DossierReadinessStatus.DEGRADED
    assert challenger.readiness_status is DossierReadinessStatus.DEGRADED
    assert all(not item.missing_required_inputs for item in (writer, route, challenger))
    assert set(writer.sent) >= {"postContract", "planning", "rhetoricalPlan", "evidence"}
    assert set(route.sent) >= {"candidates", "critiqueSignals", "postContract"}
    assert set(challenger.sent) >= {"postContract", "planning", "alternativeRoute", "evidence"}
    assert route.model_role == "anotherAngle"
    assert writer.model_role == challenger.model_role == "writer"
    assert all(item.runtime_migrated for item in (writer, route, challenger))


def test_writer_dossiers_exclude_full_artifacts_and_resolve_every_handle() -> None:
    access = ProviderDossierTestFixture.access()
    dossiers = (
        WriterDossierFactory(access).build(plan_id="plan-1"),
        AlternativeAngleDossierFactory(access).build(),
        WriterDossierFactory(access).build(plan_id=None, operation_id="alternativeAngleCandidate"),
    )

    for dossier in dossiers:
        serialized = json.dumps(dossier.provider_input(), ensure_ascii=False)
        assert all(f'"{field}"' not in serialized for field in FORBIDDEN_FIELDS)
        for handles in dossier.handles.values():
            assert all(access.resolve(handle).status is HandleResolutionStatus.RESOLVED for handle in handles)


def test_writer_dossier_profiles_fit_standard_operation_budgets() -> None:
    access = ProviderDossierTestFixture.access()
    dossiers = (
        WriterDossierFactory(access).build(plan_id="plan-1"),
        AlternativeAngleDossierFactory(access).build(),
        WriterDossierFactory(access).build(plan_id=None, operation_id="alternativeAngleCandidate"),
    )

    for dossier in dossiers:
        proof = ProviderInputBudgetGate().evaluate(
            operation_id=dossier.operation_id,
            draft_run_step=dossier.operation_id,
            provider_input=dossier.provider_input(),
            execution_mode="standard",
            model="test-model",
            model_role=dossier.model_role,
            generation_params={},
        )
        budget = proof.request_payload_fields()["payloadBudget"]
        assert budget.get("incident") is None
        assert budget["promptCharEstimate"] <= budget["limits"]["maxPromptChars"]


def test_missing_route_or_plan_blocks_only_the_affected_writer_operation() -> None:
    snapshot = ProviderDossierTestFixture.snapshot()
    snapshot["steps"]["validation"].pop("alternativeAngleTournament")
    access_without_route = type(ProviderDossierTestFixture.access()).from_snapshot(snapshot)

    missing_plan = WriterDossierFactory(ProviderDossierTestFixture.access()).build(plan_id="missing")
    missing_route = WriterDossierFactory(access_without_route).build(
        plan_id=None,
        operation_id="alternativeAngleCandidate",
    )

    assert missing_plan.readiness_status is DossierReadinessStatus.BLOCKED
    assert missing_plan.missing_required_inputs == ("rhetoricalPlan",)
    assert missing_route.readiness_status is DossierReadinessStatus.BLOCKED
    assert missing_route.missing_required_inputs == ("alternativeRoute",)


def test_draft_candidate_runtime_sends_only_budgeted_dossier_and_records_direct_proof(tmp_path) -> None:
    adapter = RecordingAdapter()
    service, ai_runs = _provider_service(tmp_path, adapter)
    context_summary, rule_pack = context_and_rule_pack()
    direction = DraftCandidateDirection(
        id="plan-1",
        title="Decision workbench",
        angle="Workflow before model",
        instruction="Open with a maintenance decision",
        rhetorical_plan_id="plan-1",
    )

    candidate, run_ids = service.create_one(
        request=make_request(),
        context_summary=context_summary,
        rule_pack=rule_pack,
        material_plan={"availableEvidence": ["claim-1"]},
        draft_strategy={"thesisAngle": "workflow before model"},
        direction=direction,
        provider_dossier=ProviderDossierTestFixture.writer_factory().build(plan_id="plan-1"),
        context_pack={"items": [{"full": "must not be sent"}]},
    )

    assert candidate["source"] == "openrouter"
    assert len(adapter.calls) == 1
    run = ai_runs.get_run(run_ids[0])
    assert run is not None
    assert run.request_payload["providerDossier"]["runtimeMigrated"] is True
    assert run.request_payload["payloadBudget"]["promptCharEstimate"] > 0
    assert run.request_payload["inputStats"] and run.request_payload["payloadStats"]
    user_payload = json.loads(adapter.calls[0]["messages"][1]["content"])
    assert set(user_payload) == {"providerInput", "repairContext", "outputLanguage"}
    assert all(field not in json.dumps(user_payload, ensure_ascii=False) for field in FORBIDDEN_FIELDS)


def test_blocked_writer_dossier_uses_fallback_without_provider_call(tmp_path) -> None:
    adapter = RecordingAdapter()
    service, ai_runs = _provider_service(tmp_path, adapter)
    context_summary, rule_pack = context_and_rule_pack()
    direction = DraftCandidateDirection("missing", "Missing", "Missing", "Missing", "missing")

    candidate, run_ids = service.create_one(
        request=make_request(),
        context_summary=context_summary,
        rule_pack=rule_pack,
        material_plan={},
        draft_strategy={},
        direction=direction,
        provider_dossier=ProviderDossierTestFixture.writer_factory().build(plan_id="missing"),
        context_pack=None,
    )

    assert adapter.calls == []
    assert candidate["fallbackUsed"] is True
    run = ai_runs.get_run(run_ids[0])
    assert run is not None
    assert run.request_payload["dossierBlocked"] is True
    assert run.request_payload["providerDossier"]["missingRequiredInputs"] == ["rhetoricalPlan"]


def _provider_service(tmp_path, adapter: RecordingAdapter) -> tuple[DraftCandidateProviderService, AiRunService]:
    ai_runs = AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))
    service = DraftCandidateProviderService(
        settings=BackendSettings(
            _env_file=None,
            OPENROUTER_API_KEY="sk-test-secret",
            OPENROUTER_DEFAULT_MODEL="writer-model",
            DRAFT_WRITER_MODEL="writer-model",
        ),
        ai_run_service=ai_runs,
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
        deterministic_candidate_service=DeterministicDraftCandidateService(),
    )
    return service, ai_runs
