from typing import Any

from backend.tests.test_draft_planning_services import context_and_rule_pack
from backend.tests.rhetorical_plan_test_helpers import (
    FakeOpenRouterResult,
    ai_service,
    context_artifact,
    rhetorical_service,
)
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


class SuccessfulRhetoricalAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        self.calls.append(kwargs)
        return FakeOpenRouterResult(
            {
                "plans": [
                    {
                        "id": "research",
                        "title": "Research route",
                        "angle": "Explain through evidence",
                        "openingMove": "Start from the source signal",
                        "moves": [{"label": "Evidence", "purpose": "Ground the thesis", "claimIds": ["claim-1"]}],
                        "claimsToUse": [{"claimId": "claim-1", "use": "support"}],
                        "claimIdsToAvoid": ["risk-1"],
                        "requiredRuleIds": ["rule-1"],
                        "sizeIntent": "standard",
                        "ctaRoute": "Ask readers to check the rollout path",
                        "risks": ["Overclaiming"],
                        "whyThisPlan": "It fits the contract.",
                    },
                    {"id": "practical", "title": "Practical route", "angle": "Turn into checks"},
                ]
            },
            {"id": "or-plans", "model": "test"},
        )


class FailingRhetoricalAdapter:
    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        raise RuntimeError("provider failed sk-test-secret")


def test_rhetorical_plan_service_returns_openrouter_artifact(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    adapter = SuccessfulRhetoricalAdapter()
    service = rhetorical_service(tmp_path, adapter, configured=True)

    result = service.create(
        context_summary=context_summary,
        context_artifact=context_artifact(),
        rule_pack=rule_pack,
        material_plan={"availableEvidence": ["evidence"]},
        draft_strategy={"thesisAngle": "angle"},
        provider_dossier=ProviderDossierTestFixture.planning_dossier("rhetoricalPlans"),
    )

    assert result.artifact_payload["source"] == "openrouter"
    assert result.artifact_payload["rhetoricalPlanSet"]["plans"][0]["id"] == "research"
    run = ai_service(tmp_path).get_run(result.ai_run_id or "")
    assert run is not None
    assert run.request_payload["draftRunStep"] == "rhetoricalPlans"
    assert run.request_payload["operationId"] == "rhetoricalPlans"
    assert run.request_payload["providerInput"]["materialPlan"]["availableEvidence"] == ["claim-1", "claim-2"]
    assert run.request_payload["payloadBudget"]["profileId"] == "rhetoricalPlans"
    assert run.request_payload["inputStats"]["modelRole"] == "strategy"
    assert run.request_payload["payloadStats"]["payloadBudget"]["profileId"] == "rhetoricalPlans"
    assert result.artifact_payload["attempts"][0]["status"] == "accepted"
    assert run.request_payload["providerDossier"]["runtimeMigrated"] is True
    assert "rulePack" not in run.request_payload["providerInput"]
    assert run.request_payload["payloadBudget"].get("incident") is None
    assert "claim-1" in str(adapter.calls[0]["messages"])
    assert "rule-1" in str(adapter.calls[0]["messages"])

def test_rhetorical_plan_service_falls_back_without_openrouter(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = rhetorical_service(tmp_path, SuccessfulRhetoricalAdapter(), configured=False)

    result = service.create(
        context_summary=context_summary,
        context_artifact=context_artifact(),
        rule_pack=rule_pack,
        material_plan={},
        draft_strategy={},
        provider_dossier=ProviderDossierTestFixture.planning_dossier("rhetoricalPlans"),
    )

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert len(result.artifact_payload["rhetoricalPlanSet"]["plans"]) == 3

def test_rhetorical_plan_provider_error_falls_back_without_secret(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = rhetorical_service(tmp_path, FailingRhetoricalAdapter(), configured=True)

    result = service.create(
        context_summary=context_summary,
        context_artifact=context_artifact(),
        rule_pack=rule_pack,
        material_plan={},
        draft_strategy={},
        provider_dossier=ProviderDossierTestFixture.planning_dossier("rhetoricalPlans"),
    )

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert "sk-test-secret" not in result.artifact_payload["error"]
