"""Owner: upstream.application

Used by: recorded upstream Radar benchmark tests and developer diagnostics.
Does not own: provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = (
    "RadarBenchmarkEvaluator",
    "RadarBenchmarkReport",
    "RadarBenchmarkScenario",
    "evaluate_live_radar_run",
    "get_golden_radar_benchmark_scenarios",
    "run_radar_benchmark",
)


def __getattr__(name: str) -> Any:
    if name in {"get_golden_radar_benchmark_scenarios", "run_radar_benchmark"}:
        runner = import_module("backend.app.upstream.application.benchmark.runner")
        return getattr(runner, name)
    if name in {"RadarBenchmarkEvaluator", "evaluate_live_radar_run"}:
        evaluator = import_module("backend.app.upstream.application.benchmark.evaluator")
        return getattr(evaluator, name)
    if name in {"RadarBenchmarkReport", "RadarBenchmarkScenario"}:
        scenarios = import_module("backend.app.upstream.application.benchmark.scenarios")
        return getattr(scenarios, name)
    raise AttributeError(name)
