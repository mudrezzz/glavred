from typing import Any

from fastapi.testclient import TestClient

from backend.app.application.public_evidence_ports import PublicUrlReadResult
from backend.app.infrastructure.openrouter_web_search_adapter import OpenRouterWebSearchCitation, OpenRouterWebSearchResult
from backend.app.main import create_app
from backend.app.settings import BackendSettings


class ApiFakeWebSearchAdapter:
    def search(self, **kwargs: Any) -> OpenRouterWebSearchResult:
        return OpenRouterWebSearchResult(
            content="Search content",
            citations=[OpenRouterWebSearchCitation(title="Case", url="https://example.com/case", snippet="implementation case metrics")],
            raw_response={"id": "search-1"},
        )


class ApiFakeUrlReader:
    def read(self, url: str) -> PublicUrlReadResult:
        return PublicUrlReadResult(url=url, final_url=url, title="Read case", text="Read body with implementation details.")


def test_external_radar_run_api_returns_trace_contract() -> None:
    app = create_app(settings=BackendSettings(_env_file=None, OPENROUTER_API_KEY="test-token", OPENROUTER_DEFAULT_MODEL="test-model", OPENROUTER_WEB_TOOLS_ENABLED=True))
    app.state.openrouter_web_search_adapter = ApiFakeWebSearchAdapter()
    app.state.public_url_reader = ApiFakeUrlReader()
    client = TestClient(app)

    response = client.post("/api/radar-runs/external", json={"radarId": "radar-1", "workspace": workspace()})

    assert response.status_code == 200
    payload = response.json()
    assert payload["run"]["searchPlan"]["queries"]
    assert payload["run"]["searchPlan"]["intents"]
    assert payload["run"]["searchPlan"]["trace"]["plannerVersion"] == "deterministic-search-campaign-v2"
    assert payload["run"]["selectedForRead"]
    assert payload["foundMaterials"][0]["title"] == "Read case"


def workspace() -> dict[str, Any]:
    return {
        "projectProfile": {"language": "en"},
        "sourceRegistry": {
            "handles": [{
                "id": "source-open-web",
                "type": "openWebQuery",
                "title": "Industrial AI web",
                "locator": "industrial AI maintenance",
                "status": "active",
                "capabilities": {"canSearch": True, "canReadUrl": False},
            }]
        },
        "radars": [{
            "id": "radar-1",
            "title": "Industrial AI radar",
            "scope": "Find industrial AI implementation patterns",
            "sourceHandleIds": ["source-open-web"],
            "rules": [{"statement": "Predictive maintenance with operational proof"}],
        }],
        "radarRuns": [],
    }
