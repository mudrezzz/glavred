from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.source_intent_normalizer import SourceIntentNormalizer
from backend.app.application.source_research_plan_service import SourceResearchPlanService
from backend.app.domain.draft_generation import DraftBriefContext, DraftEditorialModelContext, DraftGenerationRequest
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings


@dataclass
class FakeOpenRouterResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class SuccessfulAdapter:
    def complete_json(self, **kwargs: Any) -> FakeOpenRouterResult:
        return FakeOpenRouterResult(
            {
                "researchQuestions": ["What do opinion leaders say about adoption?"],
                "sourceTargets": ["independent analysts", "operator essays"],
                "verificationTasks": [
                    {
                        "id": "task-1",
                        "kind": "findPublicSources",
                        "instruction": "Find opinion leader commentary.",
                        "sourceIntentItemIds": ["source-intent-1"],
                        "expectedOutput": "short source-backed summary",
                    }
                ],
                "queryCandidates": ["AI adoption opinion leaders"],
                "exclusions": ["vendor blogs"],
            },
            {"id": "or-research", "model": "test-model"},
        )


def test_source_intent_normalizer_classifies_urls_prefixes_and_plain_requests() -> None:
    intent = SourceIntentNormalizer().normalize(
        make_request([
            "url: https://example.com/report",
            "найти: мнение лидеров мнений по этой теме",
            "проверить: свежую статистику adoption",
            "не использовать: vendor blogs",
            "Ben Thompson Stratechery",
        ])
    )

    kinds = [item.kind.value for item in intent.items]

    assert kinds == ["url", "researchRequest", "proofNeed", "exclusion", "namedSource"]
    assert intent.items[1].instruction == "мнение лидеров мнений по этой теме"


def test_plain_human_request_is_research_request_not_keyword() -> None:
    intent = SourceIntentNormalizer().normalize(make_request(["нужно мнение лидеров мнений по этой теме"]))

    assert intent.items[0].kind.value == "researchRequest"
    assert "keyword" not in intent.items[0].to_payload()


def test_source_research_plan_service_creates_openrouter_ai_run(tmp_path) -> None:
    service = SourceResearchPlanService(
        settings=settings(configured=True),
        ai_run_service=ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=SuccessfulAdapter(),
    )

    result = service.create(
        request=make_request(["найти: мнение лидеров мнений по этой теме"]),
        context_artifact={"brief": {"title": "Post"}, "sourceIntentDefaults": {"sourcesOrigin": "fabulaManual"}},
    )

    assert result.artifact_payload["source"] == "openrouter"
    assert result.artifact_payload["sourcesOrigin"] == "fabulaManual"
    assert result.artifact_payload["fallbackUsed"] is False
    assert result.artifact_payload["researchPlan"]["researchQuestions"]
    run = ai_service(tmp_path).get_run(result.ai_run_id or "")
    assert run is not None
    assert run.request_payload["draftRunStep"] == "sourceIntentResearchPlan"


def test_source_research_plan_service_falls_back_when_provider_missing(tmp_path) -> None:
    service = SourceResearchPlanService(
        settings=settings(configured=False),
        ai_run_service=ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=SuccessfulAdapter(),
    )

    result = service.create(request=make_request(["не использовать: vendor blogs"]), context_artifact={})

    assert result.artifact_payload["source"] == "deterministicFallback"
    assert result.artifact_payload["fallbackUsed"] is True
    assert result.artifact_payload["researchPlan"]["exclusions"] == ["vendor blogs"]


def make_request(sources: list[str]) -> DraftGenerationRequest:
    return DraftGenerationRequest(
        brief=DraftBriefContext(
            id="brief-source",
            title="Post",
            rubric="AI",
            audience="AI PM",
            thesis="Thesis",
            conflict="Conflict",
            author_position="Position",
            evidence=["Signal evidence"],
            examples=[],
            structure=[],
            cta="CTA",
            risks=[],
            sources=sources,
        ),
        editorial_model=DraftEditorialModelContext(audience="AI PM", style_rules=[], forbidden_topics=[], goals=[]),
    )


def ai_service(tmp_path) -> AiRunService:
    return AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))


def settings(configured: bool) -> BackendSettings:
    return BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="sk-test-secret" if configured else "",
        OPENROUTER_DEFAULT_MODEL="test-model" if configured else "",
    )
