from backend.app.drafting.application.dossiers.provider_dossier_factories import PlanningDossierFactory
from backend.app.drafting.application.operations.provider_input_budget_gate import ProviderInputBudgetGate
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


def test_dossier_passes_direct_current_call_budget_gate() -> None:
    dossier = PlanningDossierFactory(ProviderDossierTestFixture.access()).build()

    proof = ProviderInputBudgetGate().evaluate(
        operation_id="materialPlan",
        draft_run_step="materialPlan",
        provider_input=dossier.provider_input(),
        execution_mode="standard",
        model="test/model",
        model_role=dossier.model_role,
    )

    assert proof.operation_id == "materialPlan"
    assert proof.payload_budget["profileId"] == "materialPlan"
    assert proof.prompt_char_estimate > 0
    assert proof.approx_token_estimate > 0
    assert proof.request_payload_fields()["providerInput"]


def test_dossier_counts_match_actual_serialized_content() -> None:
    dossier = PlanningDossierFactory(ProviderDossierTestFixture.access()).build()

    assert dossier.sent_counts["postContract"] == 1
    assert dossier.sent_counts["evidence"] == len(dossier.sent["evidence"])
    assert dossier.sent_counts["rules"] == len(dossier.sent["rules"])
    assert dossier.trimmed_counts == {}


def test_oversized_dossier_input_produces_explicit_budget_incident() -> None:
    proof = ProviderInputBudgetGate().evaluate(
        operation_id="materialPlan",
        draft_run_step="materialPlan",
        provider_input={
            "dossierId": "planningDossier:oversized",
            "postContract": {"thesis": "x" * 200_000},
            "evidence": [{"id": str(index), "statement": "y" * 10_000} for index in range(50)],
        },
        execution_mode="standard",
        model="test/model",
        model_role="strategy",
    )

    assert proof.payload_budget["qualityRisk"] == "high"
    assert proof.payload_budget["incident"]["incidentType"] == "payloadTooLarge"
    assert proof.budgeted_input.incident["needsFollowUp"] is True
