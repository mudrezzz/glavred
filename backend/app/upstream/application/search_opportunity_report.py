"""Owner: upstream.application

Used by: RadarRun completion and signal extraction/scoring retries.
Does not own: search execution, signal semantics, benchmark scenario selection, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from backend.app.upstream.domain.search_opportunity import SearchOpportunityCoverageReport, YieldMetric


class SearchOpportunityCoverageReportBuilder:
    REVIEW_ELIGIBLE = {"recommended", "reviewWithCaution"}

    def build(
        self,
        *,
        run: dict[str, Any],
        found_materials: list[dict[str, Any]],
        source_signals: list[dict[str, Any]],
    ) -> SearchOpportunityCoverageReport:
        search_plan = run.get("searchPlan") if isinstance(run.get("searchPlan"), dict) else {}
        profile = search_plan.get("requirementProfile") if isinstance(search_plan.get("requirementProfile"), dict) else {}
        requirements = {
            str(item.get("id")): item
            for item in profile.get("requirements", [])
            if isinstance(item, dict) and item.get("id")
        }
        queries = {
            str(item.get("id")): item
            for item in search_plan.get("queries", [])
            if isinstance(item, dict) and item.get("id")
        }
        raw_results = [item for item in run.get("rawResults", []) if isinstance(item, dict)]
        executed_query_ids = {str(item.get("queryId")) for item in raw_results if item.get("queryId")}
        executed_query_ids.update(self._successful_query_ids(run, queries))
        executed_requirements = {
            str(requirement_id)
            for query_id in executed_query_ids
            for requirement_id in queries.get(query_id, {}).get("requirementIds", [])
            if requirement_id
        }
        planned_requirements = tuple(requirements)
        uncovered = tuple(
            item for item in search_plan.get("uncoveredRequiredSearchRequirements", []) if isinstance(item, dict)
        )
        readable_materials = [item for item in found_materials if item.get("status") != "metadataOnly"]
        recommendations = Counter(
            str((item.get("utilityReport") or {}).get("recommendation") or "inconclusive")
            for item in source_signals
        )
        eligible_count = sum(recommendations[item] for item in self.REVIEW_ELIGIBLE)
        rejected_count = recommendations["notRecommended"]
        provider_inconclusive = self._provider_inconclusive(run, source_signals)
        first_failure = self._first_failure(
            executed_query_ids=executed_query_ids,
            raw_results=raw_results,
            readable_materials=readable_materials,
            signals=source_signals,
            eligible_count=eligible_count,
        )
        status = self._status(
            provider_inconclusive=provider_inconclusive,
            eligible_count=eligible_count,
            signal_count=len(source_signals),
            uncovered=uncovered,
        )
        reason_codes = self._reason_codes(status, first_failure, provider_inconclusive, uncovered)
        lineage, unresolved = self._lineage(
            requirements=requirements,
            queries=queries,
            raw_results=raw_results,
            found_materials=found_materials,
            source_signals=source_signals,
        )
        family_planned = sorted({str(item.get("family")) for item in search_plan.get("intents", []) if isinstance(item, dict) and item.get("family")})
        family_executed = sorted({str(queries[item].get("family")) for item in executed_query_ids if item in queries and queries[item].get("family")})
        evidence_planned = sorted({str(item.get("evidenceTarget") or item.get("evidenceType")) for item in search_plan.get("intents", []) if isinstance(item, dict) and (item.get("evidenceTarget") or item.get("evidenceType"))})
        evidence_executed = sorted({str(queries[item].get("evidenceTarget") or queries[item].get("evidenceType")) for item in executed_query_ids if item in queries and (queries[item].get("evidenceTarget") or queries[item].get("evidenceType"))})
        return SearchOpportunityCoverageReport(
            status=status,
            planned_requirement_ids=planned_requirements,
            executed_requirement_ids=tuple(sorted(executed_requirements)),
            uncovered_requirements=uncovered,
            family_coverage={"planned": family_planned, "executed": family_executed},
            evidence_coverage={"planned": evidence_planned, "executed": evidence_executed},
            counts={
                "queryCount": len(executed_query_ids),
                "rawResultCount": len(raw_results),
                "readableMaterialCount": len(readable_materials),
                "signalCount": len(source_signals),
                "reviewEligibleCount": eligible_count,
                "notRecommendedCount": rejected_count,
            },
            extracted_signal_yield=YieldMetric(len(source_signals), len(readable_materials)),
            review_eligible_yield=YieldMetric(eligible_count, len(source_signals)),
            rejected_yield=YieldMetric(rejected_count, len(source_signals)),
            recommendation_distribution=dict(sorted(recommendations.items())),
            reason_distribution=dict(sorted(Counter(reason_codes).items())),
            first_failure_stage=first_failure,
            reason_codes=tuple(reason_codes),
            remediation=tuple(self._remediation(first_failure, provider_inconclusive)),
            lineage=tuple(lineage),
            unresolved_handles=unresolved,
        )

    def _successful_query_ids(self, run: dict[str, Any], queries: dict[str, dict[str, Any]]) -> set[str]:
        targets = {
            str(item.get("target")) for item in run.get("operations", [])
            if isinstance(item, dict) and item.get("kind") == "openWebQuery" and item.get("status") == "succeeded"
        }
        return {query_id for query_id, query in queries.items() if str(query.get("query")) in targets}

    def _provider_inconclusive(self, run: dict[str, Any], source_signals: list[dict[str, Any]]) -> bool:
        terminal_signals = bool(source_signals) and all(
            str((item.get("utilityReport") or {}).get("recommendation") or "inconclusive") != "inconclusive"
            for item in source_signals
        )
        reports = [run.get("signalExtraction"), run.get("signalScoring")]
        if not terminal_signals and any(isinstance(report, dict) and report.get("status") in {"inconclusive", "notRun"} for report in reports):
            return True
        return any(
            isinstance(item, dict)
            and item.get("kind") == "openWebQuery"
            and item.get("status") in {"failed", "skipped"}
            and any(marker in str(item.get("error") or item.get("skippedReason") or "").lower() for marker in ("provider", "openrouter", "timeout", "not-configured"))
            for item in run.get("operations", [])
        )

    def _first_failure(self, *, executed_query_ids, raw_results, readable_materials, signals, eligible_count):
        if not executed_query_ids:
            return "providerSearch"
        if not raw_results:
            return "triage"
        if not readable_materials:
            return "read"
        if not signals:
            return "signalExtraction"
        if not eligible_count:
            return "signalScoring"
        return None

    def _status(self, *, provider_inconclusive: bool, eligible_count: int, signal_count: int, uncovered) -> str:
        if provider_inconclusive and eligible_count == 0:
            return "inconclusive"
        if eligible_count > 0 and not uncovered:
            return "sufficient"
        if eligible_count > 0 or signal_count > 0:
            return "partial"
        return "zeroYield"

    def _reason_codes(self, status: str, first_failure: str | None, provider_inconclusive: bool, uncovered) -> list[str]:
        reasons = [f"first-failure-{first_failure}" if first_failure else "review-eligible-signal-found"]
        if uncovered:
            reasons.append("required-search-requirement-uncovered")
        if provider_inconclusive:
            reasons.append("provider-runtime-inconclusive")
        if status == "zeroYield":
            reasons.append("zero-review-eligible-yield")
        return reasons

    def _remediation(self, stage: str | None, provider_inconclusive: bool) -> list[str]:
        if provider_inconclusive:
            return ["Повторить запуск после восстановления provider/runtime."]
        return {
            "providerSearch": ["Проверить provider search и покрытие обязательных запросов."],
            "triage": ["Проверить формулировки запросов и причины отклонения raw results."],
            "read": ["Проверить доступность URL и бюджет чтения."],
            "signalExtraction": ["Проверить доказательные фрагменты и решения extraction."],
            "signalScoring": ["Проверить blocking-критерии и причины utility verdict."],
        }.get(stage, [])

    def _lineage(self, *, requirements, queries, raw_results, found_materials, source_signals):
        raw_by_id = {str(item.get("id")): item for item in raw_results if item.get("id")}
        material_by_id = {str(item.get("id")): item for item in found_materials if item.get("id")}
        fragment_ids = {
            str(fragment.get("id"))
            for material in found_materials
            for fragment in material.get("contentFragments", [])
            if isinstance(fragment, dict) and fragment.get("id")
        }
        unresolved = Counter({"requirement": 0, "query": 0, "material": 0, "fragment": 0})
        lineage: list[dict[str, Any]] = []
        for material in found_materials:
            trace = material.get("discoveryTrace") if isinstance(material.get("discoveryTrace"), dict) else {}
            requirement_ids = [str(item) for item in trace.get("requirementIds", []) if item]
            query_ids = [str(item) for item in trace.get("queryIds", []) if item]
            unresolved["requirement"] += sum(item not in requirements for item in requirement_ids)
            unresolved["query"] += sum(item not in queries for item in query_ids)
            lineage.append({
                "kind": "material",
                "materialId": material.get("id"),
                "requirementIds": requirement_ids,
                "queryIds": query_ids,
                "rawResultIds": [item for item in trace.get("rawResultIds", []) if str(item) in raw_by_id],
            })
        for signal in source_signals:
            refs = [item for item in signal.get("evidenceRefs", []) if isinstance(item, dict)]
            material_ids = [str(item.get("materialId")) for item in refs if item.get("materialId")]
            signal_requirement_ids = sorted({
                str(requirement_id)
                for material_id in material_ids
                for requirement_id in (material_by_id.get(material_id, {}).get("discoveryTrace") or {}).get("requirementIds", [])
                if requirement_id
            })
            unresolved["material"] += sum(item not in material_by_id for item in material_ids)
            unresolved["fragment"] += sum(str(item.get("fragmentId")) not in fragment_ids for item in refs if item.get("fragmentId"))
            lineage.append({
                "kind": "signal",
                "signalId": signal.get("id"),
                "requirementIds": signal_requirement_ids,
                "materialIds": material_ids,
                "fragmentIds": [str(item.get("fragmentId")) for item in refs if item.get("fragmentId")],
                "recommendation": (signal.get("utilityReport") or {}).get("recommendation"),
            })
        return lineage, dict(unresolved)


__all__ = ("SearchOpportunityCoverageReportBuilder",)
