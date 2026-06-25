from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.draft_llm_validation_service import DraftLlmValidationService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings


class FakeOpenRouterResult:
    def __init__(self, payload: dict[str, Any], model: str = "test-model") -> None:
        self.payload = payload
        self.raw_response = {"id": "or-validation", "model": model}


class SequentialValidationAdapter:
    def __init__(self, outcomes: list[Any]) -> None:
        self.outcomes = outcomes
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return FakeOpenRouterResult(outcome, str(kwargs.get("model") or "test-model"))


def test_llm_validation_success_reports_all_candidates(tmp_path) -> None:
    adapter = SequentialValidationAdapter([valid_payload("source"), valid_payload("voice")])
    result = service(tmp_path, adapter, configured=True, review_model="review-model").validate(
        draft_artifact={"candidates": [{"id": "candidate-1"}, {"id": "candidate-2"}]},
        context_artifact={},
        rule_pack={},
        material_plan={},
        deterministic_report={"candidateReports": [{"candidateId": "candidate-1"}, {"candidateId": "candidate-2"}]},
    )

    assert result.artifact_payload["summary"]["candidateCount"] == 2
    assert result.artifact_payload["candidateReports"][0]["findings"][0]["validatorId"] == "llm.source"
    assert len(result.ai_run_ids or []) == 2
    assert adapter.calls[0]["model"] == "review-model"
    assert result.artifact_payload["candidateReports"][0]["attempts"][0]["modelRole"] == "review"
    assert result.artifact_payload["candidateReports"][0]["attempts"][0]["modelSelectionSource"] == "role"


def test_llm_validation_unconfigured_is_not_run_without_fake_findings(tmp_path) -> None:
    result = service(tmp_path, SequentialValidationAdapter([]), configured=False).validate(
        draft_artifact={"candidates": [{"id": "candidate-1"}]},
        context_artifact={},
        rule_pack={},
        material_plan={},
        deterministic_report={},
    )

    assert result.artifact_payload["status"] == "not-run"
    assert result.artifact_payload["metadata"]["reason"] == "provider-unconfigured"
    assert result.artifact_payload["candidateReports"] == []
    assert result.ai_run_ids == []


def test_llm_validation_retries_and_uses_backup_model(tmp_path) -> None:
    adapter = SequentialValidationAdapter([ValueError("bad json sk-test-secret"), ValueError("bad repair"), valid_payload("coherence")])
    result = service(tmp_path, adapter, configured=True, backup_model="backup-model").validate(
        draft_artifact={"candidates": [{"id": "candidate-1"}]},
        context_artifact={},
        rule_pack={},
        material_plan={},
        deterministic_report={},
    )

    attempts = result.artifact_payload["candidateReports"][0]["attempts"]
    assert [attempt["label"] for attempt in attempts] == ["primary", "primary-repair", "backup"]
    assert attempts[2]["backup"] is True
    assert adapter.calls[2]["model"] == "backup-model"
    assert "sk-test-secret" not in attempts[0]["validation"]


def service(tmp_path, adapter: object, *, configured: bool, backup_model: str = "", review_model: str = "") -> DraftLlmValidationService:
    return DraftLlmValidationService(
        settings=BackendSettings(
            _env_file=None,
            OPENROUTER_API_KEY="sk-test-secret" if configured else "",
            OPENROUTER_DEFAULT_MODEL="test-model" if configured else "",
            OPENROUTER_BACKUP_MODEL=backup_model,
            DRAFT_REVIEW_MODEL=review_model,
        ),
        ai_run_service=AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3")),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
    )


def valid_payload(kind: str) -> dict[str, Any]:
    return {
        "summary": f"{kind} finding",
        "findings": [
            {
                "validatorId": f"llm.{kind}",
                "severity": "warning",
                "message": "LLM issue",
                "evidenceExcerpt": "excerpt",
                "repairGuidance": "repair",
            }
        ],
    }
