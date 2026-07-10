from dataclasses import replace

from backend.app.drafting.domain.provider_dossier import HandleResolutionStatus
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


def test_every_compact_reference_resolves_to_full_artifact() -> None:
    access = ProviderDossierTestFixture.access()
    handles = (
        access.post_contract().handles
        + access.evidence().handles
        + access.rules().handles
        + access.candidate_summaries().handles
        + access.validation_issues().handles
        + access.final_quality_lifecycle().handles
    )

    resolutions = [access.resolve(handle) for handle in handles]

    assert resolutions
    assert all(item.status == HandleResolutionStatus.RESOLVED for item in resolutions)
    assert all(item.value is not None for item in resolutions)
    assert all("value" not in item.to_trace_payload() for item in resolutions)


def test_handle_rejects_cross_run_stale_and_unknown_references() -> None:
    access = ProviderDossierTestFixture.access()
    handle = access.evidence().handles[0]

    cross_run = access.resolve(replace(handle, run_id="another-run"))
    stale = access.resolve(replace(handle, artifact_id="different-id"))
    missing = access.resolve(replace(handle, path=("missing", 0)))

    assert cross_run.status == HandleResolutionStatus.RUN_MISMATCH
    assert stale.status == HandleResolutionStatus.STALE
    assert missing.status == HandleResolutionStatus.NOT_FOUND
