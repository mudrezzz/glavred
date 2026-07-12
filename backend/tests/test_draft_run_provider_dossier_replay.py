from backend.app.drafting.application.dossiers.provider_dossier_replay import ProviderDossierReplayService
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


def test_sanitized_realistic_replay_reports_all_runtime_migrations() -> None:
    report = ProviderDossierReplayService().run(ProviderDossierTestFixture.access())
    payload = report.to_payload()

    assert report.ready_for_migration is True
    assert payload["verdict"] == "readyForMigration"
    assert payload["runtimeMigrationStatus"] == "migrated"
    assert len(payload["dossiers"]) == 10
    assert payload["unresolvedHandleIds"] == []
    assert payload["forbiddenFieldViolations"] == []
    assert [item["operationId"] for item in payload["dossiers"][:3]] == [
        "materialPlan",
        "strategy",
        "rhetoricalPlans",
    ]
    migrated = {item["operationId"] for item in payload["dossiers"] if item["runtimeMigrated"]}
    assert migrated == {
        "materialPlan",
        "strategy",
        "rhetoricalPlans",
        "draftCandidate",
        "alternativeAngleRoute",
        "alternativeAngleCandidate",
        "llmValidation",
        "pairwiseRanking",
        "directedRevision",
        "finalQualityGateReview",
    }
    assert all(item["promptCharEstimate"] > 0 for item in payload["dossiers"])
    assert "All planned dossier families are runtime-migrated" in payload["note"]


def test_replay_markdown_reports_complete_runtime_migration() -> None:
    markdown = ProviderDossierReplayService().run(ProviderDossierTestFixture.access()).to_markdown()

    assert "runtime migration: `migrated`" in markdown
    assert "All planned dossier families are runtime-migrated" in markdown
