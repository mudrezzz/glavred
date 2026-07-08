from datetime import UTC, datetime

from backend.app.domain.ai_run import AiRun, AiRunCapability, AiRunProvider, AiRunStatus
from backend.app.domain.draft_run import DraftRun, DraftRunStatus, DraftRunStep
from backend.app.domain.draft_run_steps import DraftRunStepKey, DraftRunStepStatus
from backend.app.drafting.application.reliability import DraftRunProviderReliabilityReporter
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from scripts.analyze_draft_run_reliability import DraftRunReliabilityCli


def test_retry_recovered_is_reliability_signal_not_failure() -> None:
    report = DraftRunProviderReliabilityReporter().build(
        [
            run_with_quality(
                "run-1",
                stage(
                    "llmValidation",
                    retry_path="retryRecovered",
                    result_impact="retryRecovered",
                    incidents=["malformedJson"],
                    attempts=2,
                ),
            ),
            run_with_quality("run-2", stage("llmValidation")),
            run_with_quality("run-3", stage("llmValidation")),
        ]
    )
    payload = report.to_payload()

    assert payload["summary"]["outcomeCounts"]["retryRecovered"] == 1
    assert payload["summary"]["incidentCounts"]["malformedJson"] == 1
    assert payload["summary"]["conclusionStatus"] == "cleanOrNormallyRecovered"
    assert payload["remediationItems"][0]["decision"] == "noActionExpected"


def test_backup_and_fallback_get_separate_remediation_decisions() -> None:
    report = DraftRunProviderReliabilityReporter().build(
        [
            run_with_quality("run-1", stage("draftCandidate", retry_path="backupRecovered", result_impact="backupRecovered")),
            run_with_quality("run-2", stage("evidenceInterpretation", retry_path="fallbackRecovered", result_impact="fallbackRecovered")),
            run_with_quality("run-3", stage("evidenceInterpretation", retry_path="fallbackRecovered", result_impact="fallbackRecovered")),
        ]
    )
    payload = report.to_payload()

    assert payload["summary"]["outcomeCounts"]["backupRecovered"] == 1
    assert payload["summary"]["outcomeCounts"]["fallbackRecovered"] == 2
    decisions = {item["operationId"]: item["decision"] for item in payload["remediationItems"]}
    slices = {item["operationId"]: item["recommendedSlice"] for item in payload["remediationItems"]}
    assert decisions["draftCandidate"] == "watchWithMoreRuns"
    assert decisions["evidenceInterpretation"] == "fixBacklogSlice"
    assert slices["evidenceInterpretation"] == "2.17.4.6.1.3.1"


def test_open_critical_requires_fix_before_trusting_quality() -> None:
    report = DraftRunProviderReliabilityReporter().build(
        [
            run_with_quality(
                "run-1",
                stage("editorialCritique"),
                issue_lifecycle={"openCriticalCount": 1, "openWarningCount": 0},
            ),
            run_with_quality("run-2", stage("editorialCritique")),
        ]
    )
    payload = report.to_payload()

    assert payload["summary"]["conclusionStatus"] == "requiresFixBeforeTrustingQuality"
    critical = next(item for item in payload["remediationItems"] if item["operationId"] == "qualityFidelity:openCritical")
    assert critical["decision"] == "fixBeforeTrustingQuality"
    assert critical["blockingLevel"] == "qualityGate"
    assert critical["recommendedSlice"] == "2.17.4.6.1.3.2"


def test_single_run_report_is_marked_as_insufficient_data() -> None:
    report = DraftRunProviderReliabilityReporter().build(
        [run_with_quality("run-1", stage("llmValidation", retry_path="retryRecovered", result_impact="retryRecovered"))]
    )

    assert report.to_payload()["summary"]["conclusionStatus"] == "insufficientData"
    assert "## Remediation ledger" in report.to_markdown()


def test_child_ai_run_error_is_counted_as_recovered_signal_when_run_succeeds() -> None:
    report = DraftRunProviderReliabilityReporter().build(
        [run_with_quality("run-1", stage("materialPlan"), ai_run_ids=["ai-run-1"])],
        ai_runs_by_draft_run_id={"run-1": [ai_run_record("ai-run-1", error="Malformed JSON response")]},
    )

    payload = report.to_payload()
    ai_event = next(item for item in payload["events"] if item["operationId"] == "aiRun:ai-run-1")
    assert ai_event["outcome"] == "retryRecovered"
    assert ai_event["incidentTypes"] == ["malformedJson"]
    assert payload["signalCoverage"]["summary"]["signalCounts"]["childAiRunError"] == 1


def test_cli_reads_draft_run_and_child_ai_runs_from_sqlite(tmp_path, capsys) -> None:
    draft_repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    ai_repository = SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3")
    ai_run = ai_run_record("ai-run-1", fallback_used=True)
    ai_repository.save(ai_run)
    draft_repository.save(run_with_quality("run-1", stage("llmValidation"), ai_run_ids=[ai_run.id]))

    exit_code = DraftRunReliabilityCli().run(
        [
            "--run-id",
            "run-1",
            "--format",
            "json",
            "--draft-run-db",
            str(tmp_path / "draft-runs.sqlite3"),
            "--ai-run-db",
            str(tmp_path / "ai-runs.sqlite3"),
        ]
    )

    assert exit_code == 0
    output = capsys.readouterr().out
    assert '"version": "draft-run-provider-reliability-v1"' in output
    assert '"conclusionStatus": "insufficientData"' in output


