"""Owner: upstream.application

Used by: recorded upstream Radar benchmark tests and developer diagnostics.
Does not own: live provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md
"""

from __future__ import annotations

from typing import Any

from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings
from backend.app.upstream.application.benchmark.recorded_adapters import (
    RecordedRadarFixture,
    RecordedRadarSearchAdapter,
    RecordedUrlReader,
)
from backend.app.upstream.application.benchmark.evaluator import RadarBenchmarkEvaluator
from backend.app.upstream.application.benchmark.scenarios import (
    RadarBenchmarkReport,
    RadarBenchmarkScenario,
    get_golden_radar_benchmark_scenarios,
)
from backend.app.upstream.application.external_run_service import UpstreamRadarExternalRunService
from backend.app.upstream.application.search_opportunity_report import SearchOpportunityCoverageReportBuilder


class RadarBenchmarkRunner:
    def __init__(self) -> None:
        self._evaluator = RadarBenchmarkEvaluator()

    def run(self, scenario: RadarBenchmarkScenario) -> RadarBenchmarkReport:
        fixture = RecordedRadarFixture.load(f"{scenario.id}.json")
        workspace = scenario.workspace()
        service = UpstreamRadarExternalRunService(
            settings=BackendSettings(
                _env_file=None,
                OPENROUTER_API_KEY="recorded-token",
                OPENROUTER_DEFAULT_MODEL="recorded-model",
                OPENROUTER_WEB_TOOLS_ENABLED=True,
                OPENROUTER_WEB_SEARCH_MODEL="recorded-model",
                DRAFT_RUN_EXECUTION_MODE="standard",
            ),
            web_search_adapter=RecordedRadarSearchAdapter(fixture),
            url_reader=RecordedUrlReader(fixture),
            openrouter_validator=OpenRouterConfigValidator(),
        )
        result = service.run(workspace=workspace, radar_id=scenario.radar_id)
        source_signals = fixture.source_signals(
            run_id=str(result["run"]["id"]),
            radar_id=scenario.radar_id,
            found_materials=result["foundMaterials"],
        )
        opportunity = SearchOpportunityCoverageReportBuilder().build(
            run=result["run"],
            found_materials=result["foundMaterials"],
            source_signals=source_signals,
        ).to_payload()
        result["run"]["searchOpportunityCoverage"] = opportunity
        result["sourceSignals"] = source_signals
        return self._report(scenario=scenario, workspace=workspace, result=result)

    def _report(
        self,
        *,
        scenario: RadarBenchmarkScenario,
        workspace: dict[str, Any],
        result: dict[str, Any],
    ) -> RadarBenchmarkReport:
        return self._evaluator.evaluate(
            scenario=scenario,
            run=result["run"],
            found_materials=result["foundMaterials"],
            workspace=workspace,
            result=result,
            evaluation_mode="recorded",
            source_signals=result.get("sourceSignals") or [],
            search_opportunity=result["run"].get("searchOpportunityCoverage") or {},
        )


def run_radar_benchmark(scenario_id: str) -> RadarBenchmarkReport:
    scenarios = {scenario.id: scenario for scenario in get_golden_radar_benchmark_scenarios()}
    if scenario_id not in scenarios:
        raise ValueError(f"Unknown radar benchmark scenario: {scenario_id}")
    return RadarBenchmarkRunner().run(scenarios[scenario_id])


__all__ = ("RadarBenchmarkRunner", "get_golden_radar_benchmark_scenarios", "run_radar_benchmark")
