from typing import Any

from fastapi.testclient import TestClient

from backend.app.application.public_evidence_ports import PublicUrlReadResult
from backend.app.infrastructure.openrouter_web_search_adapter import OpenRouterWebSearchCitation, OpenRouterWebSearchResult
from backend.app.main import create_app
from backend.app.settings import BackendSettings
from backend.app.upstream.application.signal_extraction_provider import SignalExtractionProviderResult
import json


class ApiFakeWebSearchAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def search(self, **kwargs: Any) -> OpenRouterWebSearchResult:
        self.calls += 1
        return OpenRouterWebSearchResult(
            content="Search content",
            citations=[OpenRouterWebSearchCitation(title="Case", url="https://example.com/case", snippet="implementation case metrics")],
            raw_response={"id": "search-1"},
        )


class ApiFakeUrlReader:
    def __init__(self) -> None:
        self.calls = 0

    def read(self, url: str) -> PublicUrlReadResult:
        self.calls += 1
        return PublicUrlReadResult(url=url, final_url=url, title="Read case", text="Read body with implementation details.")


class ApiFakeSignalExtractionProvider:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, **kwargs: Any) -> SignalExtractionProviderResult:
        self.calls += 1
        provider_input = json.loads(kwargs["messages"][1]["content"])
        material = provider_input["materials"][0]
        fragment = material["fragments"][0]
        return SignalExtractionProviderResult(
            payload={
                "signals": [{
                    "type": "case",
                    "title": "Прочитанный промышленный кейс",
                    "summary": "Материал содержит детали внедрения.",
                    "confidence": "medium",
                    "uncertainty": "Доступен только один материал.",
                    "mechanism": "Чтение описания внедрения.",
                    "actors": [],
                    "outcome": "Детали извлечены.",
                    "limitations": ["Доступен только один материал."],
                    "reasonCodes": ["readable-case"],
                    "evidenceRefs": [{"materialId": material["id"], "fragmentId": fragment["id"], "quote": fragment["text"]}],
                }],
                "materialDecisions": [{"materialId": material["id"], "decision": "signalProducing", "reasonCodes": ["grounded"]}],
            },
            usage={"prompt_tokens": 300, "completion_tokens": 120, "total_tokens": 420},
            request_id="signal-api-1",
            model=kwargs["model"],
        )


def test_external_radar_run_api_returns_trace_contract_and_retries_without_retrieval(tmp_path) -> None:
    app = create_app(settings=BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="test-token",
        OPENROUTER_DEFAULT_MODEL="test-model",
        OPENROUTER_WEB_TOOLS_ENABLED=True,
        AI_RUN_AUDIT_DB_PATH=tmp_path / "ai-runs.sqlite3",
    ))
    search = ApiFakeWebSearchAdapter()
    reader = ApiFakeUrlReader()
    extraction = ApiFakeSignalExtractionProvider()
    app.state.openrouter_web_search_adapter = search
    app.state.public_url_reader = reader
    app.state.signal_extraction_provider = extraction
    client = TestClient(app)

    response = client.post("/api/radar-runs/external", json={"radarId": "radar-1", "workspace": workspace()})

    assert response.status_code == 200
    payload = response.json()
    assert payload["run"]["searchPlan"]["queries"]
    assert payload["run"]["searchPlan"]["intents"]
    assert payload["run"]["searchPlan"]["trace"]["plannerVersion"] == "deterministic-search-campaign-v2"
    assert payload["run"]["selectedForRead"]
    assert payload["foundMaterials"][0]["title"] == "Read case"
    assert payload["foundMaterials"][0]["contentFragments"]
    assert payload["sourceSignals"][0]["reviewStatus"] == "candidate"
    assert payload["signalExtractionReport"]["status"] == "succeeded"
    assert payload["run"]["signalExtraction"]["decisionCoverageComplete"] is True

    retry_workspace = {
        **workspace(),
        "radarRuns": [payload["run"]],
        "foundMaterials": payload["foundMaterials"],
        "sourceSignals": payload["sourceSignals"],
    }
    retry = client.post(
        f"/api/radar-runs/{payload['run']['id']}/signal-extraction",
        json={"workspace": retry_workspace, "forceRetry": True},
    )
    assert retry.status_code == 200
    assert retry.json()["signalExtractionReport"]["revision"] == 2
    assert retry.json()["sourceSignals"][0]["id"] == payload["sourceSignals"][0]["id"]
    assert search.calls == 3
    assert reader.calls == 1
    assert extraction.calls == 2


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
        "foundMaterials": [],
        "sourceSignals": [],
    }
