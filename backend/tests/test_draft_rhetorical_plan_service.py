from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_rhetorical_plan_service import DeterministicRhetoricalPlanService
from backend.app.application.draft_rhetorical_plan_service import DraftRhetoricalPlanService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.tests.test_draft_planning_services import context_and_rule_pack, settings


@dataclass
class FakeOpenRouterResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class SuccessfulRhetoricalAdapter:
    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
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
    service = rhetorical_service(tmp_path, SuccessfulRhetoricalAdapter(), configured=True)

    result = service.create(
        context_summary=context_summary,
        context_artifact=context_artifact(),
        rule_pack=rule_pack,
        material_plan={"availableEvidence": ["evidence"]},
        draft_strategy={"thesisAngle": "angle"},
    )

    assert result.artifact_payload["source"] == "openrouter"
    assert result.artifact_payload["rhetoricalPlanSet"]["plans"][0]["id"] == "research"
    run = ai_service(tmp_path).get_run(result.ai_run_id or "")
    assert run is not None
    assert run.request_payload["draftRunStep"] == "rhetoricalPlans"

def test_rhetorical_plan_service_falls_back_without_openrouter(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = rhetorical_service(tmp_path, SuccessfulRhetoricalAdapter(), configured=False)

    result = service.create(
        context_summary=context_summary,
        context_artifact=context_artifact(),
        rule_pack=rule_pack,
        material_plan={},
        draft_strategy={},
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
    )

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert "sk-test-secret" not in result.artifact_payload["error"]

def rhetorical_service(tmp_path, adapter: object, *, configured: bool) -> DraftRhetoricalPlanService:
    return DraftRhetoricalPlanService(
        settings=settings(configured),
        ai_run_service=ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
        deterministic_plan_service=DeterministicRhetoricalPlanService(),
    )

def ai_service(tmp_path) -> AiRunService:
    return AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))

def context_artifact() -> dict[str, Any]:
    return {
        "postContract": {
            "title": "Post",
            "thesis": "Thesis",
            "cta": "Check rollout quality",
            "claims": [{"id": "claim-1"}],
            "riskNotes": ["Overclaiming"],
        }
    }
