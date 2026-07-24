"""Owner: upstream.application

Used by: SearchOpportunityCoverageReportBuilder.
Does not own: delivery stages, recommendation policy, search execution, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from collections import Counter
from typing import Any


class SearchOpportunityMetricsBuilder:
    """Build readable/used evidence coverage and claim-support diagnostics."""

    def coverage(
        self,
        *,
        search_plan: dict[str, Any],
        queries: dict[str, dict[str, Any]],
        executed_query_ids: set[str],
        readable_materials: list[dict[str, Any]],
        source_signals: list[dict[str, Any]],
        review_eligible: set[str],
    ) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
        family_planned = self._intent_values(search_plan, "family")
        family_executed = self._query_values(
            queries, executed_query_ids, "family"
        )
        evidence_planned = self._intent_values(
            search_plan, "evidenceTarget", "evidenceType"
        )
        evidence_executed = self._query_values(
            queries, executed_query_ids, "evidenceTarget", "evidenceType"
        )
        family_readable, evidence_readable = self._material_coverage(
            readable_materials
        )
        used_material_ids = {
            str(ref.get("materialId") or "")
            for signal in source_signals
            if str(
                (signal.get("utilityReport") or {}).get("recommendation") or ""
            )
            in review_eligible
            for ref in signal.get("evidenceRefs", [])
            if isinstance(ref, dict) and ref.get("materialId")
        }
        family_used, evidence_used = self._material_coverage(
            [
                item
                for item in readable_materials
                if str(item.get("id") or "") in used_material_ids
            ]
        )
        return (
            {
                "planned": family_planned,
                "executed": family_executed,
                "readable": family_readable,
                "usedBySignal": family_used,
            },
            {
                "planned": evidence_planned,
                "executed": evidence_executed,
                "readable": evidence_readable,
                "usedBySignal": evidence_used,
            },
        )

    def corroboration(self, source_signals: list[dict[str, Any]]) -> dict[str, Any]:
        claim_support = Counter(self._claim_support(item) for item in source_signals)
        gaps = [
            {
                "signalId": str(item.get("id") or ""),
                "reason": (
                    "corroboration-not-found"
                    if self._claim_support(item) == "singleSource"
                    else "source-support-not-checked"
                ),
            }
            for item in source_signals
            if self._claim_support(item) in {"singleSource", "notChecked"}
        ]
        return {
            "corroboratedCount": claim_support["corroborated"],
            "singleSourceCount": claim_support["singleSource"],
            "contradictedCount": claim_support["contradicted"],
            "notCheckedCount": claim_support["notChecked"],
            "gaps": gaps,
        }

    def _material_coverage(
        self,
        materials: list[dict[str, Any]],
    ) -> tuple[list[str], list[str]]:
        families = sorted(
            {
                str(value)
                for item in materials
                for value in (item.get("discoveryTrace") or {}).get("families", [])
                if value
            }
        )
        evidence = sorted(
            {
                str(value)
                for item in materials
                for value in (item.get("discoveryTrace") or {}).get(
                    "evidenceTypes", []
                )
                if value
            }
        )
        return families, evidence

    def _intent_values(
        self,
        search_plan: dict[str, Any],
        primary: str,
        fallback: str | None = None,
    ) -> list[str]:
        return sorted(
            {
                str(item.get(primary) or (item.get(fallback) if fallback else ""))
                for item in search_plan.get("intents", [])
                if isinstance(item, dict)
                and (item.get(primary) or (fallback and item.get(fallback)))
            }
        )

    def _query_values(
        self,
        queries: dict[str, dict[str, Any]],
        query_ids: set[str],
        primary: str,
        fallback: str | None = None,
    ) -> list[str]:
        return sorted(
            {
                str(
                    queries[item].get(primary)
                    or (queries[item].get(fallback) if fallback else "")
                )
                for item in query_ids
                if item in queries
                and (
                    queries[item].get(primary)
                    or (fallback and queries[item].get(fallback))
                )
            }
        )

    def _claim_support(self, signal: dict[str, Any]) -> str:
        checks = (signal.get("utilityReport") or {}).get("qualityChecks") or []
        source = next(
            (
                item
                for item in checks
                if isinstance(item, dict) and item.get("checkId") == "source-posture"
            ),
            {},
        )
        return str((source.get("details") or {}).get("claimSupport") or "notChecked")


__all__ = ("SearchOpportunityMetricsBuilder",)
