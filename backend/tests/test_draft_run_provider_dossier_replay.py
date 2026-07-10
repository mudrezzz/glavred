from backend.app.drafting.application.dossiers.provider_dossier_replay import ProviderDossierReplayService
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


def test_sanitized_realistic_replay_proves_factory_foundation_only() -> None:
    report = ProviderDossierReplayService().run(ProviderDossierTestFixture.access())
    payload = report.to_payload()

    assert report.ready_for_migration is True
    assert payload["verdict"] == "readyForMigration"
    assert payload["runtimeMigrationStatus"] == "notMigrated"
    assert len(payload["dossiers"]) == 6
    assert payload["unresolvedHandleIds"] == []
    assert payload["forbiddenFieldViolations"] == []
    assert all(item["runtimeMigrated"] is False for item in payload["dossiers"])
    assert all(item["promptCharEstimate"] > 0 for item in payload["dossiers"])
    assert "Factory proof only" in payload["note"]


def test_replay_markdown_does_not_claim_live_runtime_migration() -> None:
    markdown = ProviderDossierReplayService().run(ProviderDossierTestFixture.access()).to_markdown()

    assert "runtime migration: `notMigrated`" in markdown
    assert "provider operation call sites are not migrated" in markdown
