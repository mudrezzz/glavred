from backend.app.drafting.application.dossiers.provider_dossier_factories import (
    FinalQualityDossierFactory,
    PlanningDossierFactory,
    RankingDossierFactory,
    ReviewDossierFactory,
    RevisionDossierFactory,
    WriterDossierFactory,
)
from backend.app.drafting.domain.provider_dossier import (
    DossierQualityRisk,
    DossierReadinessStatus,
    ProviderDossier,
)
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


def test_all_operation_families_return_ready_typed_dossiers() -> None:
    access = ProviderDossierTestFixture.access()
    dossiers = (
        PlanningDossierFactory(access).build(),
        WriterDossierFactory(access).build(plan_id="plan-1"),
        ReviewDossierFactory(access).build(candidate_id="candidate-1"),
        RankingDossierFactory(access).build(),
        RevisionDossierFactory(access).build(candidate_id="candidate-1"),
        FinalQualityDossierFactory(access).build(candidate_id="candidate-1"),
    )

    assert all(isinstance(item, ProviderDossier) for item in dossiers)
    assert all(item.readiness_status == DossierReadinessStatus.READY for item in dossiers)
    assert all(item.quality_risk == DossierQualityRisk.NONE for item in dossiers)
    assert {item.model_role for item in dossiers} == {"strategy", "writer", "review", "finalGate"}
    assert all(item.runtime_migrated is False for item in dossiers)


def test_missing_required_input_blocks_dossier() -> None:
    dossier = WriterDossierFactory(ProviderDossierTestFixture.access()).build(plan_id="missing-plan")

    assert dossier.readiness_status == DossierReadinessStatus.BLOCKED
    assert dossier.quality_risk == DossierQualityRisk.HIGH
    assert dossier.missing_required_inputs == ("rhetoricalPlan",)
    assert "rhetoricalPlan" not in dossier.sent


def test_trace_payload_exposes_semantic_contract_and_counts() -> None:
    payload = PlanningDossierFactory(ProviderDossierTestFixture.access()).build().to_payload()

    assert payload["profileId"] == "planningDossier:materialPlan"
    assert payload["mustHave"] == ["postContract", "evidence"]
    assert payload["readinessStatus"] == "ready"
    assert payload["sentCounts"]["evidence"] == len(payload["sent"]["evidence"])
    assert payload["runtimeMigrated"] is False


def test_review_factory_keeps_critic_and_alternative_angle_roles_explicit() -> None:
    factory = ReviewDossierFactory(ProviderDossierTestFixture.access())

    assert factory.build(candidate_id="candidate-1", operation_id="editorialCritique").model_role == "critic"
    assert factory.build(candidate_id="candidate-1", operation_id="alternativeAngleRoute").model_role == "anotherAngle"
