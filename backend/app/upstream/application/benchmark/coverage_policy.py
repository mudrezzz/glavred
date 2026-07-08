"""Owner: upstream.application

Used by: Radar benchmark evaluator.
Does not own: provider transport, API routing, UI rendering, signal scoring, or DraftRun.
Architecture doc: docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.benchmark.scenarios import RadarBenchmarkScenario


class RadarBenchmarkCoveragePolicy:
    def coverage(
        self,
        *,
        scenario: RadarBenchmarkScenario,
        intent_families: set[str],
        evidence_types: set[str],
        selected_domains: set[str],
        trace_complete: bool,
    ) -> dict[str, Any]:
        return {
            "queryFamilies": {
                "expected": list(scenario.expected_intent_families),
                "covered": sorted(intent_families),
                "missing": [family for family in scenario.expected_intent_families if family not in intent_families],
                "optionalMissing": [family for family in scenario.optional_intent_families if family not in intent_families],
            },
            "evidenceTypes": {
                "expected": list(scenario.expected_evidence_types),
                "covered": sorted(evidence_types),
                "missing": [item for item in scenario.expected_evidence_types if item not in evidence_types],
            },
            "domains": {
                "minimum": scenario.minimum_distinct_domains,
                "covered": sorted(selected_domains),
            },
            "traceComplete": trace_complete,
        }

    def skipped_required_coverage(
        self,
        *,
        scenario: RadarBenchmarkScenario,
        missing_families: set[str],
        missing_evidence_types: set[str],
        skipped_intents: list[dict[str, Any]],
        planned_intents: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        planned_by_id = {str(item.get("id")): item for item in planned_intents if isinstance(item, dict)}
        entries: list[dict[str, Any]] = []
        for skipped in skipped_intents:
            if not isinstance(skipped, dict):
                continue
            intent_id = str(skipped.get("intentId") or skipped.get("id") or "")
            planned = planned_by_id.get(intent_id, {})
            family = str(skipped.get("family") or planned.get("family") or "")
            evidence_type = str(planned.get("evidenceType") or "")
            if family in scenario.expected_intent_families and family in missing_families:
                entries.append(
                    {
                        "kind": "queryFamily",
                        "value": family,
                        "reason": str(skipped.get("reason") or "skipped"),
                        "intentId": intent_id,
                    }
                )
            if evidence_type in scenario.expected_evidence_types and evidence_type in missing_evidence_types:
                entries.append(
                    {
                        "kind": "evidenceType",
                        "value": evidence_type,
                        "reason": str(skipped.get("reason") or "skipped"),
                        "intentId": intent_id,
                    }
                )
        return self._unique_entries(entries)

    def _unique_entries(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[str, str, str, str]] = set()
        unique = []
        for entry in entries:
            key = (
                str(entry.get("kind") or ""),
                str(entry.get("value") or ""),
                str(entry.get("reason") or ""),
                str(entry.get("intentId") or ""),
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(entry)
        return unique
