"""Owner: upstream.application

Used by: recorded upstream Radar benchmark tests and developer diagnostics.
Does not own: provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md
"""

from backend.app.upstream.application.benchmark.runner import (
    get_golden_radar_benchmark_scenarios,
    run_radar_benchmark,
)
from backend.app.upstream.application.benchmark.scenarios import (
    RadarBenchmarkReport,
    RadarBenchmarkScenario,
)

__all__ = (
    "RadarBenchmarkReport",
    "RadarBenchmarkScenario",
    "get_golden_radar_benchmark_scenarios",
    "run_radar_benchmark",
)
