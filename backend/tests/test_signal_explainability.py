from __future__ import annotations

import pytest

from backend.app.upstream.application.signal_relationships import SignalRelationshipPolicy
from backend.app.upstream.application.signal_type_semantics import SignalTypeSemanticsRegistry
from backend.app.upstream.application.signal_utility_criteria import SignalUtilityCriteriaPolicy
from backend.app.upstream.application.signal_utility_decision import SignalUtilityDecisionPolicy
from backend.app.upstream.domain.signal_utility import (
    ProjectEditorialSetting,
    SignalRelationshipKind,
    SignalUtilityDimension,
    SignalUtilityDimensionResult,
    SignalUtilityImportance,
    SignalUtilityStatus,
)


@pytest.mark.parametrize(
    ("signal_type", "mechanism_applicable", "outcome_applicable"),
    (
        ("eventFact", False, True),
        ("change", True, True),
        ("audienceQuestion", False, False),
        ("tensionCounterargument", False, False),
        ("case", True, True),
        ("dataPoint", False, False),
        ("practice", True, True),
        ("problemFailureMode", True, True),
        ("personalObservation", False, False),
        ("recurringPattern", True, False),
    ),
)
def test_type_semantics_cover_all_signal_types(
    signal_type: str,
    mechanism_applicable: bool,
    outcome_applicable: bool,
) -> None:
    checks = by_check(SignalTypeSemanticsRegistry().quality_checks(signal(signal_type=signal_type)))

    assert checks["mechanism-support"].applicable is mechanism_applicable
    assert checks["outcome-support"].applicable is outcome_applicable


def test_type_semantics_do_not_require_mechanism_or_outcome_for_audience_question() -> None:
    checks = by_check(SignalTypeSemanticsRegistry().quality_checks(signal(signal_type="audienceQuestion")))

    assert checks["mechanism-support"].applicable is False
    assert checks["outcome-support"].applicable is False
    assert checks["outcome-support"].classification == "notApplicable"


def test_digital_advisor_capability_is_not_misrepresented_as_observed_result() -> None:
    source = signal(
        title="Цифровой советчик как модуль поддержки решений в ТОиР",
        outcome="Система формирует рекомендации и поддерживает решение инженера.",
    )

    checks = by_check(SignalTypeSemanticsRegistry().quality_checks(source))

    assert checks["mechanism-support"].classification == "reported"
    assert checks["outcome-support"].classification == "capabilityOnly"
    assert checks["outcome-support"].verdict == "ОПИСАНА ФУНКЦИЯ"


@pytest.mark.parametrize(
    ("outcome", "reason_codes", "expected"),
    (
        ("Время простоя сократилось на 18 часов.", ("outcome-observed",), "observed"),
        ("Поставщик сообщил о сокращении простоя на 18 часов.", (), "reported"),
        ("Система формирует рекомендации для инженера.", (), "capabilityOnly"),
        ("Система может сократить время диагностики.", (), "expected"),
        ("", (), "missing"),
    ),
)
def test_result_support_contract(
    outcome: str,
    reason_codes: tuple[str, ...],
    expected: str,
) -> None:
    source = signal(outcome=outcome)
    source["reasonCodes"] = list(reason_codes)

    check = by_check(SignalTypeSemanticsRegistry().quality_checks(source))["outcome-support"]

    assert check.classification == expected


def test_nonempty_fields_without_resolvable_evidence_are_not_proof() -> None:
    source = signal()
    source["evidenceRefs"] = []

    checks = by_check(SignalTypeSemanticsRegistry().quality_checks(source))

    assert checks["evidence-grounding"].effect.value == "block"
    assert checks["mechanism-support"].verdict == "НЕ ДОКАЗАНО"


