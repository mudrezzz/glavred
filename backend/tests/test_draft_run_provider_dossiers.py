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
    assert dossiers[0].runtime_migrated is True
    assert all(item.runtime_migrated is False for item in dossiers[1:])


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
    assert payload["runtimeMigrated"] is True


def test_planning_dossiers_have_operation_specific_required_inputs() -> None:
    factory = PlanningDossierFactory(ProviderDossierTestFixture.access())

    material = factory.build("materialPlan").to_payload()
    strategy = factory.build("strategy").to_payload()
    rhetorical = factory.build("rhetoricalPlans").to_payload()

    assert material["mustHave"] == ["postContract", "evidence"]
    assert strategy["mustHave"] == ["postContract", "materialPlan"]
    assert rhetorical["mustHave"] == ["postContract", "materialPlan", "draftStrategy"]
    assert strategy["sent"]["materialPlan"]["availableEvidence"] == ["claim-1", "claim-2"]
    assert rhetorical["sent"]["draftStrategy"]["thesisAngle"] == "Workflow before model"
    assert len(material["sent"]["rules"]) <= 8
    assert len(strategy["sent"]["evidence"]) <= 6
    assert len(rhetorical["sent"]["evidence"]) <= 2
    assert len(rhetorical["sent"]["rules"]) <= 4
    assert "sourceNotes" not in strategy["sent"]["materialPlan"]


def test_review_factory_keeps_critic_and_alternative_angle_roles_explicit() -> None:
    factory = ReviewDossierFactory(ProviderDossierTestFixture.access())

    assert factory.build(candidate_id="candidate-1", operation_id="editorialCritique").model_role == "critic"
    assert factory.build(candidate_id="candidate-1", operation_id="alternativeAngleRoute").model_role == "anotherAngle"
