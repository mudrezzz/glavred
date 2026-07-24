"""Owner: upstream.application

Used by: signal utility decision policy before final recommendation.
Does not own: source discovery, provider scoring, human review, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import replace

from backend.app.upstream.domain.signal_utility import (
    SignalCriterionEffect,
    SignalQualityCheck,
    SignalUtilityCriterionResult,
    SignalUtilityStatus,
)


class SourceCredibilityConsistencyPolicy:
    """Prevents provider criteria from contradicting canonical source posture."""

    _TRUSTED = {"independent", "corroborated"}

    def reconcile(
        self,
        *,
        criteria: tuple[SignalUtilityCriterionResult, ...],
        quality_checks: tuple[SignalQualityCheck, ...],
    ) -> tuple[SignalUtilityCriterionResult, ...]:
        source_check = next(
            (item for item in quality_checks if item.check_id == "source-posture"),
            None,
        )
        if source_check is None or source_check.classification in self._TRUSTED:
            return criteria
        ownership = str((source_check.details or {}).get("ownershipPosture") or source_check.classification)
        support = str((source_check.details or {}).get("claimSupport") or "notChecked")
        status = (
            SignalUtilityStatus.NOT_PROVEN
            if ownership == "unknown"
            else SignalUtilityStatus.PARTIAL
        )
        return tuple(
            self._reconcile_criterion(item, status, ownership, support)
            if item.dimension == "sourceCredibility"
            else item
            for item in criteria
        )

    def _reconcile_criterion(
        self,
        criterion: SignalUtilityCriterionResult,
        status: SignalUtilityStatus,
        ownership: str,
        support: str,
    ) -> SignalUtilityCriterionResult:
        if criterion.status == SignalUtilityStatus.CONFLICT:
            return criterion
        summary = {
            "firstParty": "Источник описывает собственный результат; независимое подтверждение не найдено.",
            "vendor": "Источник принадлежит поставщику решения; независимое подтверждение не найдено.",
            "unknown": "Происхождение источника не установлено, поэтому надежность не подтверждена.",
        }.get(ownership, "Надежность источника требует дополнительной проверки.")
        if support == "contradicted":
            summary = "Сохранено противоречащее доказательство; вывод требует редакторской проверки."
        return replace(
            criterion,
            status=status,
            verdict=self._verdict(criterion.mode, status),
            effect=SignalCriterionEffect.CAUTION,
            summary=summary,
            uncertainty="Оценка согласована с системной проверкой происхождения источника.",
        )

    def _verdict(self, mode: str, status: SignalUtilityStatus) -> str:
        if mode == "seekTension":
            return "НАПРЯЖЕНИЕ НЕ ДОКАЗАНО"
        if mode == "mustNotMatch":
            return "ТРЕБУЕТ ПРОВЕРКИ"
        if mode == "mustMatch":
            return "ЧАСТИЧНО" if status == SignalUtilityStatus.PARTIAL else "НЕ ДОКАЗАНО"
        return "ЧАСТИЧНО" if status == SignalUtilityStatus.PARTIAL else "НЕ ПОДТВЕРЖДЕНО"


__all__ = ("SourceCredibilityConsistencyPolicy",)
