"""Owner: upstream.application

Used by: signal utility scoring after provider payload validation.
Does not own: semantic provider evaluation, project projection, review status, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.domain.signal_utility import (
    ProjectEditorialSetting,
    SignalCriterionEffect,
    SignalRelationshipReport,
    SignalUtilityDimensionResult,
    SignalUtilityEvaluation,
    SignalUtilityRecommendation,
)
from backend.app.upstream.application.signal_type_semantics import SignalTypeSemanticsRegistry
from backend.app.upstream.application.signal_utility_criteria import SignalUtilityCriteriaPolicy


class SignalUtilityDecisionPolicy:
    def __init__(self) -> None:
        self._criteria = SignalUtilityCriteriaPolicy()
        self._semantics = SignalTypeSemanticsRegistry()

    def evaluate(
        self,
        *,
        signal: dict[str, Any],
        provider_dimensions: tuple[SignalUtilityDimensionResult, ...],
        settings: tuple[ProjectEditorialSetting, ...] = (),
        relationship_report: SignalRelationshipReport | None = None,
    ) -> SignalUtilityEvaluation:
        dimensions = tuple(provider_dimensions)
        radar_criteria, project_criteria, excluded = self._criteria.build(
            settings=settings,
            dimensions=dimensions,
        )
        quality_checks = self._semantics.quality_checks(signal)
        blocking = tuple(
            item.summary for item in (*radar_criteria, *project_criteria)
            if item.effect == SignalCriterionEffect.BLOCK
        )
        blocking += tuple(item.summary for item in quality_checks if item.effect == SignalCriterionEffect.BLOCK)
        warnings: list[str] = []
        if any(item.effect == SignalCriterionEffect.CAUTION for item in (*radar_criteria, *project_criteria)):
            warnings.append("partial-or-unproven-utility")
        warnings.extend(
            f"quality-check:{item.check_id}"
            for item in quality_checks
            if item.effect == SignalCriterionEffect.CAUTION
        )
        if blocking:
            recommendation = SignalUtilityRecommendation.NOT_RECOMMENDED
        elif warnings:
            recommendation = SignalUtilityRecommendation.REVIEW_WITH_CAUTION
        else:
            recommendation = SignalUtilityRecommendation.RECOMMENDED
        return SignalUtilityEvaluation(
            signal_id=str(signal.get("id") or ""),
            recommendation=recommendation,
            dimensions=dimensions,
            blocking_reasons=blocking,
            warnings=tuple(dict.fromkeys(warnings)),
            radar_criteria=radar_criteria,
            project_criteria=project_criteria,
            quality_checks=quality_checks,
            not_applicable_settings=excluded,
            relationship_report=relationship_report,
        )

    def inconclusive(
        self,
        signal_id: str,
        reason: str,
        *,
        relationship_report: SignalRelationshipReport | None = None,
    ) -> SignalUtilityEvaluation:
        return SignalUtilityEvaluation(
            signal_id=signal_id,
            recommendation=SignalUtilityRecommendation.INCONCLUSIVE,
            dimensions=(),
            warnings=(reason,),
            relationship_report=relationship_report,
        )

__all__ = ("SignalUtilityDecisionPolicy",)