def test_report_audits_raw_structured_signal_coverage() -> None:
    run = run_with_quality(
        "run-1",
        stage(
            "evidenceInterpretation",
            retry_path="backupRecovered",
            result_impact="backupRecovered",
            incidents=["providerTimeout", "backupAccepted"],
            attempts=2,
        ),
        extra_artifact={
            "operationEnvelope": {
                "operationId": "evidenceInterpretation",
                "status": "backupAccepted",
                "incident": {"incidentType": "backupAccepted"},
                "attempts": [
                    {
                        "label": "primary",
                        "status": "timeout",
                        "incident": {"incidentType": "providerTimeout"},
                        "payloadStats": {"payloadBudget": {"profileId": "evidenceInterpretation:standard"}},
                    },
                    {"label": "backup", "status": "backupAccepted", "backup": True},
                ],
            },
            "payloadBudget": {"profileId": "evidenceInterpretation:standard", "overBudget": True},
            "runtimeBudget": {"exhausted": True, "stopReason": "budgetExhausted"},
            "fallbackUsed": True,
        },
    )

    payload = DraftRunProviderReliabilityReporter().build([run], ai_runs_by_draft_run_id={"run-1": [ai_run_record("ai-run-1", fallback_used=True)]}).to_payload()

    coverage = payload["signalCoverage"]
    assert coverage["summary"]["coveredSignals"] > 0
    assert coverage["summary"]["ignoredSignals"] > 0
    signal_counts = coverage["summary"]["signalCounts"]
    assert signal_counts["operationEnvelopeIncident"] == 1
    assert signal_counts["attemptIncident"] == 1
    assert signal_counts["retry"] >= 1
    assert signal_counts["backup"] >= 1
    assert signal_counts["fallback"] >= 1
    assert signal_counts["payloadBudgetIncident"] == 1
    assert signal_counts["runtimeBudgetIncident"] == 1
    assert signal_counts["childAiRun"] == 1
    assert any(item["reason"] == "budgetStatsOnly" for item in coverage["records"])


def run_with_quality(
    run_id: str,
    *stages: dict,
    issue_lifecycle: dict | None = None,
    ai_run_ids: list[str] | None = None,
    extra_artifact: dict | None = None,
) -> DraftRun:
    now = datetime.now(UTC)
    quality = {
        "version": "draft-run-quality-fidelity-v1",
        "technicalStatus": "succeeded",
        "providerRecoveryStatus": "clean",
        "editorialStatus": "publishable",
        "overallVerdict": "cleanSuccess",
        "stageSummaries": list(stages),
        "evidenceFidelity": {"coverageVerdict": "sufficient"},
        "issueLifecycle": issue_lifecycle or {"openCriticalCount": 0, "openWarningCount": 0},
    }
    return DraftRun(
        id=run_id,
        status=DraftRunStatus.SUCCEEDED,
        request_payload={"draftRunBudget": {"executionMode": "standard"}},
        input_summary={"title": "Draft"},
        final_draft={"title": "Draft", "body": "Body"},
        error=None,
        ai_run_ids=ai_run_ids or [],
        created_at=now,
        updated_at=now,
        steps=[
            DraftRunStep(
                id=f"{run_id}-validation",
                run_id=run_id,
                key=DraftRunStepKey.VALIDATION,
                status=DraftRunStepStatus.SUCCEEDED,
                title="Validation",
                artifact_payload={"rankingRevision": {"qualityFidelity": quality}, **(extra_artifact or {})},
                error=None,
                started_at=now,
                completed_at=now,
                sort_order=0,
            )
        ],
    )


def stage(
    operation_id: str,
    *,
    retry_path: str = "clean",
    result_impact: str = "none",
    incidents: list[str] | None = None,
    attempts: int = 1,
) -> dict:
    return {
        "operationId": operation_id,
        "stepKey": "validation",
        "attemptCount": attempts,
        "acceptedAttemptLabel": "accepted",
        "provider": "openrouter",
        "model": "openai/test-model",
        "modelRole": "review",
        "retryPath": retry_path,
        "incidentTypes": incidents or [],
        "resultImpact": result_impact,
    }


def ai_run_record(run_id: str, *, fallback_used: bool = False, error: str | None = None) -> AiRun:
    now = datetime.now(UTC)
    return AiRun(
        id=run_id,
        capability=AiRunCapability.DRAFT_GENERATION,
        status=AiRunStatus.SUCCEEDED,
        provider=AiRunProvider.OPENROUTER,
        model="openai/test-model",
        request_payload={"draftRunStep": "llmValidation"},
        result_payload={"ok": True},
        error=error,
        fallback_used=fallback_used,
        created_at=now,
        updated_at=now,
    )
