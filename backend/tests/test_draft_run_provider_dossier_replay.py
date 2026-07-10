from backend.app.drafting.application.dossiers.provider_dossier_replay import ProviderDossierReplayService
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


def test_sanitized_realistic_replay_reports_planning_migration_only() -> None:
    report = ProviderDossierReplayService().run(ProviderDossierTestFixture.access())
    payload = report.to_payload()

    assert report.ready_for_migration is True
    assert payload["verdict"] == "readyForMigration"
    assert payload["runtimeMigrationStatus"] == "partiallyMigrated"
    assert len(payload["dossiers"]) == 8
    assert payload["unresolvedHandleIds"] == []
    assert payload["forbiddenFieldViolations"] == []
    assert [item["operationId"] for item in payload["dossiers"][:3]] == [
        "materialPlan",
        "strategy",
        "rhetoricalPlans",
    ]
    assert all(item["runtimeMigrated"] is True for item in payload["dossiers"][:3])
    assert all(item["runtimeMigrated"] is False for item in payload["dossiers"][3:])
    assert all(item["promptCharEstimate"] > 0 for item in payload["dossiers"])
    assert "Planning call sites are migrated" in payload["note"]


def test_replay_markdown_reports_partial_runtime_migration() -> None:
    markdown = ProviderDossierReplayService().run(ProviderDossierTestFixture.access()).to_markdown()

    assert "runtime migration: `partiallyMigrated`" in markdown
    assert "Planning call sites are migrated" in markdown
