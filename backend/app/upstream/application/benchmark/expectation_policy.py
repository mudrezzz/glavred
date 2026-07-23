"""Owner: upstream.application

Used by: Radar benchmark evaluator.
Does not own: provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.benchmark.scenarios import RadarBenchmarkScenario


class RadarBenchmarkExpectationPolicy:
    def missing_expectations(
        self,
        *,
        scenario: RadarBenchmarkScenario,
        intent_families: set[str],
        evidence_types: set[str],
        raw_results: list[dict[str, Any]],
        selected: list[dict[str, Any]],
        found_materials: list[dict[str, Any]],
        selected_domains: set[str],
    ) -> list[str]:
        missing = [
            f"intent-family:{family}"
            for family in scenario.expected_intent_families
            if family not in intent_families
        ]
        missing.extend(
            f"evidence-type:{evidence_type}"
            for evidence_type in scenario.expected_evidence_types
            if evidence_type not in evidence_types
        )
        thresholds = {
            "raw-results": (len(raw_results), scenario.minimum_raw_results),
            "selected-reads": (len(selected), scenario.minimum_selected_reads),
            "found-materials": (len(found_materials), scenario.minimum_found_materials),
            "distinct-domains": (len(selected_domains), scenario.minimum_distinct_domains),
        }
        missing.extend(f"{name}:{actual}/{expected}" for name, (actual, expected) in thresholds.items() if actual < expected)
        return missing

    def accepted_noise_hits(self, *, scenario: RadarBenchmarkScenario, found_materials: list[dict[str, Any]]) -> list[str]:
        hits = []
        for material in found_materials:
            text = f"{material.get('title', '')} {material.get('snippet', '')} {material.get('summary', '')}".lower()
            if any(term in text for term in scenario.unacceptable_noise_terms):
                hits.append(str(material.get("id") or material.get("title") or "found-material"))
        return hits

    def downstream_leaks(self, *, workspace: dict[str, Any], result: dict[str, Any]) -> list[str]:
        leaks = []
        if result.get("postCandidates"):
            leaks.append("postCandidates")
        if result.get("draftRuns"):
            leaks.append("draftRuns")
        for key in ("postCandidates", "contentPlanItems", "draftRuns"):
            if workspace.get(key):
                leaks.append(f"workspace-input:{key}")
        return leaks
