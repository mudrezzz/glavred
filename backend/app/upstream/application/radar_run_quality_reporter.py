"""Owner: upstream.application

Used by: RadarRun completion and retry paths after signal scoring.
Does not own: retrieval, extraction, scoring, benchmark policy, persistence, or UI.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.radar_benchmark_reporter import RadarRunBenchmarkReporter
from backend.app.upstream.application.search_opportunity_report import SearchOpportunityCoverageReportBuilder


class RadarRunQualityReporter:
    def __init__(self) -> None:
        self._opportunity = SearchOpportunityCoverageReportBuilder()
        self._benchmark = RadarRunBenchmarkReporter()

    def attach(
        self,
        *,
        workspace: dict[str, Any],
        project_id: str | None,
        radar_id: str,
        run: dict[str, Any],
        found_materials: list[dict[str, Any]],
        source_signals: list[dict[str, Any]],
    ) -> dict[str, Any]:
        opportunity = self._opportunity.build(
            run=run,
            found_materials=found_materials,
            source_signals=source_signals,
        ).to_payload()
        run["searchOpportunityCoverage"] = opportunity
        self._benchmark.attach_if_matching(
            workspace=workspace,
            project_id=project_id,
            radar_id=radar_id,
            run=run,
            found_materials=found_materials,
            source_signals=source_signals,
            search_opportunity=opportunity,
        )
        return opportunity


__all__ = ("RadarRunQualityReporter",)
