from typing import Any

from backend.tests.test_draft_planning_services import context_and_rule_pack
from backend.tests.rhetorical_plan_test_helpers import FakeOpenRouterResult, context_artifact, rhetorical_service
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


class SequentialRhetoricalAdapter:
    def __init__(self, outcomes: list[Any]) -> None:
        self.outcomes = outcomes
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return FakeOpenRouterResult(outcome, {"id": f"or-{len(self.calls)}", "model": kwargs.get("model")})


def test_rhetorical_plan_retries_after_malformed_primary(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    adapter = SequentialRhetoricalAdapter([ValueError("not object"), rhetorical_payload()])
    service = rhetorical_service(tmp_path, adapter, configured=True)

    result = service.create(
        context_summary=context_summary,
        context_artifact=context_artifact(),
        rule_pack=rule_pack,
        material_plan={},
        draft_strategy={},
        provider_dossier=ProviderDossierTestFixture.planning_dossier("rhetoricalPlans"),
    )

    assert result.artifact_payload["source"] == "openrouter"
    assert [attempt["label"] for attempt in result.artifact_payload["attempts"]] == ["primary", "primary-repair"]
    assert result.artifact_payload["attempts"][0]["status"] == "error"
    assert result.artifact_payload["attempts"][1]["status"] == "accepted"
    assert adapter.calls[1]["model"] == "test-model"
    assert result.ai_run_ids and len(result.ai_run_ids) == 2


def test_rhetorical_plan_uses_backup_model_after_repair_failure(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    adapter = SequentialRhetoricalAdapter([ValueError("not object"), ValueError("still not object"), rhetorical_payload()])
    service = rhetorical_service(tmp_path, adapter, configured=True, backup_model="backup-model", strategy_model="strategy-model")

    result = service.create(
        context_summary=context_summary,
        context_artifact=context_artifact(),
        rule_pack=rule_pack,
        material_plan={},
        draft_strategy={},
        provider_dossier=ProviderDossierTestFixture.planning_dossier("rhetoricalPlans"),
    )

    assert result.artifact_payload["source"] == "openrouter"
    assert [attempt["label"] for attempt in result.artifact_payload["attempts"]] == ["primary", "primary-repair", "backup"]
    assert result.artifact_payload["attempts"][2]["backup"] is True
    assert result.artifact_payload["attempts"][0]["selectedModel"] == "strategy-model"
    assert result.artifact_payload["attempts"][0]["modelRole"] == "strategy"
    assert adapter.calls[2]["model"] == "backup-model"


def test_rhetorical_plan_all_failed_attempts_fallback_with_trace(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    adapter = SequentialRhetoricalAdapter([ValueError("not object"), ValueError("still not object")])
    service = rhetorical_service(tmp_path, adapter, configured=True)

    result = service.create(
        context_summary=context_summary,
        context_artifact=context_artifact(),
        rule_pack=rule_pack,
        material_plan={},
        draft_strategy={},
        provider_dossier=ProviderDossierTestFixture.planning_dossier("rhetoricalPlans"),
    )

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert result.artifact_payload["fallbackUsed"] is True
    assert [attempt["status"] for attempt in result.artifact_payload["attempts"]] == ["error", "error", "fallback"]
    assert result.ai_run_ids and len(result.ai_run_ids) == 3


def rhetorical_payload() -> dict[str, Any]:
    return {
        "plans": [
            {"id": "research", "title": "Research route", "angle": "Explain through evidence"},
            {"id": "practical", "title": "Practical route", "angle": "Turn into checks"},
        ]
    }