def test_criterion_modes_have_distinct_verdicts_and_only_proven_blocker_blocks() -> None:
    settings = (
        setting("must", "mustMatch"),
        setting("prefer", "shouldMatch"),
        setting("ban", "mustNotMatch"),
        setting("tension", "seekTension"),
    )
    dimensions = tuple(
        dimension(item.id, SignalUtilityStatus.CONFLICT if item.id == "ban" else SignalUtilityStatus.NOT_PROVEN)
        for item in settings
    )

    radar, _, _ = SignalUtilityCriteriaPolicy().build(settings=settings, dimensions=dimensions)
    by_id = {item.criterion_id: item for item in radar}

    assert by_id["must"].verdict == "НЕ ДОКАЗАНО"
    assert by_id["must"].effect.value == "caution"
    assert by_id["prefer"].verdict == "НЕ ПОДТВЕРЖДЕНО"
    assert by_id["ban"].verdict == "НАРУШАЕТ ЗАПРЕТ"
    assert by_id["ban"].effect.value == "block"
    assert by_id["tension"].verdict == "НАПРЯЖЕНИЕ НЕ ДОКАЗАНО"
    assert by_id["tension"].effect.value == "diagnostic"


def test_relationship_policy_groups_same_claim_but_keeps_other_same_source_claim() -> None:
    first = signal(signal_id="advisor-1", title="Цифровой советчик как модуль поддержки решений в ТОиР")
    alias = signal(signal_id="advisor-2", title="Цифровой советчик как модуль поддержки решений ТОиР")
    risk = signal(signal_id="risk-1", title="Автоматизированная оценка рисков в ТОиР")

    reports = SignalRelationshipPolicy().reports([first, alias, risk])
    first_relations = {item.other_signal_id: item.kind for item in reports["advisor-1"].relations}

    assert first_relations["advisor-2"] == SignalRelationshipKind.SAME_CLAIM
    assert first_relations["risk-1"] == SignalRelationshipKind.RELATED_SAME_SOURCE
    assert reports["advisor-1"].canonical_signal_id == reports["advisor-2"].canonical_signal_id
    assert reports["risk-1"].canonical_signal_id == "risk-1"


def test_same_claim_from_another_material_is_corroboration_not_duplicate() -> None:
    first = signal(signal_id="source-a", title="Цифровой советчик для ТОиР", material_id="material-a")
    second = signal(signal_id="source-b", title="Цифровой советчик для ТОиР", material_id="material-b")

    reports = SignalRelationshipPolicy().reports([first, second])

    relation = reports["source-a"].relations[0]
    assert relation.kind == SignalRelationshipKind.CORROBORATES
    assert reports["source-a"].canonical_signal_id == "source-a"
    assert reports["source-b"].canonical_signal_id == "source-b"


def test_exact_duplicate_uses_one_canonical_signal_without_deleting_provenance() -> None:
    first = signal(signal_id="duplicate-a", title="Цифровой советчик для ТОиР")
    second = signal(signal_id="duplicate-b", title="Цифровой советчик для ТОиР")
    second["evidenceRefs"].append({
        "materialId": "material-1",
        "fragmentId": "material-1-fragment-2",
        "quote": "Второе доказательство того же тезиса.",
    })

    reports = SignalRelationshipPolicy().reports([first, second])

    assert reports["duplicate-a"].relations[0].kind == SignalRelationshipKind.EXACT_DUPLICATE
    assert reports["duplicate-a"].canonical_signal_id == "duplicate-b"
    assert len(reports["duplicate-a"].relations[0].evidence_refs) == 2


def test_structured_contradiction_is_not_treated_as_duplicate() -> None:
    first = signal(signal_id="claim-a", material_id="material-a")
    second = signal(signal_id="claim-b", title="Ручная проверка остается обязательной", material_id="material-b")
    second["reasonCodes"] = ["contradiction"]

    reports = SignalRelationshipPolicy().reports([first, second])

    assert reports["claim-a"].relations[0].kind == SignalRelationshipKind.CONTRADICTS


def test_ambiguous_pair_stays_inconclusive_when_provider_does_not_classify_it() -> None:
    first = signal(signal_id="advisor-a", title="Цифровой советчик для ремонта", material_id="material-a")
    second = signal(signal_id="advisor-b", title="Цифровые советы для обслуживания", material_id="material-b")

    reports = SignalRelationshipPolicy().reports([first, second])

    assert reports["advisor-a"].relations[0].kind == SignalRelationshipKind.INCONCLUSIVE


