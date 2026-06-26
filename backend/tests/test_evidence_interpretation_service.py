from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_evidence_interpretation import DeterministicEvidenceInterpretationService
from backend.app.application.evidence_interpretation_service import EvidenceInterpretationService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings


@dataclass
class FakeOpenRouterResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class SequenceAdapter:
    def __init__(self, payloads: list[dict[str, Any]]) -> None:
        self.payloads = payloads
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        self.calls.append(kwargs)
        payload = self.payloads.pop(0)
        return FakeOpenRouterResult(payload, {"id": f"or-{len(self.calls)}", "model": kwargs.get("model")})


def test_deterministic_interpretation_links_external_claims_to_implications() -> None:
    payload = DeterministicEvidenceInterpretationService().interpret(
        context_artifact=context_artifact(),
        rule_pack=rule_pack(),
    ).to_payload()

    assert payload["implications"][0]["claimIds"] == ["external-evidence-public-1"]
    assert payload["implications"][0]["publicEvidenceItemIds"] == ["public-1"]
    assert payload["usableExamples"][0]["summary"] == "Workflow adoption beats model demos."
    assert payload["limits"][0]["allowedUse"] == "needsQualification"
    assert payload["forbiddenOverclaims"][0]["allowedUse"] == "doNotState"


def test_provider_interpretation_uses_strategy_role_model_and_writes_trace(tmp_path) -> None:
    adapter = SequenceAdapter([provider_payload()])
    service = interpretation_service(tmp_path, adapter, configured=True, strategy_model="strategy-model")

    result = service.create(context_summary={"brief": {"id": "brief-1", "title": "Brief"}}, context_artifact=context_artifact(), rule_pack=rule_pack())

    assert result.artifact_payload["source"] == "openrouter"
    assert result.artifact_payload["fallbackUsed"] is False
    assert result.artifact_payload["evidenceInterpretation"]["implications"][0]["id"] == "implication-1"
    assert adapter.calls[0]["model"] == "strategy-model"
    assert result.artifact_payload["attempts"][0]["modelRole"] == "strategy"
    assert result.ai_run_id


def test_provider_empty_payload_triggers_repair_retry(tmp_path) -> None:
    adapter = SequenceAdapter([empty_payload(), provider_payload()])
    service = interpretation_service(tmp_path, adapter, configured=True)

    result = service.create(context_summary={}, context_artifact=context_artifact(), rule_pack=rule_pack())

    assert [call["model"] for call in adapter.calls] == ["test-model", "test-model"]
    assert result.artifact_payload["attempts"][0]["status"] == "error"
    assert result.artifact_payload["attempts"][1]["status"] == "accepted"
    assert result.artifact_payload["fallbackUsed"] is False


def test_provider_failures_use_backup_then_deterministic_fallback(tmp_path) -> None:
    adapter = SequenceAdapter([empty_payload(), empty_payload(), empty_payload()])
    service = interpretation_service(tmp_path, adapter, configured=True, backup_model="backup-model")

    result = service.create(context_summary={}, context_artifact=context_artifact(), rule_pack=rule_pack())

    assert [call["model"] for call in adapter.calls] == ["test-model", "test-model", "backup-model"]
    assert result.artifact_payload["source"] == "deterministicFallback"
    assert result.artifact_payload["fallbackUsed"] is True
    assert result.artifact_payload["attempts"][2]["backup"] is True
    assert result.artifact_payload["evidenceInterpretation"]["implications"]


def test_unconfigured_provider_uses_deterministic_without_secret(tmp_path) -> None:
    adapter = SequenceAdapter([provider_payload()])
    service = interpretation_service(tmp_path, adapter, configured=False)

    result = service.create(context_summary={}, context_artifact=context_artifact(), rule_pack=rule_pack())

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert result.artifact_payload["fallbackUsed"] is True
    assert adapter.calls == []


def interpretation_service(
    tmp_path,
    adapter: SequenceAdapter,
    *,
    configured: bool,
    backup_model: str = "",
    strategy_model: str = "",
) -> EvidenceInterpretationService:
    return EvidenceInterpretationService(
        settings=BackendSettings(
            _env_file=None,
            OPENROUTER_API_KEY="sk-test-secret" if configured else "",
            OPENROUTER_DEFAULT_MODEL="test-model" if configured else "",
            OPENROUTER_BACKUP_MODEL=backup_model,
            DRAFT_STRATEGY_MODEL=strategy_model,
        ),
        ai_run_service=AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3")),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
    )


def context_artifact() -> dict[str, Any]:
    return {
        "postContract": {"thesis": "Workflow before model", "claims": [{"id": "external-evidence-public-1"}]},
        "sourceLedger": {
            "claims": [{
                "id": "external-evidence-public-1",
                "type": "externalEvidenceClaim",
                "statement": "Public evidence says workflow adoption matters more than model demos.",
                "allowedUse": "needsQualification",
                "confidence": "medium",
                "provenance": {
                    "publicEvidenceItemId": "public-1",
                    "sourceTitle": "Independent report",
                    "sourceUrl": "https://example.com/report",
                    "snippet": "Workflow adoption beats model demos.",
                },
            }],
            "metadata": {"externalClaimCount": 1},
        },
        "publicEvidence": {
            "items": [{
                "id": "public-1",
                "sourceTitle": "Independent report",
                "sourceUrl": "https://example.com/report",
                "snippet": "Workflow adoption beats model demos.",
            }]
        },
        "evidenceSynthesis": {"externalClaims": [{"publicEvidenceItemId": "public-1"}]},
    }


def rule_pack() -> dict[str, Any]:
    return {"ruleRegistrySnapshot": {"rules": [{"id": "rule-grounding", "severity": "hard"}]}}


def provider_payload() -> dict[str, Any]:
    return {
        "implications": [{
            "id": "implication-1",
            "title": "Workflow proof",
            "summary": "Use the source to sharpen the workflow adoption argument.",
            "sourceIds": ["https://example.com/report"],
            "publicEvidenceItemIds": ["public-1"],
            "claimIds": ["external-evidence-public-1"],
            "ruleIds": ["rule-grounding"],
            "confidence": "medium",
            "allowedUse": "needsQualification",
            "reason": "Accepted source claim.",
        }],
        "tensions": [],
        "usableExamples": [],
        "limits": [],
        "forbiddenOverclaims": [],
        "authorPositionLinks": [],
        "readerValueHooks": [],
        "recommendedUseByPlan": [],
        "rejectedEvidenceUses": [],
        "warnings": [],
    }


def empty_payload() -> dict[str, Any]:
    return {
        "implications": [],
        "tensions": [],
        "usableExamples": [],
        "limits": [],
        "forbiddenOverclaims": [],
        "authorPositionLinks": [],
        "readerValueHooks": [],
        "recommendedUseByPlan": [],
        "rejectedEvidenceUses": [],
        "warnings": [],
    }
