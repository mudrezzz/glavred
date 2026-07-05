from dataclasses import dataclass
import json
import time
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.evidence.deterministic_evidence_interpretation import DeterministicEvidenceInterpretationService
from backend.app.drafting.application.evidence.evidence_interpretation_service import EvidenceInterpretationService
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


class SlowThenSuccessAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            time.sleep(0.2)
        return FakeOpenRouterResult(provider_payload(), {"id": f"or-{len(self.calls)}", "model": kwargs.get("model")})


class FakeProgress:
    def __init__(self) -> None:
        self.operations: list[dict[str, Any]] = []

    def start_operation(self, operation_id: str, **kwargs: Any) -> None:
        self.operations.append({"id": operation_id, "status": "running", **kwargs})

    def complete_operation(self, operation_id: str, **kwargs: Any) -> None:
        self.operations.append({"id": operation_id, "status": "succeeded", **kwargs})

    def fail_operation(self, operation_id: str, error: str, **kwargs: Any) -> None:
        self.operations.append({"id": operation_id, "status": "failed", "error": error, **kwargs})


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
    assert result.artifact_payload["operationEnvelope"]["operationId"] == "evidenceInterpretation"
    assert result.artifact_payload["operationEnvelope"]["status"] == "accepted"
    assert result.artifact_payload["operationEnvelope"]["payloadStats"]["payloadBudget"]["profileId"] == "evidenceInterpretation"
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
    assert result.artifact_payload["operationEnvelope"]["status"] == "fallback"
    assert result.artifact_payload["operationEnvelope"]["incident"]["incidentType"] == "deterministicFallback"
    assert result.artifact_payload["evidenceInterpretation"]["implications"]


def test_provider_timeout_records_failed_attempt_and_continues_to_repair(tmp_path) -> None:
    adapter = SlowThenSuccessAdapter()
    progress = FakeProgress()
    service = interpretation_service(
        tmp_path,
        adapter,
        configured=True,
        timeout_seconds=0.05,
    )

    result = service.create(
        context_summary={},
        context_artifact=context_artifact(),
        rule_pack=rule_pack(),
        progress=progress,  # type: ignore[arg-type]
    )

    assert result.artifact_payload["fallbackUsed"] is False
    assert [attempt["status"] for attempt in result.artifact_payload["attempts"]] == ["timeout", "accepted"]
    assert "OperationTimeoutError" in result.artifact_payload["attempts"][0]["error"]
    assert result.artifact_payload["attempts"][0]["incident"]["incidentType"] == "providerTimeout"
    assert result.artifact_payload["operationEnvelope"]["timeoutProfile"]["attemptTimeoutSeconds"] == 0.05
    assert len(result.ai_run_ids) == 2
    assert any(operation["status"] == "failed" and operation["id"] == "evidence-interpretation-primary" for operation in progress.operations)
    assert any(operation["status"] == "succeeded" and operation["id"] == "evidence-interpretation-primary-repair" for operation in progress.operations)


def test_provider_interpretation_uses_compact_payload_and_records_input_stats(tmp_path) -> None:
    adapter = SequenceAdapter([provider_payload()])
    service = interpretation_service(tmp_path, adapter, configured=True)

    result = service.create(context_summary={}, context_artifact=large_context_artifact(), rule_pack=large_rule_pack())

    user_payload = json.loads(adapter.calls[0]["messages"][1]["content"])
    compact_rules = user_payload["ruleRegistrySnapshot"]["rules"]
    attempt_stats = result.artifact_payload["attempts"][0]["inputStats"]
    assert len(compact_rules) < 120
    assert len(compact_rules) <= 40
    assert attempt_stats["originalRuleCount"] == 120
    assert attempt_stats["compactRuleCount"] == len(compact_rules)
    assert attempt_stats["promptCharEstimate"] > 0
    assert result.artifact_payload["attempts"][0]["payloadStats"]["payloadBudget"]["trimmedCounts"]["rules"] > 0


def test_unconfigured_provider_uses_deterministic_without_secret(tmp_path) -> None:
    adapter = SequenceAdapter([provider_payload()])
    service = interpretation_service(tmp_path, adapter, configured=False)

    result = service.create(context_summary={}, context_artifact=context_artifact(), rule_pack=rule_pack())

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert result.artifact_payload["fallbackUsed"] is True
    assert result.artifact_payload["operationEnvelope"]["incident"]["incidentType"] == "deterministicFallback"
    assert adapter.calls == []


def interpretation_service(
    tmp_path,
    adapter: Any,
    *,
    configured: bool,
    backup_model: str = "",
    strategy_model: str = "",
    timeout_seconds: float = 75,
) -> EvidenceInterpretationService:
    return EvidenceInterpretationService(
        settings=BackendSettings(
            _env_file=None,
            OPENROUTER_API_KEY="sk-test-secret" if configured else "",
            OPENROUTER_DEFAULT_MODEL="test-model" if configured else "",
            OPENROUTER_BACKUP_MODEL=backup_model,
            DRAFT_STRATEGY_MODEL=strategy_model,
            DRAFT_EVIDENCE_INTERPRETATION_TIMEOUT_SECONDS=timeout_seconds,
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


def large_rule_pack() -> dict[str, Any]:
    rules = []
    for index in range(120):
        rules.append({
            "id": f"rule-{index}",
            "title": f"Rule {index}",
            "severity": "soft",
            "scope": "generic",
        })
    rules[5].update({"id": "rule-evidence-hard", "severity": "hard", "scope": "evidence"})
    rules[6].update({"id": "rule-style", "scope": "style"})
    rules[7].update({"id": "rule-attribution", "scope": "attribution"})
    return {"ruleRegistrySnapshot": {"rules": rules, "metadata": {"version": "test"}}}


def large_context_artifact() -> dict[str, Any]:
    artifact = context_artifact()
    artifact["sourceLedger"]["claims"] = [
        {
            "id": f"external-evidence-public-{index}",
            "type": "externalEvidenceClaim",
            "statement": f"External claim {index}",
            "allowedUse": "needsQualification",
            "confidence": "medium",
            "provenance": {
                "publicEvidenceItemId": f"public-{index}",
                "sourceTitle": f"Report {index}",
                "sourceUrl": f"https://example.com/report-{index}",
                "snippet": f"Snippet {index}",
            },
        }
        for index in range(40)
    ]
    artifact["sourceLedger"]["metadata"] = {"externalClaimCount": 40}
    artifact["publicEvidence"]["items"] = [
        {
            "id": f"public-{index}",
            "sourceTitle": f"Report {index}",
            "sourceUrl": f"https://example.com/report-{index}",
            "snippet": f"Snippet {index}",
        }
        for index in range(40)
    ]
    artifact["evidenceSynthesis"] = {
        "externalClaims": [
            {"id": f"synthesis-{index}", "statement": f"Synthesis claim {index}", "publicEvidenceItemId": f"public-{index}"}
            for index in range(40)
        ]
    }
    return artifact


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
