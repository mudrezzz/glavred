"""Owner: upstream.application

Used by: recorded upstream Radar benchmark runner and tests.
Does not own: provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


BenchmarkStatus = Literal["passed", "warning", "failed"]


@dataclass(frozen=True)
class RadarBenchmarkScenario:
    id: str
    project_id: str
    radar_id: str
    expected_intent_families: tuple[str, ...]
    optional_intent_families: tuple[str, ...]
    expected_evidence_types: tuple[str, ...]
    minimum_raw_results: int
    minimum_selected_reads: int
    minimum_found_materials: int
    minimum_distinct_domains: int
    unacceptable_noise_terms: tuple[str, ...]

    def workspace(self) -> dict[str, Any]:
        return {
            "projectProfile": {
                "id": self.project_id,
                "name": "Опытный цех «Сборочная»",
                "language": "en",
                "researchDepth": "standard",
                "benchmarkRole": "industrial-ai-pattern-quality",
            },
            "topics": [{"id": "ai-pattern-topic-industrial-artifacts", "title": "Industrial AI artifacts"}],
            "fabulas": [{"id": "ai-pattern-fabula-pattern-card", "title": "Pattern card"}],
            "publisherRules": [
                {"statement": "Prefer public operational proof, implementation constraints, and explicit human accountability."}
            ],
            "sourceRegistry": {
                "handles": [
                    {
                        "id": "ai-pattern-source-industrial-web",
                        "type": "openWebQuery",
                        "title": "Industrial AI web",
                        "locator": "industrial AI maintenance predictive maintenance EAM reliability decision support",
                        "status": "active",
                        "capabilities": {"canSearch": True, "canReadUrl": False},
                    }
                ]
            },
            "radars": [
                {
                    "id": self.radar_id,
                    "title": "Industrial AI cases",
                    "scope": "Find practical industrial AI cases with data, user roles, constraints, and results.",
                    "sourceHandleIds": ["ai-pattern-source-industrial-web"],
                    "rules": [
                        {"statement": "Find industrial AI cases with implementation evidence, constraints, and operational outcomes."}
                    ],
                }
            ],
            "radarRuns": [],
            "foundMaterials": [],
            "sourceSignals": [],
            "postCandidates": [],
            "contentPlanItems": [],
            "draftRuns": [],
        }


@dataclass(frozen=True)
class RadarBenchmarkReport:
    scenario_id: str
    status: BenchmarkStatus
    counters: dict[str, int]
    missing_expectations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    unacceptable_noise_hits: list[str] = field(default_factory=list)
    downstream_leaks: list[str] = field(default_factory=list)
    trace_complete: bool = False
    run: dict[str, Any] = field(default_factory=dict)
    found_materials: list[dict[str, Any]] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "scenarioId": self.scenario_id,
            "status": self.status,
            "counters": self.counters,
            "missingExpectations": self.missing_expectations,
            "warnings": self.warnings,
            "unacceptableNoiseHits": self.unacceptable_noise_hits,
            "downstreamLeaks": self.downstream_leaks,
            "traceComplete": self.trace_complete,
            "run": self.run,
            "foundMaterials": self.found_materials,
        }


GOLDEN_RADAR_BENCHMARK_SCENARIOS = (
    RadarBenchmarkScenario(
        id="benchmark-industrial-ai-maintenance-cases",
        project_id="project-ai-design-patterns",
        radar_id="ai-pattern-radar-industrial-cases",
        expected_intent_families=("broadDiscovery", "caseExample", "benchmarkPaper", "limitationCritique"),
        optional_intent_families=("ossTooling",),
        expected_evidence_types=("overview", "caseExample", "benchmarkPaper", "limitationCritique"),
        minimum_raw_results=5,
        minimum_selected_reads=2,
        minimum_found_materials=2,
        minimum_distinct_domains=2,
        unacceptable_noise_terms=("generic ai news", "model leaderboard", "pricing", "vendor pricing", "buy now"),
    ),
)


def get_golden_radar_benchmark_scenarios() -> list[RadarBenchmarkScenario]:
    return list(GOLDEN_RADAR_BENCHMARK_SCENARIOS)


__all__ = (
    "BenchmarkStatus",
    "GOLDEN_RADAR_BENCHMARK_SCENARIOS",
    "RadarBenchmarkReport",
    "RadarBenchmarkScenario",
    "get_golden_radar_benchmark_scenarios",
)
