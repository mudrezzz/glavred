from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.planning.deterministic_draft_planning_service import DeterministicDraftPlanningService
from backend.app.drafting.application.planning.draft_material_plan_service import DraftMaterialPlanService
from backend.app.drafting.application.evidence.draft_rule_pack_compiler import DraftRulePackCompiler
from backend.app.drafting.application.artifacts.draft_run_context_builder import build_draft_run_context_summary
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_from_payload
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
        return FakeOpenRouterResult(material_payload(), {"id": "or-material", "model": kwargs.get("model")})


class FailingAdapter:
    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        raise RuntimeError("provider boom sk-test-secret")


class SequenceAdapter:
    def __init__(self, payloads: list[dict[str, Any]]) -> None:
        self.payloads = payloads
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        self.calls.append(kwargs)
        payload = self.payloads.pop(0)
        return FakeOpenRouterResult(payload, {"id": f"or-{len(self.calls)}", "model": kwargs.get("model")})


def test_material_plan_service_returns_openrouter_artifact(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    adapter = SuccessfulAdapter()
    service = material_service(tmp_path, adapter, configured=True, strategy_model="strategy-model")

    result = service.create(context_summary=context_summary, rule_pack=rule_pack, provider_dossier=ProviderDossierTestFixture.planning_dossier())

    assert result.artifact_payload["source"] == "openrouter"
    assert result.artifact_payload["fallbackUsed"] is False
    assert result.artifact_payload["materialPlan"]["availableEvidence"] == ["claim-1"]
    assert result.artifact_payload["evidenceAccountability"]["valid"] is True
    assert adapter.calls[0]["model"] == "strategy-model"
    assert result.artifact_payload["attempts"][0]["modelRole"] == "strategy"
    assert result.artifact_payload["attempts"][0]["selectedModel"] == "strategy-model"
    assert result.ai_run_id
    run = AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3")).get_run(result.ai_run_id or "")
    assert run is not None
    assert run.request_payload["operationId"] == "materialPlan"
    assert run.request_payload["providerInput"]
    assert run.request_payload["payloadBudget"]["profileId"] == "materialPlan"
    assert run.request_payload["inputStats"]["modelRole"] == "strategy"
    assert run.request_payload["payloadStats"]["payloadBudget"]["profileId"] == "materialPlan"
    assert run.request_payload["providerDossier"]["runtimeMigrated"] is True
    assert run.request_payload["providerInput"]["dossierId"] == "planningDossier:materialPlan"
    assert "rulePack" not in run.request_payload["providerInput"]
    assert run.request_payload["payloadBudget"].get("incident") is None
    assert "claim-1" in str(adapter.calls[0]["messages"])
    assert "rule-1" in str(adapter.calls[0]["messages"])


def test_material_plan_retries_when_projected_evidence_is_ignored(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack_with_ledger()
    adapter = SequenceAdapter([empty_material_payload(), accountable_material_payload()])
    service = material_service(tmp_path, adapter, configured=True)

    result = service.create(context_summary=context_summary, rule_pack=rule_pack, provider_dossier=ProviderDossierTestFixture.planning_dossier(), context_artifact=context_summary)

    assert len(adapter.calls) == 2
    assert result.artifact_payload["attempts"][0]["status"] == "rejected"
    assert result.artifact_payload["attempts"][1]["status"] == "accepted"
    assert result.artifact_payload["materialPlan"]["availableEvidence"] == ["external-claim-1"]
    repair_run = AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3")).get_run(
        result.artifact_payload["attempts"][1]["aiRunId"]
    )
    assert repair_run is not None
    repair_context = repair_run.request_payload["providerInput"]["repairContext"]
    assert set(repair_context["previousAttempt"]) == {"label", "status", "model", "backup"}
    assert "validation" not in repair_context["previousAttempt"]
    assert repair_run.request_payload["payloadBudget"].get("incident") is None
    assert result.ai_run_ids == [
        result.artifact_payload["attempts"][0]["aiRunId"],
        result.artifact_payload["attempts"][1]["aiRunId"],
    ]


def test_material_plan_uses_backup_model_after_primary_retries_fail(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack_with_ledger()
    adapter = SequenceAdapter([empty_material_payload(), empty_material_payload(), accountable_material_payload()])
    service = material_service(tmp_path, adapter, configured=True, backup_model="backup-model")

    result = service.create(context_summary=context_summary, rule_pack=rule_pack, provider_dossier=ProviderDossierTestFixture.planning_dossier(), context_artifact=context_summary)

    assert [call["model"] for call in adapter.calls] == ["test-model", "test-model", "backup-model"]
    assert result.artifact_payload["attempts"][2]["backup"] is True
    assert result.artifact_payload["fallbackUsed"] is False


def test_material_plan_uses_emergency_fallback_after_all_attempts_fail(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack_with_ledger()
    adapter = SequenceAdapter([empty_material_payload(), empty_material_payload()])
    service = material_service(tmp_path, adapter, configured=True)

    result = service.create(context_summary=context_summary, rule_pack=rule_pack, provider_dossier=ProviderDossierTestFixture.planning_dossier(), context_artifact=context_summary)

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert result.artifact_payload["fallbackUsed"] is True
    assert result.artifact_payload["attempts"][-1]["label"] == "emergency-fallback"
    assert result.artifact_payload["usableEvidenceCandidates"][0]["claimId"] == "external-claim-1"


def test_material_plan_falls_back_without_exposing_token(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = material_service(tmp_path, FailingAdapter(), configured=True)

    result = service.create(context_summary=context_summary, rule_pack=rule_pack, provider_dossier=ProviderDossierTestFixture.planning_dossier())

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert "sk-test-secret" not in result.artifact_payload["error"]


def test_material_plan_uses_deterministic_fallback_when_openrouter_missing(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = material_service(tmp_path, SuccessfulAdapter(), configured=False)

    result = service.create(context_summary=context_summary, rule_pack=rule_pack, provider_dossier=ProviderDossierTestFixture.planning_dossier())

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert result.artifact_payload["fallbackUsed"] is True


def context_and_rule_pack() -> tuple[dict[str, Any], dict[str, Any]]:
    payload = make_payload()
    payload["draftContext"] = make_context()
    context_summary = build_draft_run_context_summary(request_from_payload(payload), context_from_payload(payload))
    rule_pack = DraftRulePackCompiler().compile(context_summary).to_payload()
    return context_summary, rule_pack


def context_and_rule_pack_with_ledger() -> tuple[dict[str, Any], dict[str, Any]]:
    context_summary, _ = context_and_rule_pack()
    context_summary = {
        **context_summary,
        "sourceLedger": {
            "claims": [{
                "id": "external-claim-1",
                "type": "externalEvidenceClaim",
                "statement": "Public evidence shows workflow integration improves AI adoption.",
                "source": "publicEvidence",
                "allowedUse": "needsQualification",
                "confidence": "medium",
                "provenance": {"sourceTitle": "Independent report", "sourceUrl": "https://example.com/report"},
            }],
            "warnings": [],
            "metadata": {"claimCount": 1, "externalClaimCount": 1, "warningCount": 0},
        },
        "postContract": {
            "status": "created",
            "claims": [{"id": "external-claim-1", "allowedUse": "needsQualification"}],
        },
    }
    return context_summary, DraftRulePackCompiler().compile(context_summary).to_payload()


def material_service(tmp_path, adapter: object, *, configured: bool, backup_model: str = "", strategy_model: str = "") -> DraftMaterialPlanService:
    return DraftMaterialPlanService(
        settings=settings(configured, backup_model=backup_model, strategy_model=strategy_model),
        ai_run_service=AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3")),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
        deterministic_planning_service=DeterministicDraftPlanningService(),
    )


def settings(configured: bool, backup_model: str = "", strategy_model: str = "") -> BackendSettings:
    return BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="sk-test-secret" if configured else "",
        OPENROUTER_DEFAULT_MODEL="test-model" if configured else "",
        OPENROUTER_BACKUP_MODEL=backup_model,
        DRAFT_STRATEGY_MODEL=strategy_model,
    )


def material_payload() -> dict[str, Any]:
    return {
        "availableEvidence": ["claim-1"],
        "rejectedEvidence": [],
        "rejectionReasons": [],
        "claimsRequiringAttribution": ["claim-1"],
        "qualifiedClaims": [],
        "missingEvidence": [],
        "riskyClaims": ["overclaiming"],
        "groundingPlan": ["use signal"],
        "sourceNotes": ["source note"],
        "openQuestions": [],
    }


def accountable_material_payload() -> dict[str, Any]:
    payload = material_payload()
    payload["availableEvidence"] = ["external-claim-1"]
    payload["claimsRequiringAttribution"] = ["external-claim-1"]
    payload["qualifiedClaims"] = ["external-claim-1"]
    return payload


def empty_material_payload() -> dict[str, Any]:
    return {
        "availableEvidence": [],
        "rejectedEvidence": [],
        "rejectionReasons": [],
        "claimsRequiringAttribution": [],
        "qualifiedClaims": [],
        "missingEvidence": [],
        "riskyClaims": [],
        "groundingPlan": [],
        "sourceNotes": [],
        "openQuestions": [],
    }
