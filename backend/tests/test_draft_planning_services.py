from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.planning.deterministic_draft_planning_service import DeterministicDraftPlanningService
from backend.app.drafting.application.evidence.draft_rule_pack_compiler import DraftRulePackCompiler
from backend.app.drafting.application.artifacts.draft_run_context_builder import build_draft_run_context_summary
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_from_payload
from backend.app.drafting.application.planning.draft_strategy_service import DraftStrategyService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings
from backend.tests.test_draft_run_context_builder import make_context, make_payload
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


@dataclass
class FakeOpenRouterResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class SuccessfulAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        self.calls.append(kwargs)
        return FakeOpenRouterResult(strategy_payload(), {"id": "or-strategy", "model": "test"})


def test_strategy_service_returns_openrouter_artifact_and_uses_material_plan(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    adapter = SuccessfulAdapter()
    service = DraftStrategyService(
        settings=settings(configured=True),
        ai_run_service=ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
        deterministic_planning_service=DeterministicDraftPlanningService(),
    )

    result = service.create(
        context_summary=context_summary,
        rule_pack=rule_pack,
        material_plan={"availableEvidence": ["pilot usage data"]},
        provider_dossier=ProviderDossierTestFixture.planning_dossier("strategy"),
        context_pack={"role": "strategy", "items": [{"cardId": "claim-1", "summary": "usable claim"}]},
    )

    assert result.artifact_payload["source"] == "openrouter"
    assert result.artifact_payload["draftStrategy"]["argumentSequence"] == ["signal", "lesson"]
    run = ai_service(tmp_path).get_run(result.ai_run_id or "")
    assert run is not None
    assert run.request_payload["operationId"] == "strategy"
    assert run.request_payload["providerInput"]["materialPlan"]["availableEvidence"] == ["claim-1", "claim-2"]
    assert run.request_payload["payloadBudget"]["profileId"] == "draftStrategy"
    assert run.request_payload["payloadBudget"]["operationAlias"] == "strategy"
    assert run.request_payload["inputStats"]["modelRole"] == "strategy"
    assert run.request_payload["payloadStats"]["payloadBudget"]["profileId"] == "draftStrategy"
    assert run.request_payload["providerDossier"]["runtimeMigrated"] is True
    assert "rulePack" not in run.request_payload["providerInput"]
    assert run.request_payload["payloadBudget"].get("incident") is None
    assert "claim-1" in str(adapter.calls[0]["messages"])
    assert "rule-1" in str(adapter.calls[0]["messages"])


def context_and_rule_pack() -> tuple[dict[str, Any], dict[str, Any]]:
    payload = make_payload()
    payload["draftContext"] = make_context()
    context_summary = build_draft_run_context_summary(request_from_payload(payload), context_from_payload(payload))
    rule_pack = DraftRulePackCompiler().compile(context_summary).to_payload()
    return context_summary, rule_pack


def ai_service(tmp_path) -> AiRunService:
    return AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))


def settings(configured: bool) -> BackendSettings:
    return BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="sk-test-secret" if configured else "",
        OPENROUTER_DEFAULT_MODEL="test-model" if configured else "",
    )


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