def test_unrelated_pair_is_not_claimed_as_proven_distinct_without_relationship_proof() -> None:
    first = signal(signal_id="advisor", title="Цифровой советчик для ТОиР", material_id="material-a")
    second = signal(signal_id="weather", title="Прогноз погоды для агронома", material_id="material-b")

    reports = SignalRelationshipPolicy().reports([first, second])

    assert reports["advisor"].status == "notChecked"
    assert reports["advisor"].relations == ()


def test_provider_can_prove_distinct_for_a_bounded_candidate_pair() -> None:
    first = signal(signal_id="advisor-a", title="Цифровой советчик для ремонта", material_id="material-a")
    second = signal(signal_id="advisor-b", title="Цифровые советы для обслуживания", material_id="material-b")
    pair_id = "advisor-a|advisor-b"

    reports = SignalRelationshipPolicy().reports(
        [first, second],
        {pair_id: {"kind": "distinct", "summary": "Тезисы используют разные механизмы и результаты."}},
    )

    assert reports["advisor-a"].relations[0].kind == SignalRelationshipKind.DISTINCT


def test_digital_advisor_replay_is_topic_match_with_capability_only_caution() -> None:
    source = signal(
        signal_id="digital-advisor",
        title="Цифровой советчик как модуль поддержки решений в ТОиР",
        outcome="Система формирует рекомендации и поддерживает решение инженера.",
    )
    radar_setting = setting("industrial-topic", "mustMatch")
    topic_match = dimension("industrial-topic", SignalUtilityStatus.MATCHED)

    evaluation = SignalUtilityDecisionPolicy().evaluate(
        signal=source,
        provider_dimensions=(topic_match,),
        settings=(radar_setting,),
    )
    checks = {item.check_id: item for item in evaluation.quality_checks}

    assert evaluation.radar_criteria[0].verdict == "СОВПАДАЕТ"
    assert checks["mechanism-support"].evidence_refs
    assert checks["outcome-support"].classification == "capabilityOnly"
    assert checks["source-posture"].classification == "unknown"
    assert evaluation.recommendation.value == "reviewWithCaution"


def by_check(checks):
    return {item.check_id: item for item in checks}


def signal(
    *,
    signal_id: str = "signal-1",
    signal_type: str = "case",
    title: str = "Цифровой советчик для ТОиР",
    outcome: str = "Система формирует рекомендации для инженера.",
    material_id: str = "material-1",
) -> dict:
    fragment_id = f"{material_id}-fragment-1"
    return {
        "id": signal_id,
        "type": signal_type,
        "title": title,
        "summary": "Источник описывает поддержку решений в промышленном обслуживании.",
        "mechanism": "Система сопоставляет телеметрию с журналом обслуживания.",
        "outcome": outcome,
        "capturedAt": "2026-07-20T12:00:00+00:00",
        "evidenceRefs": [{
            "materialId": material_id,
            "fragmentId": fragment_id,
            "quote": "Система формирует рекомендации для инженера по обслуживанию.",
        }],
        "evidence": [{
            "materialId": material_id,
            "fragmentId": fragment_id,
            "sourceUrl": f"https://example.test/{material_id}",
        }],
    }


def setting(setting_id: str, mode: str) -> ProjectEditorialSetting:
    return ProjectEditorialSetting(
        id=setting_id,
        kind="radarFilter:topicAffinity",
        title=f"Критерий {setting_id}",
        statement="Формальная настройка радара.",
        mode=mode,
        dimension="topicAffinity",
        origin="radar",
    )


def dimension(setting_id: str, status: SignalUtilityStatus) -> SignalUtilityDimensionResult:
    return SignalUtilityDimensionResult(
        dimension=SignalUtilityDimension.TOPIC_AFFINITY,
        status=status,
        importance=SignalUtilityImportance.BLOCKING,
        summary=f"Результат для {setting_id}.",
        reason_codes=("recorded-proof",),
        setting_refs=(setting_id,),
        evidence_refs=({"materialId": "material-1", "fragmentId": "fragment-1"},),
    )
