from typing import Any

from backend.app.drafting.application.dossiers.provider_dossier_factories import (
    FinalQualityDossierFactory,
    PlanningDossierFactory,
    RankingDossierFactory,
    ReviewDossierFactory,
    RevisionDossierFactory,
    WriterDossierFactory,
)
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


def test_forbidden_full_artifacts_are_absent_from_actual_provider_input() -> None:
    access = ProviderDossierTestFixture.access()
    dossiers = (
        PlanningDossierFactory(access).build(),
        WriterDossierFactory(access).build(plan_id="plan-1"),
        ReviewDossierFactory(access).build(candidate_id="candidate-1"),
        RankingDossierFactory(access).build(),
        RevisionDossierFactory(access).build(candidate_id="candidate-1"),
        FinalQualityDossierFactory(access).build(candidate_id="candidate-1"),
    )

    for dossier in dossiers:
        provider_keys = _all_keys(dossier.provider_input())
        assert not set(dossier.semantic_contract.never_send_to_provider) & provider_keys
        assert set(dossier.semantic_contract.never_send_to_provider) <= set(dossier.suppressed_fields)


def test_ranking_receives_summaries_instead_of_full_candidate_pool() -> None:
    dossier = RankingDossierFactory(ProviderDossierTestFixture.access()).build()

    assert "candidates" in dossier.sent
    assert len(dossier.sent["candidates"]) == 2
    assert all("body" not in item for item in dossier.sent["candidates"])
    assert all(len(item["bodyExcerpt"]) <= 480 for item in dossier.sent["candidates"])


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {key for child in value.values() for key in _all_keys(child)}
    if isinstance(value, list):
        return {key for child in value for key in _all_keys(child)}
    return set()
