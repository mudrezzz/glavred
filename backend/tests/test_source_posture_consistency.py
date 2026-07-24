from backend.app.upstream.application.source_posture import SourcePosturePolicy
from backend.app.upstream.application.source_credibility_consistency import (
    SourceCredibilityConsistencyPolicy,
)
from backend.app.upstream.domain.signal_utility import (
    SignalCriterionEffect,
    SignalCriterionOrigin,
    SignalQualityCheck,
    SignalUtilityCriterionResult,
    SignalUtilityStatus,
)


def test_first_party_source_and_single_source_support_are_independent_axes() -> None:
    assessment = SourcePosturePolicy().assess({
        "id": "signal-ifactory",
        "title": "iFactory reports maintenance results",
        "evidence": [{
            "sourceUrl": "https://ifactory.example/case",
            "sourceTitle": "iFactory deployment report",
            "quote": "iFactory reported lower downtime.",
        }],
    })

    payload = assessment.to_payload()
    assert payload["ownershipPosture"] == "firstParty"
    assert payload["claimSupport"] == "singleSource"
    assert payload["sourcePosture"] == "firstParty"


def test_two_domains_with_same_publisher_owner_do_not_create_false_corroboration() -> None:
    assessment = SourcePosturePolicy().assess({
        "id": "signal-vendor",
        "title": "Vendor result",
        "evidence": [
            {
                "sourceUrl": "https://vendor.example/case",
                "publisherOwner": "Vendor Group",
                "sourceTitle": "Vendor case",
                "quote": "Reported result.",
            },
            {
                "sourceUrl": "https://vendor-news.example/report",
                "publisherOwner": "Vendor Group",
                "sourceTitle": "Vendor news",
                "quote": "The same reported result.",
            },
        ],
    })

    assert assessment.claim_support.value == "singleSource"
    assert assessment.to_payload()["ownerKeys"] == ["vendorgroup"]


def test_two_independent_owner_keys_can_corroborate_one_claim() -> None:
    assessment = SourcePosturePolicy().assess({
        "id": "signal-corroborated",
        "title": "Industrial result",
        "evidence": [
            {
                "sourceUrl": "https://ieee.org/report",
                "publisherOwner": "IEEE",
                "sourceTitle": "IEEE report",
                "quote": "Observed result.",
            },
            {
                "sourceUrl": "https://reuters.com/report",
                "publisherOwner": "Reuters",
                "sourceTitle": "Reuters report",
                "quote": "The result was independently reported.",
            },
        ],
    })

    assert assessment.ownership.value == "independent"
    assert assessment.claim_support.value == "corroborated"
    assert assessment.effective_posture.value == "corroborated"


def test_provider_reason_code_cannot_promote_vendor_domain_to_independent() -> None:
    assessment = SourcePosturePolicy().assess({
        "id": "signal-vendor-claim",
        "title": "Vendor reports its own result",
        "source": "Vendor",
        "reasonCodes": ["source-independent"],
        "evidence": [{
            "sourceUrl": "https://vendor.example/case",
            "sourceTitle": "Vendor customer story",
            "quote": "Our solution delivered the reported result.",
        }],
    })

    assert assessment.ownership.value == "vendor"
    assert assessment.claim_support.value == "singleSource"


def test_first_party_quality_check_downgrades_conflicting_source_criterion() -> None:
    criterion = SignalUtilityCriterionResult(
        criterion_id="filter-source-credibility",
        origin=SignalCriterionOrigin.RADAR,
        dimension="sourceCredibility",
        title="Надежность источника",
        statement="Нужен независимый или подтвержденный источник.",
        mode="mustMatch",
        status=SignalUtilityStatus.MATCHED,
        verdict="СОВПАДАЕТ",
        effect=SignalCriterionEffect.PASS,
        summary="Provider назвал источник подходящим.",
    )
    source_check = SignalQualityCheck(
        check_id="source-posture",
        title="Позиция источника",
        status="partial",
        verdict="ТРЕБУЕТ ПРОВЕРКИ",
        effect=SignalCriterionEffect.CAUTION,
        summary="Источник описывает собственный результат.",
        classification="firstParty",
        details={
            "ownershipPosture": "firstParty",
            "claimSupport": "singleSource",
        },
    )

    reconciled = SourceCredibilityConsistencyPolicy().reconcile(
        criteria=(criterion,),
        quality_checks=(source_check,),
    )[0]

    assert reconciled.status == SignalUtilityStatus.PARTIAL
    assert reconciled.effect == SignalCriterionEffect.CAUTION
    assert reconciled.verdict == "ЧАСТИЧНО"
