"""Owner: upstream.application

Used by: RadarRun completion and signal extraction/scoring retries.
Does not own: search execution, signal semantics, benchmark scenario selection, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from backend.app.upstream.application.search_evidence_delivery import SearchEvidenceDeliveryPolicy
from backend.app.upstream.application.search_opportunity_lineage import SearchOpportunityLineageBuilder
from backend.app.upstream.application.search_opportunity_metrics import SearchOpportunityMetricsBuilder
from backend.app.upstream.application.search_opportunity_status import SearchOpportunityStatusPolicy
from backend.app.upstream.domain.search_opportunity import SearchOpportunityCoverageReport, YieldMetric


class SearchOpportunityCoverageReportBuilder:
    REVIEW_ELIGIBLE = {"recommended", "reviewWithCaution"}

    def __init__(self) -> None:
        self._delivery = SearchEvidenceDeliveryPolicy()
        self._lineage_builder = SearchOpportunityLineageBuilder()
        self._metrics = SearchOpportunityMetricsBuilder()
        self._status_policy = SearchOpportunityStatusPolicy()

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
        requirement_coverage = self._delivery.build(
            run=run,
            requirements=requirements,
            queries=queries,
            executed_query_ids=executed_query_ids,
            found_materials=found_materials,
            source_signals=source_signals,
        )
        required_delivery_gaps = tuple(
            {
                "requirementId": item.requirement_id,
                "furthestStage": item.furthest_stage,
                "reason": item.stop_reason or "required-evidence-not-delivered",
            }
            for item in requirement_coverage
            if item.role == "required" and not item.delivered
        )
        optional_delivery_gaps = tuple(
            {
                "requirementId": item.requirement_id,
                "furthestStage": item.furthest_stage,
                "reason": item.stop_reason or "optional-evidence-not-delivered",
            }
            for item in requirement_coverage
            if item.role in {"optional", "tension"} and not item.delivered
        )
        provider_inconclusive = self._status_policy.provider_inconclusive(
            run, source_signals
        )
        first_failure = self._status_policy.first_failure(
            executed_query_ids=executed_query_ids,
            raw_results=raw_results,
            readable_materials=readable_materials,
            signals=source_signals,
            eligible_count=eligible_count,
        )
        delivery_gaps = (*uncovered, *required_delivery_gaps)
        status = self._status_policy.status(
            provider_inconclusive=provider_inconclusive,
            eligible_count=eligible_count,
            signal_count=len(source_signals),
            uncovered=delivery_gaps,
        )
        reason_codes = self._status_policy.reason_codes(
            status=status,
            first_failure=first_failure,
            provider_inconclusive=provider_inconclusive,
            uncovered=delivery_gaps,
        )
        lineage, unresolved = self._lineage_builder.build(
            run=run,
            requirements=requirements,
            queries=queries,
            raw_results=raw_results,
            found_materials=found_materials,
            source_signals=source_signals,
        )
        family_coverage, evidence_coverage = self._metrics.coverage(
            search_plan=search_plan,
            queries=queries,
            executed_query_ids=executed_query_ids,
            readable_materials=readable_materials,
            source_signals=source_signals,
            review_eligible=self.REVIEW_ELIGIBLE,
        )
        return SearchOpportunityCoverageReport(
            status=status,
            planned_requirement_ids=planned_requirements,
            executed_requirement_ids=tuple(sorted(executed_requirements)),
            uncovered_requirements=uncovered,
            family_coverage=family_coverage,
            evidence_coverage=evidence_coverage,
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
            remediation=tuple(
                self._status_policy.remediation(first_failure, provider_inconclusive)
            ),
            lineage=tuple(lineage),
            requirement_coverage=requirement_coverage,
            delivered_requirement_ids=tuple(
                item.requirement_id for item in requirement_coverage if item.delivered
            ),
            required_delivery_gaps=required_delivery_gaps,
            optional_delivery_gaps=optional_delivery_gaps,
            corroboration_coverage=self._metrics.corroboration(source_signals),
            unresolved_handles=unresolved,
        )

    def _successful_query_ids(self, run: dict[str, Any], queries: dict[str, dict[str, Any]]) -> set[str]:
        targets = {
            str(item.get("target")) for item in run.get("operations", [])
            if isinstance(item, dict) and item.get("kind") == "openWebQuery" and item.get("status") == "succeeded"
        }
        return {query_id for query_id, query in queries.items() if str(query.get("query")) in targets}

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

__all__ = ("SearchOpportunityCoverageReportBuilder",)
