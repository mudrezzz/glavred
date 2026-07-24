"""Owner: upstream.application

Used by: signal utility decision policy and report diagnostics.
Does not own: provider scoring, project criteria, persistence, or UI rendering.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.app.upstream.domain.signal_utility import (
    SignalCriterionEffect,
    SignalQualityCheck,
    SignalResultSupport,
    SignalSourcePosture,
)
from backend.app.upstream.application.source_posture import SourcePosturePolicy
from backend.app.upstream.domain.source_posture import SourcePostureAssessment


class SignalTypeSemanticsRegistry:
    """Defines which explanatory checks make sense for each signal taxonomy type."""

    MECHANISM_TYPES = frozenset({"case", "practice", "change", "problemFailureMode", "recurringPattern"})
    OUTCOME_TYPES = frozenset({"case", "practice", "change", "problemFailureMode", "eventFact"})
    FRESHNESS_TYPES = frozenset({"eventFact", "change", "dataPoint"})

    def __init__(self, source_posture: SourcePosturePolicy | None = None) -> None:
        self._source_posture_policy = source_posture or SourcePosturePolicy()

    def quality_checks(self, signal: dict[str, Any]) -> tuple[SignalQualityCheck, ...]:
        evidence_refs = self._evidence_refs(signal)
        signal_type = str(signal.get("type") or "")
        result_support = self._result_support(signal, signal_type)
        source_posture = self._source_posture_policy.assess(signal)
        return (
            self._grounding(evidence_refs),
            self._mechanism(signal, signal_type, evidence_refs),
            self._outcome(signal, signal_type, result_support, evidence_refs),
            self._source(source_posture, evidence_refs),
            self._freshness(signal, signal_type),
        )

    def _grounding(self, refs: tuple[dict[str, str], ...]) -> SignalQualityCheck:
        resolved = bool(refs)
        return SignalQualityCheck(
            check_id="evidence-grounding",
            title="Связь с источником",
            status="matched" if resolved else "notProven",
            verdict="ДОКАЗАТЕЛЬСТВО НАЙДЕНО" if resolved else "НЕ ДОКАЗАНО",
            effect=SignalCriterionEffect.PASS if resolved else SignalCriterionEffect.BLOCK,
            summary=(
                "Утверждение связано с конкретной цитатой источника."
                if resolved else "Утверждение не связано с разрешимым фрагментом источника."
            ),
            evidence_refs=refs,
        )

    def _mechanism(
        self,
        signal: dict[str, Any],
        signal_type: str,
        refs: tuple[dict[str, str], ...],
    ) -> SignalQualityCheck:
        applicable = signal_type in self.MECHANISM_TYPES
        present = bool(" ".join(str(signal.get("mechanism") or "").split()))
        return SignalQualityCheck(
            check_id="mechanism-support",
            title="Как это работает",
            status="reported" if applicable and present and refs else "missing" if applicable else "notApplicable",
            verdict="ОПИСАНО В ИСТОЧНИКЕ" if applicable and present and refs else "НЕ ДОКАЗАНО" if applicable else "НЕ ПРИМЕНИМО",
            effect=SignalCriterionEffect.PASS if applicable and present and refs else SignalCriterionEffect.CAUTION if applicable else SignalCriterionEffect.DIAGNOSTIC,
            summary=(
                "Источник описывает механизм; это не является независимой проверкой его эффективности."
                if applicable and present and refs else
                "Для этого типа сигнала механизм не подтвержден сохраненным доказательством."
                if applicable else "Для этого типа сигнала механизм не является обязательным полем."
            ),
            classification="reported" if applicable and present and refs else "missing" if applicable else "notApplicable",
            applicable=applicable,
            evidence_refs=refs if applicable and present else (),
        )

    def _outcome(
        self,
        signal: dict[str, Any],
        signal_type: str,
        support: SignalResultSupport,
        refs: tuple[dict[str, str], ...],
    ) -> SignalQualityCheck:
        applicable = signal_type in self.OUTCOME_TYPES
        labels = {
            SignalResultSupport.OBSERVED: ("НАБЛЮДАЕМЫЙ РЕЗУЛЬТАТ", SignalCriterionEffect.PASS),
            SignalResultSupport.REPORTED: ("ЗАЯВЛЕННЫЙ РЕЗУЛЬТАТ", SignalCriterionEffect.CAUTION),
            SignalResultSupport.CAPABILITY_ONLY: ("ОПИСАНА ФУНКЦИЯ", SignalCriterionEffect.CAUTION),
            SignalResultSupport.EXPECTED: ("ОЖИДАЕМЫЙ ЭФФЕКТ", SignalCriterionEffect.CAUTION),
            SignalResultSupport.MISSING: ("НЕ ДОКАЗАНО", SignalCriterionEffect.CAUTION),
            SignalResultSupport.NOT_APPLICABLE: ("НЕ ПРИМЕНИМО", SignalCriterionEffect.DIAGNOSTIC),
        }
        verdict, effect = labels[support]
        summaries = {
            SignalResultSupport.OBSERVED: "Источник содержит конкретный наблюдаемый результат, связанный с доказательством.",
            SignalResultSupport.REPORTED: "Результат заявлен источником, но не подтвержден независимым материалом.",
            SignalResultSupport.CAPABILITY_ONLY: "Описана возможность системы, а не измеренный результат внедрения.",
            SignalResultSupport.EXPECTED: "Источник описывает ожидаемый эффект, а не состоявшийся результат.",
            SignalResultSupport.MISSING: "Сохраненные доказательства не устанавливают результат.",
            SignalResultSupport.NOT_APPLICABLE: "Для этого типа сигнала результат не является обязательным полем.",
        }
        return SignalQualityCheck(
            check_id="outcome-support",
            title="Что получилось",
            status=support.value,
            verdict=verdict,
            effect=effect,
            summary=summaries[support],
            classification=support.value,
            applicable=applicable,
            evidence_refs=refs if applicable and support != SignalResultSupport.MISSING else (),
        )

    def _source(
        self,
        assessment: SourcePostureAssessment,
        refs: tuple[dict[str, str], ...],
    ) -> SignalQualityCheck:
        posture = assessment.effective_posture
        pass_postures = {SignalSourcePosture.INDEPENDENT, SignalSourcePosture.CORROBORATED}
        summaries = {
            SignalSourcePosture.INDEPENDENT: "Источник классифицирован как независимый от описываемого решения.",
            SignalSourcePosture.CORROBORATED: "Тезис подтверждается материалами с нескольких доменов.",
            SignalSourcePosture.FIRST_PARTY: "Источник описывает собственный продукт или собственный результат.",
            SignalSourcePosture.VENDOR: "Материал опубликован заинтересованным поставщиком решения.",
            SignalSourcePosture.UNKNOWN: "Независимость источника не установлена; отсутствие vendor-маркера не считается доказательством.",
        }
        return SignalQualityCheck(
            check_id="source-posture",
            title="Позиция источника",
            status="matched" if posture in pass_postures else "partial",
            verdict="НЕЗАВИСИМЫЙ" if posture == SignalSourcePosture.INDEPENDENT else "ПОДТВЕРЖДЕНО НЕСКОЛЬКИМИ" if posture == SignalSourcePosture.CORROBORATED else "ТРЕБУЕТ ПРОВЕРКИ",
            effect=SignalCriterionEffect.PASS if posture in pass_postures else SignalCriterionEffect.CAUTION,
            summary=summaries[posture],
            classification=posture.value,
            evidence_refs=refs,
            details=assessment.to_payload(),
        )

    def _freshness(self, signal: dict[str, Any], signal_type: str) -> SignalQualityCheck:
        applicable = signal_type in self.FRESHNESS_TYPES
        captured = self._date(str(signal.get("capturedAt") or ""))
        current = bool(captured and (datetime.now(UTC) - captured).days <= 730)
        return SignalQualityCheck(
            check_id="freshness",
            title="Актуальность",
            status="matched" if applicable and current else "notProven" if applicable else "notApplicable",
            verdict="АКТУАЛЬНО" if applicable and current else "ТРЕБУЕТ ПРОВЕРКИ" if applicable else "НЕ ПРИМЕНИМО",
            effect=SignalCriterionEffect.PASS if applicable and current else SignalCriterionEffect.CAUTION if applicable else SignalCriterionEffect.DIAGNOSTIC,
            summary="Дата сигнала находится в двухлетнем окне." if applicable and current else "Актуальность требует отдельной проверки." if applicable else "Свежесть не влияет на этот тип сигнала автоматически.",
            applicable=applicable,
        )

    def _result_support(self, signal: dict[str, Any], signal_type: str) -> SignalResultSupport:
        if signal_type not in self.OUTCOME_TYPES:
            return SignalResultSupport.NOT_APPLICABLE
        outcome = " ".join(str(signal.get("outcome") or "").split())
        if not outcome:
            return SignalResultSupport.MISSING
        reason_codes = {str(item) for item in signal.get("reasonCodes") or []}
        if "outcome-observed" in reason_codes:
            return SignalResultSupport.OBSERVED
        text = f"{outcome} {' '.join(str(item.get('quote') or '') for item in signal.get('evidenceRefs') or [] if isinstance(item, dict))}".casefold()
        if any(token in text for token in ("ожида", "может ", "позволит", "expected", "may ")):
            return SignalResultSupport.EXPECTED
        if any(token in text for token in ("рекомендац", "поддержк", "диагност", "выдает", "формирует", "enabling", "supports")) and not any(char.isdigit() for char in text):
            return SignalResultSupport.CAPABILITY_ONLY
        return SignalResultSupport.REPORTED

    def _evidence_refs(self, signal: dict[str, Any]) -> tuple[dict[str, str], ...]:
        return tuple(
            {"materialId": str(item.get("materialId") or ""), "fragmentId": str(item.get("fragmentId") or "")}
            for item in signal.get("evidenceRefs") or []
            if isinstance(item, dict) and item.get("materialId") and item.get("fragmentId")
        )

    def _date(self, value: str) -> datetime | None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            return None


__all__ = ("SignalTypeSemanticsRegistry",)
