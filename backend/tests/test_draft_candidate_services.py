from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_draft_candidate_service import DeterministicDraftCandidateService
from backend.app.application.draft_candidate_direction_service import DraftCandidateDirectionService
from backend.app.application.draft_candidate_generation_service import DraftCandidateGenerationService
from backend.app.application.draft_candidate_selection_service import DraftCandidateSelectionService
from backend.app.domain.ai_run import AiRunProvider
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings
from backend.tests.test_draft_planning_services import context_and_rule_pack
from backend.tests.test_draft_run_pipeline import make_request


@dataclass
class FakeOpenRouterResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class SuccessfulCandidateAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        self.calls.append(kwargs)
        return FakeOpenRouterResult(
            {
                "title": "Provider draft candidate",
                "body": "Provider body with topic, conflict and practical value.",
                "rationale": "Uses the selected direction and rule pack.",
                "usedEvidence": ["pilot usage data"],
                "ruleCoverage": ["hard rule", "topic fit", "fabula fit"],
                "risks": ["claim risk"],
                "weaknesses": [],
            },
            {"id": "or-candidate", "model": "test"},
        )


class FailingCandidateAdapter:
    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        raise RuntimeError("provider failed sk-test-secret")


def test_direction_builder_returns_three_stable_directions() -> None:
    context_summary, rule_pack = context_and_rule_pack()

    directions = DraftCandidateDirectionService().create_directions(
        context_summary=context_summary,
        rule_pack=rule_pack,
        draft_strategy={"thesisAngle": "workflow before model", "fabulaUsage": "research note"},
    )

    assert [direction.id for direction in directions] == ["research", "polemic", "checklist"]


def test_direction_builder_uses_rhetorical_plans_when_available() -> None:
    context_summary, rule_pack = context_and_rule_pack()

    directions = DraftCandidateDirectionService().create_directions(
        context_summary=context_summary,
        rule_pack=rule_pack,
        draft_strategy={"thesisAngle": "workflow before model"},
        rhetorical_plans={"plans": [{"id": "contrast", "title": "Contrast plan", "angle": "Show the false belief"}]},
    )

    assert [direction.id for direction in directions] == ["contrast"]
    assert directions[0].rhetorical_plan_id == "contrast"


def test_candidate_generation_uses_openrouter_and_child_ai_runs(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    adapter = SuccessfulCandidateAdapter()
    service = candidate_service(tmp_path, adapter, configured=True, writer_model="writer-model")

    result = service.create(
        request=make_request(),
        context_summary=context_summary,
        rule_pack=rule_pack,
        material_plan={"availableEvidence": ["pilot usage data"]},
        draft_strategy={"thesisAngle": "workflow before model"},
        rhetorical_plans={"plans": [{"id": "research", "title": "Research plan"}]},
    )

    assert result.artifact_payload["source"] == "openrouter"
    assert len(result.artifact_payload["candidates"]) == 1
    assert result.artifact_payload["candidates"][0]["rhetoricalPlanId"] == "research"
    assert result.artifact_payload["selection"]["selectedCandidateId"]
    assert len(result.ai_run_ids) == 1
    run = ai_service(tmp_path).get_run(result.ai_run_ids[0])
    assert run is not None
    assert run.provider == AiRunProvider.OPENROUTER
    assert run.request_payload["draftRunStep"] == "draftCandidate"
    assert run.request_payload["modelRole"] == "writer"
    assert run.request_payload["selectedModel"] == "writer-model"
    assert run.request_payload["modelSelectionSource"] == "role"
    assert adapter.calls[0]["model"] == "writer-model"
    assert result.artifact_payload["candidates"][0]["modelRole"] == "writer"
    assert result.final_draft.body.startswith("Provider body")


def test_candidate_generation_falls_back_without_openrouter(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = candidate_service(tmp_path, SuccessfulCandidateAdapter(), configured=False)

    result = service.create(
        request=make_request(),
        context_summary=context_summary,
        rule_pack=rule_pack,
        material_plan={"availableEvidence": ["pilot usage data"]},
        draft_strategy={"thesisAngle": "workflow before model"},
    )

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert result.artifact_payload["fallbackUsed"] is True
    assert all(candidate["fallbackUsed"] for candidate in result.artifact_payload["candidates"])
    assert result.final_draft is None
    assert result.artifact_payload["selection"]["selectedCandidateId"] is None
    assert all(score["selectionStatus"] == "excluded" for score in result.artifact_payload["selection"]["scorecard"])


def test_candidate_provider_error_falls_back_without_secret(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = candidate_service(tmp_path, FailingCandidateAdapter(), configured=True)

    result = service.create(
        request=make_request(),
        context_summary=context_summary,
        rule_pack=rule_pack,
        material_plan={"availableEvidence": ["pilot usage data"]},
        draft_strategy={"thesisAngle": "workflow before model"},
    )

    run = ai_service(tmp_path).get_run(result.ai_run_ids[0])
    assert run is not None
    assert run.fallback_used is True
    assert "sk-test-secret" not in (run.error or "")
    assert result.artifact_payload["source"] == "deterministicFallback"
    assert result.final_draft is None


def candidate_service(tmp_path, adapter: object, *, configured: bool, writer_model: str = "") -> DraftCandidateGenerationService:
    return DraftCandidateGenerationService(
        settings=BackendSettings(
            _env_file=None,
            OPENROUTER_API_KEY="sk-test-secret" if configured else "",
            OPENROUTER_DEFAULT_MODEL="test-model" if configured else "",
            DRAFT_WRITER_MODEL=writer_model,
        ),
        ai_run_service=ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
        direction_service=DraftCandidateDirectionService(),
        deterministic_candidate_service=DeterministicDraftCandidateService(),
        selection_service=DraftCandidateSelectionService(),
    )


def ai_service(tmp_path) -> AiRunService:
    return AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))
