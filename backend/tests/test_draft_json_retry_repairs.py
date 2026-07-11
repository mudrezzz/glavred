from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.generation.deterministic_draft_candidate_service import DeterministicDraftCandidateService
from backend.app.drafting.application.generation.draft_alternative_angle_candidate_service import DraftAlternativeAngleCandidateService
from backend.app.drafting.application.generation.draft_candidate_direction_service import DraftCandidateDirectionService
from backend.app.drafting.application.generation.draft_candidate_generation_service import DraftCandidateGenerationService
from backend.app.drafting.application.generation.draft_candidate_selection_service import DraftCandidateSelectionService
from backend.app.domain.draft_alternative_angle import AlternativeAngleRoute
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings
from backend.tests.test_draft_planning_services import context_and_rule_pack
from backend.tests.test_draft_run_pipeline import make_request
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


@dataclass
class FakeOpenRouterResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class SequentialAdapter:
    def __init__(self, outcomes: list[Any]) -> None:
        self.outcomes = outcomes
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return FakeOpenRouterResult(outcome, {"id": f"or-{len(self.calls)}", "model": kwargs.get("model")})


class JsonFailure(ValueError):
    raw_response_excerpt = "```json not-json ```"


def test_writer_candidate_retries_primary_repair_and_backup_before_success(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    adapter = SequentialAdapter([JsonFailure("bad json"), ValueError("still bad"), candidate_payload()])
    service = _candidate_service(tmp_path, adapter)

    result = service.create(
        request=make_request(),
        context_summary=context_summary,
        rule_pack=rule_pack,
        material_plan={"availableEvidence": ["evidence"]},
        draft_strategy={"thesisAngle": "workflow before model"},
        rhetorical_plans={"plans": [{"id": "plan-1", "title": "Research plan"}]},
        provider_dossier_factory=ProviderDossierTestFixture.writer_factory(),
    )

    assert [call["model"] for call in adapter.calls] == ["writer-model", "writer-model", "backup-model"]
    assert [call["temperature"] for call in adapter.calls] == [0.65, 0.15, 0.15]
    assert [call.get("top_p") for call in adapter.calls] == [0.9, None, None]
    assert len(result.ai_run_ids) == 3
    assert result.artifact_payload["source"] == "openrouter"
    first_run = _ai_service(tmp_path).get_run(result.ai_run_ids[0])
    assert first_run is not None
    assert first_run.result_payload["rawResponseExcerpt"] == "```json not-json ```"
    backup_run = _ai_service(tmp_path).get_run(result.ai_run_ids[-1])
    assert backup_run is not None
    assert backup_run.request_payload["attempt"]["label"] == "backup"
    assert backup_run.request_payload["attempt"]["backup"] is True
    assert backup_run.request_payload["generationParams"]["generationParamProfile"] == "jsonRepair"
    assert backup_run.request_payload["generationParams"]["temperature"] == 0.15
    for run_id in result.ai_run_ids:
        attempt_run = _ai_service(tmp_path).get_run(run_id)
        assert attempt_run is not None
        assert attempt_run.request_payload["payloadBudget"]["promptCharEstimate"] > 0
        assert attempt_run.request_payload["providerDossier"]["runtimeMigrated"] is True


def test_alternative_angle_candidate_retries_before_returning_challenger(tmp_path) -> None:
    context_summary, _ = context_and_rule_pack()
    adapter = SequentialAdapter([RuntimeError("malformed"), candidate_payload()])
    service = DraftAlternativeAngleCandidateService(
        settings=_settings(),
        ai_run_service=_ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
    )

    candidate, ai_run_ids, error, attempts = service.create(
        request=make_request(),
        route=AlternativeAngleRoute(
            id="challenger",
            title="Challenge",
            angle="Use a different author stance.",
            opening_move="Open from dissent.",
            why_different="It avoids the generic source recap.",
        ),
        context_summary=context_summary,
        provider_dossier=ProviderDossierTestFixture.writer_factory().build(
            plan_id=None,
            operation_id="alternativeAngleCandidate",
        ),
    )

    assert error == ""
    assert candidate is not None
    assert [call["model"] for call in adapter.calls] == ["writer-model", "writer-model"]
    assert [call["temperature"] for call in adapter.calls] == [0.65, 0.15]
    assert [attempt["label"] for attempt in attempts] == ["primary", "primary-repair"]
    assert len(ai_run_ids) == 2
    assert all(_ai_service(tmp_path).get_run(run_id).request_payload["payloadBudget"] for run_id in ai_run_ids)


def test_public_prose_guard_is_present_in_writer_prompt(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    adapter = SequentialAdapter([candidate_payload()])
    service = _candidate_service(tmp_path, adapter)

    service.create(
        request=make_request(),
        context_summary=context_summary,
        rule_pack=rule_pack,
        material_plan={"availableEvidence": ["evidence"]},
        draft_strategy={"thesisAngle": "workflow before model"},
        rhetorical_plans={"plans": [{"id": "plan-1", "title": "Research plan"}]},
        provider_dossier_factory=ProviderDossierTestFixture.writer_factory(),
    )

    system_message = adapter.calls[0]["messages"][0]["content"]
    assert "SourceLedger" in system_message
    assert "publicEvidence" in system_message
    assert "dev-jargon" in system_message


def _candidate_service(tmp_path, adapter: SequentialAdapter) -> DraftCandidateGenerationService:
    return DraftCandidateGenerationService(
        settings=_settings(),
        ai_run_service=_ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
        direction_service=DraftCandidateDirectionService(),
        deterministic_candidate_service=DeterministicDraftCandidateService(),
        selection_service=DraftCandidateSelectionService(),
    )


def _settings() -> BackendSettings:
    return BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="sk-test-secret",
        OPENROUTER_DEFAULT_MODEL="default-model",
        OPENROUTER_BACKUP_MODEL="backup-model",
        DRAFT_WRITER_MODEL="writer-model",
    )


def _ai_service(tmp_path) -> AiRunService:
    return AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))


def candidate_payload() -> dict[str, Any]:
    return {
        "title": "Provider candidate",
        "body": "Provider body with evidence and author stance.",
        "rationale": "Uses the selected route.",
        "usedEvidence": ["evidence"],
        "ruleCoverage": ["rule"],
        "risks": [],
        "weaknesses": [],
    }
