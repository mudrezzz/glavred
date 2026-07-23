from typing import Any

from backend.app.application.public_evidence_ports import PublicUrlReadResult
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.openrouter_web_search_adapter import OpenRouterWebSearchCitation, OpenRouterWebSearchResult
from backend.app.settings import BackendSettings
from backend.app.upstream.application.external_run_service import UpstreamRadarExternalRunService


class FakeWebSearchAdapter:
    def search(self, **kwargs: Any) -> OpenRouterWebSearchResult:
        return OpenRouterWebSearchResult(
            content="Search content",
            citations=[
                OpenRouterWebSearchCitation(title="Industrial AI case", url="https://example.com/case?utm_source=test", snippet="implementation case with benchmark metrics"),
                OpenRouterWebSearchCitation(title="Industrial AI case duplicate", url="https://example.com/case", snippet="same case"),
                OpenRouterWebSearchCitation(title="Generic vendor page", url="https://vendor.example/pricing", snippet="buy now pricing vendor"),
            ],
            raw_response={"id": "search-1"},
        )


class FakeUrlReader:
    def read(self, url: str) -> PublicUrlReadResult:
        if "vendor" in url:
            raise RuntimeError("blocked")
        return PublicUrlReadResult(
            url=url,
            final_url=url,
            title="Read " + url,
            text="Detailed industrial AI implementation case with lessons and metrics.",
        )


def test_external_radar_run_builds_search_plan_and_found_materials() -> None:
    result = service().run(workspace=workspace(), radar_id="radar-1")
    run = result["run"]

    assert run["searchPlan"]["queries"]
    assert run["searchPlan"]["intents"]
    assert run["searchPlan"]["trace"]["plannerVersion"] == "deterministic-search-campaign-v3"
    assert run["searchPlan"]["requirementProfile"]["requirements"]
    assert "searchOpportunityCoverage" in run
    assert run["searchPlan"]["sourceStrategy"]["searchableSourceHandleIds"] == ["source-open-web"]
    assert run["rawResults"]
    assert run["selectedForRead"]
    assert run["rejectedBeforeRead"]
    assert run["foundMaterialIds"] == [result["foundMaterials"][0]["id"]]
    assert result["foundMaterials"][0]["type"] == "searchResult"
    assert result["foundMaterials"][0]["summary"].startswith("Detailed industrial AI")
    assert all(signal.get("id") != result["foundMaterials"][0]["id"] for signal in workspace()["sourceSignals"])


def test_external_radar_run_deduplicates_before_reading() -> None:
    result = service().run(workspace=workspace(), radar_id="radar-1")
    run = result["run"]

    assert any(item["reason"] == "duplicate-url" for item in run["rejectedBeforeRead"])
    assert run["budget"]["usedUrlReads"] == 1
    assert len(result["foundMaterials"]) == 1


def test_external_radar_run_records_provider_not_configured() -> None:
    result = service(web_enabled=False).run(workspace=workspace(), radar_id="radar-1")
    run = result["run"]

    assert run["foundMaterialIds"] == []
    assert run["searchPlan"]["intents"]
    assert run["searchPlan"]["trace"]["intentCoverage"]
    assert run["operations"][0]["status"] == "skipped"
    assert run["operations"][0]["skippedReason"] == "openrouter-web-tools-disabled"
    assert "no-raw-search-results" in run["warnings"]


def service(*, web_enabled: bool = True) -> UpstreamRadarExternalRunService:
    return UpstreamRadarExternalRunService(
        settings=BackendSettings(
            OPENROUTER_API_KEY="test-token",
            OPENROUTER_DEFAULT_MODEL="test-model",
            OPENROUTER_WEB_TOOLS_ENABLED=web_enabled,
            OPENROUTER_WEB_SEARCH_MODEL="test-model",
            DRAFT_RUN_EXECUTION_MODE="smoke",
        ),
        web_search_adapter=FakeWebSearchAdapter(),
        url_reader=FakeUrlReader(),
        openrouter_validator=OpenRouterConfigValidator(),
    )


def workspace() -> dict[str, Any]:
    return {
        "projectProfile": {"language": "en"},
        "sourceRegistry": {
            "handles": [
                {
                    "id": "source-open-web",
                    "type": "openWebQuery",
                    "title": "Industrial AI web",
                    "locator": "industrial AI maintenance",
                    "status": "active",
                    "capabilities": {"canSearch": True, "canReadUrl": False},
                }
            ]
        },
        "radars": [
            {
                "id": "radar-1",
                "title": "Industrial AI radar",
                "scope": "Find industrial AI implementation patterns",
                "sourceHandleIds": ["source-open-web"],
                "rules": [{"statement": "Predictive maintenance with operational proof"}],
            }
        ],
        "radarRuns": [],
        "sourceSignals": [{"id": "signal-existing"}],
    }
