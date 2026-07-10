from typing import Any

from backend.app.drafting.application.dossiers.provider_dossier_factories import PlanningDossierFactory
from backend.app.drafting.application.context.draft_run_context_access import DraftRunContextAccessService
from backend.app.drafting.application.planning.deterministic_draft_planning_service import DeterministicDraftPlanningService
from backend.app.drafting.application.planning.draft_strategy_service import DraftStrategyService
from backend.app.drafting.domain.provider_dossier import ProviderDossier
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture
from backend.tests.rhetorical_plan_test_helpers import context_artifact, rhetorical_service
from backend.tests.test_draft_material_plan_service import context_and_rule_pack, material_service
from backend.tests.test_draft_planning_services import ai_service, settings


class RejectingProviderAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        raise AssertionError("blocked dossier must not call provider")


def test_operation_specific_missing_inputs_block_each_planning_dossier() -> None:
    material_snapshot = ProviderDossierTestFixture.snapshot()
    material_snapshot["steps"].pop("postContract")
    material_snapshot["steps"].pop("publicEvidence")
    strategy_snapshot = ProviderDossierTestFixture.snapshot()
    strategy_snapshot["steps"].pop("materialPlan")
    rhetorical_snapshot = ProviderDossierTestFixture.snapshot()
    rhetorical_snapshot["steps"].pop("strategy")

    material = _dossier(material_snapshot, "materialPlan")
    strategy = _dossier(strategy_snapshot, "strategy")
    rhetorical = _dossier(rhetorical_snapshot, "rhetoricalPlans")

    assert material.readiness_status.value == "blocked"
    assert material.missing_required_inputs == ("postContract",)
    assert strategy.missing_required_inputs == ("materialPlan",)
    assert rhetorical.missing_required_inputs == ("draftStrategy",)


def test_blocked_material_dossier_uses_fallback_without_provider_call(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    snapshot = ProviderDossierTestFixture.snapshot()
    snapshot["steps"].pop("postContract")
    adapter = RejectingProviderAdapter()
    service = material_service(tmp_path, adapter, configured=True)

    result = service.create(
        context_summary=context_summary,
        rule_pack=rule_pack,
        provider_dossier=_dossier(snapshot, "materialPlan"),
    )

    assert adapter.calls == []
    assert result.artifact_payload["fallbackUsed"] is True
    assert "Planning dossier blocked" in result.artifact_payload["error"]


def test_blocked_strategy_and_rhetorical_dossiers_skip_provider(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    strategy_snapshot = ProviderDossierTestFixture.snapshot()
    strategy_snapshot["steps"].pop("materialPlan")
    rhetorical_snapshot = ProviderDossierTestFixture.snapshot()
    rhetorical_snapshot["steps"].pop("strategy")
    strategy_adapter = RejectingProviderAdapter()
    rhetorical_adapter = RejectingProviderAdapter()
    strategy_service = DraftStrategyService(
        settings=settings(configured=True),
        ai_run_service=ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=strategy_adapter,
        deterministic_planning_service=DeterministicDraftPlanningService(),
    )

    strategy_result = strategy_service.create(
        context_summary=context_summary,
        rule_pack=rule_pack,
        material_plan={},
        provider_dossier=_dossier(strategy_snapshot, "strategy"),
    )
    rhetorical_result = rhetorical_service(
        tmp_path,
        rhetorical_adapter,
        configured=True,
    ).create(
        context_summary=context_summary,
        context_artifact=context_artifact(),
        rule_pack=rule_pack,
        material_plan={},
        draft_strategy={},
        provider_dossier=_dossier(rhetorical_snapshot, "rhetoricalPlans"),
    )

    assert strategy_adapter.calls == []
    assert rhetorical_adapter.calls == []
    assert strategy_result.artifact_payload["fallbackUsed"] is True
    assert rhetorical_result.artifact_payload["fallbackUsed"] is True


def _dossier(snapshot: dict[str, Any], operation_id: str) -> ProviderDossier:
    access = DraftRunContextAccessService.from_snapshot(snapshot)
    return PlanningDossierFactory(access).build(operation_id)
