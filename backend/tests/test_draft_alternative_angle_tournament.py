from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.generation.draft_alternative_angle_candidate_service import DraftAlternativeAngleCandidateService
from backend.app.drafting.application.validation.draft_alternative_angle_route_service import DraftAlternativeAngleRouteService
from backend.app.drafting.application.validation.draft_alternative_angle_tournament_service import DraftAlternativeAngleTournamentService
from backend.app.drafting.application.revision.draft_ranking_revision_result import DraftRankingRevisionResult
from backend.app.drafting.application.validation.draft_validation_step_service import DraftValidationStepService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings
from backend.tests.test_draft_planning_services import context_and_rule_pack
from backend.tests.test_draft_run_pipeline import make_request


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


def test_alternative_angle_tournament_adds_challenger_candidate(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    adapter = SequentialAdapter([route_payload(), candidate_payload()])
    service = tournament_service(tmp_path, adapter, configured=True)

    merged, tournament, ai_run_ids = service.run(
        request=make_request(),
        draft_artifact=draft_artifact(),
        validation_report=initial_validation(),
        context_summary=context_summary,
        context_artifact={"contextPacks": {"anotherAngle": {"items": [{"cardId": "risk-1"}]}, "writer": {"items": [{"cardId": "claim-1"}]}}},
        rule_pack=rule_pack,
        material_plan={"availableEvidence": ["evidence"]},
        draft_strategy={"thesisAngle": "workflow before model"},
    )

    assert tournament["status"] == "succeeded"
    assert tournament["route"]["whyDifferent"] == "It attacks the weakest move instead of polishing the same opening."
    assert merged["alternativeAngleCandidateId"] == "alternative-angle-1-brief-demo"
    assert [candidate["id"] for candidate in merged["candidates"]] == ["candidate-1", "alternative-angle-1-brief-demo"]
    assert merged["candidates"][1]["routeType"] == "alternativeAngle"
    assert len(ai_run_ids) == 2
    assert adapter.calls[0]["model"] == "another-angle-model"
    assert adapter.calls[1]["model"] == "writer-model"
    assert adapter.calls[0]["temperature"] == 0.8
    assert adapter.calls[0].get("top_p") is None
    assert adapter.calls[1]["temperature"] == 0.65
    assert adapter.calls[1]["top_p"] == 0.9
    route_run = ai_service(tmp_path).get_run(ai_run_ids[0])
    assert route_run is not None
    assert route_run.request_payload["draftRunStep"] == "alternativeAngleRoute"
    assert route_run.request_payload["modelRole"] == "anotherAngle"
    assert route_run.request_payload["generationParams"]["generationParamProfile"] == "anotherAngle"


def test_alternative_angle_tournament_is_not_run_without_provider(tmp_path) -> None:
    context_summary, rule_pack = context_and_rule_pack()
    service = tournament_service(tmp_path, SequentialAdapter([]), configured=False)

    merged, tournament, ai_run_ids = service.run(
        request=make_request(),
        draft_artifact=draft_artifact(),
        validation_report=initial_validation(),
        context_summary=context_summary,
        context_artifact={},
        rule_pack=rule_pack,
        material_plan={},
        draft_strategy={},
    )

    assert merged == draft_artifact()
    assert tournament["status"] == "not-run"
    assert tournament["reason"] == "provider-unconfigured"
    assert ai_run_ids == []


def test_validation_step_reruns_final_report_for_alternative_candidate() -> None:
    service = DraftValidationStepService(alternative_tournament=FakeAlternativeTournament())

    result = service.validate(
        request=make_request(),
        context_summary={},
        draft_artifact=draft_artifact(),
        context_artifact={},
        rule_pack={},
        material_plan={},
        draft_strategy={},
    )

    candidate_ids = [report["candidateId"] for report in result.artifact_payload["candidateReports"]]
    assert candidate_ids == ["candidate-1", "alternative-angle-1-brief-demo"]
    assert result.artifact_payload["initialValidation"]["summary"]["candidateCount"] == 1
    assert result.artifact_payload["alternativeAngleTournament"]["status"] == "succeeded"
    assert result.ai_run_ids == ["ai-alt"]


def test_validation_step_ranks_merged_candidate_pool() -> None:
    ranking = FakeRankingRevision()
    service = DraftValidationStepService(alternative_tournament=FakeAlternativeTournament(), ranking_revision_service=ranking)

    service.validate(
        request=make_request(),
        context_summary={},
        draft_artifact=draft_artifact(),
        context_artifact={},
        rule_pack={},
        material_plan={},
        draft_strategy={},
    )

    assert ranking.candidate_ids == ["candidate-1", "alternative-angle-1-brief-demo"]


class FakeAlternativeTournament:
    def run(self, **kwargs: Any) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
        merged = {**kwargs["draft_artifact"], "alternativeAngleCandidateId": "alternative-angle-1-brief-demo"}
        merged["candidates"] = [
            *kwargs["draft_artifact"]["candidates"],
            {"id": "alternative-angle-1-brief-demo", "title": "Alternative", "body": "Alternative body", "routeType": "alternativeAngle"},
        ]
        return merged, {"status": "succeeded", "candidate": merged["candidates"][1]}, ["ai-alt"]


class FakeRankingRevision:
    def __init__(self) -> None:
        self.candidate_ids: list[str] = []

    def run(self, **kwargs: Any) -> DraftRankingRevisionResult:
        self.candidate_ids = [candidate["id"] for candidate in kwargs["draft_artifact"]["candidates"]]
        return DraftRankingRevisionResult(artifact_payload={"status": "succeeded"}, final_draft=None, ai_run_ids=[])


def tournament_service(tmp_path, adapter: SequentialAdapter, *, configured: bool) -> DraftAlternativeAngleTournamentService:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="sk-test-secret" if configured else "",
        OPENROUTER_DEFAULT_MODEL="default-model" if configured else "",
        DRAFT_ANOTHER_ANGLE_MODEL="another-angle-model",
        DRAFT_WRITER_MODEL="writer-model",
    )
    provider_kwargs = {
        "settings": settings,
        "ai_run_service": ai_service(tmp_path),
        "openrouter_validator": OpenRouterConfigValidator(),
        "openrouter_adapter": adapter,
    }
    return DraftAlternativeAngleTournamentService(
        route_service=DraftAlternativeAngleRouteService(**provider_kwargs),
        candidate_service=DraftAlternativeAngleCandidateService(**provider_kwargs),
    )


