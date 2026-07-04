from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.draft_editorial_critique_service import DraftEditorialCritiqueService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings


@dataclass
class FakeJsonResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class SequenceAdapter:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeJsonResult:
        self.calls.append(kwargs)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return FakeJsonResult(response, {"id": f"call-{len(self.calls)}", "model": kwargs.get("model")})


def test_editorial_critique_success_stores_report_and_child_ai_run(tmp_path) -> None:
    ai = ai_service(tmp_path)
    adapter = SequenceAdapter([critique_payload()])
    service = service_with(tmp_path, adapter, ai=ai)

    result = service.critique(
        draft_artifact=draft_artifact(),
        context_artifact=context_artifact(),
        rule_pack=rule_pack(),
        material_plan={"availableEvidence": ["source-backed example"]},
        deterministic_report={"candidateReports": []},
        llm_validation_report={"candidateReports": []},
    )

    assert result.artifact_payload["status"] == "warning"
    assert result.artifact_payload["summary"]["findingCount"] == 1
    report = result.artifact_payload["candidateReports"][0]
    assert report["editorialRisk"] == "high"
    assert report["findings"][0]["validatorId"] == "critic.genericAiProse"
    assert report["observations"][0]["criticId"] == "critic.tension"
    assert len(result.ai_run_ids) == 1
    run = ai.get_run(result.ai_run_ids[0])
    assert run is not None
    assert run.request_payload["draftRunStep"] == "editorialCritique"
    assert run.request_payload["modelRole"] == "critic"
    assert run.request_payload["selectedModel"] == "critic-model"


def test_editorial_critique_retries_malformed_json_and_uses_repair(tmp_path) -> None:
    adapter = SequenceAdapter([
        {"summary": "bad", "findings": "not-list", "observations": []},
        critique_payload(editorial_risk="medium"),
    ])
    service = service_with(tmp_path, adapter)

    result = service.critique(
        draft_artifact=draft_artifact(),
        context_artifact=context_artifact(),
        rule_pack=rule_pack(),
        material_plan={},
        deterministic_report={"candidateReports": []},
        llm_validation_report={},
    )

    attempts = result.artifact_payload["candidateReports"][0]["attempts"]
    assert [attempt["label"] for attempt in attempts] == ["primary", "primary-repair"]
    assert attempts[0]["status"] == "error"
    assert attempts[0]["incident"]["incidentType"] == "schemaFailure"
    assert attempts[1]["status"] == "accepted"
    assert result.artifact_payload["candidateReports"][0]["operationEnvelope"]["status"] == "accepted"
    assert adapter.calls[0]["model"] == "critic-model"


def test_editorial_critique_provider_unconfigured_is_not_run(tmp_path) -> None:
    service = DraftEditorialCritiqueService(
        settings=BackendSettings(_env_file=None, OPENROUTER_API_KEY="", OPENROUTER_DEFAULT_MODEL=""),
        ai_run_service=ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=SequenceAdapter([]),
    )

    result = service.critique(
        draft_artifact=draft_artifact(),
        context_artifact={},
        rule_pack={},
        material_plan={},
        deterministic_report={},
        llm_validation_report={},
    )

    assert result.artifact_payload["status"] == "not-run"
    assert result.artifact_payload["metadata"]["reason"] == "provider-unconfigured"
    assert result.artifact_payload["metadata"]["operationEnvelope"]["status"] == "notRun"
    assert result.artifact_payload["metadata"]["operationEnvelope"]["incident"]["incidentType"] == "notConfigured"
    assert result.ai_run_ids == []


def service_with(tmp_path, adapter: SequenceAdapter, ai: AiRunService | None = None) -> DraftEditorialCritiqueService:
    return DraftEditorialCritiqueService(
        settings=BackendSettings(
            _env_file=None,
            OPENROUTER_API_KEY="sk-test-secret",
            OPENROUTER_DEFAULT_MODEL="primary-model",
            DRAFT_CRITIC_MODEL="critic-model",
        ),
        ai_run_service=ai or ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
    )


def ai_service(tmp_path) -> AiRunService:
    return AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))


def draft_artifact() -> dict[str, Any]:
    return {
        "candidates": [{"id": "candidate-1", "title": "Draft", "body": "Readable but generic body."}],
        "contextPacks": {"critic": {"role": "critic", "items": [{"cardId": "risk-1", "summary": "Generic prose risk"}]}},
    }


def context_artifact() -> dict[str, Any]:
    return {"postContract": {"thesis": "Approved thesis"}, "sourceLedger": {"claims": []}}


def rule_pack() -> dict[str, Any]:
    return {"ruleRegistrySnapshot": {"rules": []}, "evidenceInterpretation": {"tensions": []}}


def critique_payload(editorial_risk: str = "high") -> dict[str, Any]:
    return {
        "summary": "The draft is safe but generic.",
        "editorialRisk": editorial_risk,
        "overallJudgment": "It needs a sharper author stance.",
        "strongestMove": "Clear workflow framing.",
        "weakestMove": "Sounds like generic AI prose.",
        "recommendedEditorialMove": "Name the uncomfortable product trade-off earlier.",
        "findings": [
            {
                "criticId": "critic.genericAiProse",
                "severity": "warning",
                "editorialDimension": "genericAiProse",
                "message": "The draft can be swapped with many generic AI posts.",
                "evidenceExcerpt": "Readable but generic body.",
                "repairGuidance": "Add a concrete author claim that creates tension.",
            }
        ],
        "observations": [
            {
                "criticId": "critic.tension",
                "editorialDimension": "tension",
                "message": "There is a usable workflow tension.",
                "evidenceExcerpt": "workflow",
            }
        ],
    }
