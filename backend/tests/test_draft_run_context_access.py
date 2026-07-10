from copy import deepcopy

from backend.app.drafting.application.context.draft_run_context_access import DraftRunContextAccessService
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


def test_context_access_is_deterministic_and_does_not_mutate_snapshot() -> None:
    snapshot = ProviderDossierTestFixture.snapshot()
    original = deepcopy(snapshot)
    first = DraftRunContextAccessService.from_snapshot(snapshot)
    second = DraftRunContextAccessService.from_snapshot(snapshot)

    assert first.post_contract().value == second.post_contract().value
    assert first.evidence().value == second.evidence().value
    assert [item.to_payload() for item in first.rules().handles] == [
        item.to_payload() for item in second.rules().handles
    ]
    assert snapshot == original


def test_context_access_compacts_evidence_and_reports_trimming() -> None:
    access = ProviderDossierTestFixture.access()

    evidence = access.evidence(limit=2)

    assert evidence.available is True
    assert evidence.total_count == 3
    assert evidence.selected_count == 2
    assert evidence.trimmed_count == 1
    assert all("provenance" not in item for item in evidence.value)
    assert all(item.get("id") != "claim-blocked" for item in evidence.value)


def test_context_access_returns_structured_missing_selection() -> None:
    access = DraftRunContextAccessService.from_snapshot({"runId": "empty", "steps": {}})

    assert access.post_contract().available is False
    assert access.selected_candidate("candidate-1").available is False
    assert access.final_quality_lifecycle().available is False
