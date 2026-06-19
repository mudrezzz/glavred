from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_draft_planning_service import DeterministicDraftPlanningService
from backend.app.application.draft_material_plan_service import DraftMaterialPlanService
from backend.app.application.draft_rule_pack_compiler import DraftRulePackCompiler
from backend.app.application.draft_run_context_builder import build_draft_run_context_summary
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_from_payload
from backend.app.application.draft_strategy_service import DraftStrategyService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings
from backend.tests.test_draft_run_context_builder import make_context, make_payload


@dataclass
class FakeOpenRouterResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class SuccessfulAdapter:
    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        if "thesisAngle" in kwargs["expected_keys"]:
            return FakeOpenRouterResult(strategy_payload(), {"id": "or-strategy", "model": "test"})
        return FakeOpenRouterResult(material_payload(), {"id": "or-material", "model": "test"})


class FailingAdapter:
    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        raise RuntimeError("provider boom sk-test-secret")


def test_material_plan_service_returns_openrouter_artifact(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = material_service(tmp_path, SuccessfulAdapter(), configured=True)

    result = service.create(context_summary=context_summary, rule_pack=rule_pack)

    assert result.artifact_payload["source"] == "openrouter"
    assert result.artifact_payload["fallbackUsed"] is False
    assert result.artifact_payload["materialPlan"]["availableEvidence"] == ["pilot usage data"]
    assert result.ai_run_id


def test_strategy_service_returns_openrouter_artifact_and_uses_material_plan(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = strategy_service(tmp_path, SuccessfulAdapter(), configured=True)

    result = service.create(
        context_summary=context_summary,
        rule_pack=rule_pack,
        material_plan={"availableEvidence": ["pilot usage data"]},
    )

    assert result.artifact_payload["source"] == "openrouter"
    assert result.artifact_payload["draftStrategy"]["argumentSequence"] == ["signal", "lesson"]
    run = ai_service(tmp_path).get_run(result.ai_run_id or "")
    assert run is not None
    assert run.request_payload["capabilityInput"]["materialPlan"]["availableEvidence"] == ["pilot usage data"]


def test_planning_services_use_deterministic_fallback_when_openrouter_missing(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = material_service(tmp_path, SuccessfulAdapter(), configured=False)

    result = service.create(context_summary=context_summary, rule_pack=rule_pack)

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert result.artifact_payload["fallbackUsed"] is True
    run = ai_service(tmp_path).get_run(result.ai_run_id or "")
    assert run is not None
    assert run.fallback_used is True


def test_provider_error_falls_back_without_exposing_token(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = material_service(tmp_path, FailingAdapter(), configured=True)

    result = service.create(context_summary=context_summary, rule_pack=rule_pack)

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert "sk-test-secret" not in result.artifact_payload["error"]


def context_and_rule_pack() -> tuple[dict[str, Any], dict[str, Any]]:
    payload = make_payload()
    payload["draftContext"] = make_context()
    context_summary = build_draft_run_context_summary(request_from_payload(payload), context_from_payload(payload))
    rule_pack = DraftRulePackCompiler().compile(context_summary).to_payload()
    return context_summary, rule_pack


def material_service(tmp_path, adapter: object, *, configured: bool) -> DraftMaterialPlanService:
    return DraftMaterialPlanService(
        settings=settings(configured),
        ai_run_service=ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
        deterministic_planning_service=DeterministicDraftPlanningService(),
    )


def strategy_service(tmp_path, adapter: object, *, configured: bool) -> DraftStrategyService:
    return DraftStrategyService(
        settings=settings(configured),
        ai_run_service=ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
        deterministic_planning_service=DeterministicDraftPlanningService(),
    )


def ai_service(tmp_path) -> AiRunService:
    return AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))


def settings(configured: bool) -> BackendSettings:
    return BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="sk-test-secret" if configured else "",
        OPENROUTER_DEFAULT_MODEL="test-model" if configured else "",
    )


def material_payload() -> dict[str, Any]:
    return {
        "availableEvidence": ["pilot usage data"],
        "missingEvidence": [],
        "riskyClaims": ["overclaiming"],
        "groundingPlan": ["use signal"],
        "sourceNotes": ["source note"],
        "openQuestions": [],
    }


def strategy_payload() -> dict[str, Any]:
    return {
        "thesisAngle": "workflow before model",
        "openingMove": "start with pilot gap",
        "argumentSequence": ["signal", "lesson"],
        "fabulaUsage": "research note",
        "ctaPlan": "check workflow",
        "forbiddenMoves": ["generic hype"],
        "toneNotes": ["research tone"],
    }
