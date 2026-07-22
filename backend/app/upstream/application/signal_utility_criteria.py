"""Owner: upstream.application

Used by: signal utility decision policy to produce explainable setting-backed criteria.
Does not own: provider calls, system quality checks, relationships, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from backend.app.upstream.domain.signal_utility import (
    ProjectEditorialSetting,
    SignalCriterionEffect,
    SignalCriterionOrigin,
    SignalUtilityCriterionResult,
    SignalUtilityDimensionResult,
    SignalUtilityStatus,
)


class SignalUtilityCriteriaPolicy:
    def build(
        self,
        *,
        settings: tuple[ProjectEditorialSetting, ...],
        dimensions: tuple[SignalUtilityDimensionResult, ...],
    ) -> tuple[
        tuple[SignalUtilityCriterionResult, ...],
        tuple[SignalUtilityCriterionResult, ...],
        tuple[dict[str, str], ...],
    ]:
        radar: list[SignalUtilityCriterionResult] = []
        project: list[SignalUtilityCriterionResult] = []
        excluded: list[dict[str, str]] = []
        for setting in settings:
            if not setting.dimension:
                excluded.append({
                    "settingId": setting.id,
                    "title": setting.title,
                    "reason": "notThisStage",
                })
                continue
            result = self._dimension_result(setting, dimensions)
            status = result.status if result else SignalUtilityStatus.NOT_PROVEN
            criterion = SignalUtilityCriterionResult(
                criterion_id=setting.id,
                origin=SignalCriterionOrigin.RADAR if setting.origin == "radar" else SignalCriterionOrigin.PROJECT,
                dimension=setting.dimension,
                title=setting.title,
                statement=setting.statement,
                mode=setting.mode,
                status=status,
                verdict=self._verdict(setting.mode, status),
                effect=self._effect(setting.mode, status),
                summary=result.summary if result else "Оценка по этой настройке не была доказана провайдером.",
                setting_refs=(setting.id,),
                evidence_refs=result.evidence_refs if result else (),
                uncertainty=result.uncertainty if result else "Требуется повторная оценка с разрешимой ссылкой на настройку.",
            )
            (radar if setting.origin == "radar" else project).append(criterion)
        return tuple(radar), tuple(project), tuple(excluded)

    def _dimension_result(
        self,
        setting: ProjectEditorialSetting,
        dimensions: tuple[SignalUtilityDimensionResult, ...],
    ) -> SignalUtilityDimensionResult | None:
        for item in dimensions:
            if item.dimension.value == setting.dimension and setting.id in item.setting_refs:
                return item
        return None

    def _effect(self, mode: str, status: SignalUtilityStatus) -> SignalCriterionEffect:
        if mode == "seekTension":
            return SignalCriterionEffect.DIAGNOSTIC
        if status == SignalUtilityStatus.MATCHED:
            return SignalCriterionEffect.PASS
        if status == SignalUtilityStatus.CONFLICT and mode in {"mustMatch", "mustNotMatch"}:
            return SignalCriterionEffect.BLOCK
        return SignalCriterionEffect.CAUTION

    def _verdict(self, mode: str, status: SignalUtilityStatus) -> str:
        labels = {
            "mustMatch": {
                SignalUtilityStatus.MATCHED: "СОВПАДАЕТ",
                SignalUtilityStatus.PARTIAL: "ЧАСТИЧНО",
                SignalUtilityStatus.NOT_PROVEN: "НЕ ДОКАЗАНО",
                SignalUtilityStatus.CONFLICT: "НЕ СООТВЕТСТВУЕТ",
            },
            "shouldMatch": {
                SignalUtilityStatus.MATCHED: "ПОДХОДИТ",
                SignalUtilityStatus.PARTIAL: "ЧАСТИЧНО",
                SignalUtilityStatus.NOT_PROVEN: "НЕ ПОДТВЕРЖДЕНО",
                SignalUtilityStatus.CONFLICT: "НЕ ПОДХОДИТ",
            },
            "mustNotMatch": {
                SignalUtilityStatus.MATCHED: "ЗАПРЕТ НЕ НАРУШЕН",
                SignalUtilityStatus.PARTIAL: "ТРЕБУЕТ ПРОВЕРКИ",
                SignalUtilityStatus.NOT_PROVEN: "ТРЕБУЕТ ПРОВЕРКИ",
                SignalUtilityStatus.CONFLICT: "НАРУШАЕТ ЗАПРЕТ",
            },
            "seekTension": {
                SignalUtilityStatus.MATCHED: "ЕСТЬ НАПРЯЖЕНИЕ",
                SignalUtilityStatus.PARTIAL: "НАПРЯЖЕНИЕ ВОЗМОЖНО",
                SignalUtilityStatus.NOT_PROVEN: "НАПРЯЖЕНИЕ НЕ ДОКАЗАНО",
                SignalUtilityStatus.CONFLICT: "НАПРЯЖЕНИЕ НЕ НАЙДЕНО",
            },
        }
        return labels.get(mode, labels["shouldMatch"])[status]


__all__ = ("SignalUtilityCriteriaPolicy",)