def ai_service(tmp_path) -> AiRunService:
    return AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))


def draft_artifact() -> dict[str, Any]:
    return {
        "candidates": [{"id": "candidate-1", "title": "Original", "body": "Original body"}],
        "selection": {"selectedCandidateId": "candidate-1", "scorecard": [{"candidateId": "candidate-1", "total": 70}]},
    }


def initial_validation() -> dict[str, Any]:
    return {
        "status": "warning",
        "candidateReports": [{"candidateId": "candidate-1", "findings": [{"validatorId": "critic.genericAiProse", "message": "Too generic"}]}],
        "editorialCritiqueReport": {
            "status": "warning",
            "candidateReports": [{"candidateId": "candidate-1", "editorialRisk": "high", "weakestMove": "Generic opening"}],
        },
    }


def route_payload() -> dict[str, Any]:
    return {
        "id": "challenger",
        "title": "Author stance challenger",
        "angle": "Start from the author's dissent instead of the source recap.",
        "openingMove": "Open with a sharper author claim.",
        "whyDifferent": "It attacks the weakest move instead of polishing the same opening.",
        "critiqueInputs": ["critic.genericAiProse"],
        "claimsToUse": ["claim-1"],
        "claimsToAvoid": [],
        "rulesToStress": ["rule-1"],
        "risks": ["May overcorrect tone"],
    }


def candidate_payload() -> dict[str, Any]:
    return {
        "title": "Alternative challenger",
        "body": "A different body with author stance and evidence.",
        "rationale": "Uses the challenger route.",
        "usedEvidence": ["claim-1"],
        "ruleCoverage": ["rule-1"],
        "risks": [],
        "weaknesses": [],
    }
