from dataclasses import dataclass
from typing import Any

from fastapi.testclient import TestClient

from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft
from backend.app.infrastructure.openrouter_draft_adapter import OpenRouterDraftResult
from backend.app.main import create_app
from backend.app.settings import BackendSettings


def make_payload() -> dict[str, Any]:
    return {
        "brief": {
            "id": "brief-demo",
            "title": "Почему AI-B2B demo еще не продукт",
            "rubric": "AI product discovery",
            "audience": "AI PM и founders",
            "thesis": "Demo magic не равно adoption.",
            "conflict": "Команды празднуют demo, но теряют rollout.",
            "authorPosition": "Сначала workflow improvement, потом модель.",
            "evidence": ["usage после пилота не растет"],
            "examples": ["нет evals", "непонятны rollback boundaries"],
            "structure": ["конфликт", "позиция", "проверки"],
            "cta": "Проверить продуктовую петлю до rollout.",
            "risks": ["не звучать против быстрых прототипов"],
            "sources": ["author note"],
        },
        "editorialModel": {
            "audience": "AI Product Manager",
            "styleRules": ["исследовательский тон"],
            "forbiddenTopics": ["generic AI hype"],
            "goals": ["объяснить adoption gap"],
        },
    }


def make_client(tmp_path, *, configured: bool, adapter: object | None = None) -> TestClient:
    return TestClient(
        create_app(
            settings=BackendSettings(
                _env_file=None,
                OPENROUTER_API_KEY="secret-token" if configured else "",
                OPENROUTER_DEFAULT_MODEL="openrouter/test-model" if configured else "",
                AI_RUN_AUDIT_DB_PATH=str(tmp_path / "audit.sqlite3"),
            ),
            openrouter_draft_adapter=adapter,
        )
    )


@dataclass
class SuccessfulDraftAdapter:
    def generate(self, settings: BackendSettings, request: DraftGenerationRequest) -> OpenRouterDraftResult:
        return OpenRouterDraftResult(
            draft=GeneratedDraft(
                id=f"draft-{request.brief.id}",
                brief_id=request.brief.id,
                title="OpenRouter draft title",
                body="OpenRouter draft body",
                version=1,
                status="draft",
                updated_at="2026-06-18T00:00:00+00:00",
            ),
            raw_response={"id": "run-provider-id", "model": settings.openrouter_default_model},
        )


@dataclass
class FailingDraftAdapter:
    message: str

    def generate(self, settings: BackendSettings, request: DraftGenerationRequest) -> OpenRouterDraftResult:
        raise ValueError(self.message)


def test_generate_draft_uses_openrouter_when_configured(tmp_path) -> None:
    client = make_client(tmp_path, configured=True, adapter=SuccessfulDraftAdapter())

    response = client.post("/api/drafts/generate", json=make_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["draft"] == {
        "id": "draft-brief-demo",
        "briefId": "brief-demo",
        "title": "OpenRouter draft title",
        "body": "OpenRouter draft body",
        "version": 1,
        "status": "draft",
        "updatedAt": "2026-06-18T00:00:00+00:00",
    }
    assert payload["aiRun"]["status"] == "succeeded"
    assert payload["aiRun"]["provider"] == "openrouter"
    assert payload["aiRun"]["fallbackUsed"] is False
    assert "secret-token" not in response.text


def test_generate_draft_falls_back_when_openrouter_is_missing(tmp_path) -> None:
    client = make_client(tmp_path, configured=False)

    response = client.post("/api/drafts/generate", json=make_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["draft"]["briefId"] == "brief-demo"
    assert payload["draft"]["body"]
    assert payload["aiRun"]["provider"] == "deterministic"
    assert payload["aiRun"]["fallbackUsed"] is True
    assert payload["aiRun"]["error"] == "OpenRouter is not configured"


def test_generate_draft_falls_back_on_provider_error_without_exposing_secret(tmp_path) -> None:
    client = make_client(tmp_path, configured=True, adapter=FailingDraftAdapter("secret-token provider failed"))

    response = client.post("/api/drafts/generate", json=make_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["aiRun"]["provider"] == "openrouter"
    assert payload["aiRun"]["fallbackUsed"] is True
    assert "secret-token" not in response.text
    assert payload["draft"]["body"]


def test_generate_draft_records_run_visible_in_ai_run_list(tmp_path) -> None:
    client = make_client(tmp_path, configured=True, adapter=SuccessfulDraftAdapter())
    created = client.post("/api/drafts/generate", json=make_payload()).json()

    listed = client.get("/api/ai-runs?capability=draftGeneration").json()
    loaded = client.get(f"/api/ai-runs/{created['aiRun']['id']}").json()

    assert listed[0]["id"] == created["aiRun"]["id"]
    assert loaded["resultPayload"]["draftId"] == created["draft"]["id"]
