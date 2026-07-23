"""Owner: upstream.application

Used by: UpstreamRadarExternalRunService.
Does not own: provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.benchmark.evaluator import evaluate_live_radar_run
from backend.app.upstream.application.benchmark.scenarios import find_golden_radar_benchmark_scenario


class RadarRunBenchmarkReporter:
    def attach_if_matching(
        self,
        *,
        workspace: dict[str, Any],
        project_id: str | None = None,
        radar_id: str,
        run: dict[str, Any],
        found_materials: list[dict[str, Any]],
        source_signals: list[dict[str, Any]] | None = None,
        search_opportunity: dict[str, Any] | None = None,
    ) -> None:
        scenario = find_golden_radar_benchmark_scenario(
            project_id=project_id or self._project_id(workspace),
            radar_id=radar_id,
        )
        if scenario:
            run["benchmarkReport"] = evaluate_live_radar_run(
                scenario=scenario,
                run=run,
                found_materials=found_materials,
                source_signals=source_signals or [],
                search_opportunity=search_opportunity or {},
            ).to_payload()

    def _project_id(self, workspace: dict[str, Any]) -> str | None:
        profile = workspace.get("projectProfile") if isinstance(workspace.get("projectProfile"), dict) else {}
        value = profile.get("id")
        return str(value) if value else None
