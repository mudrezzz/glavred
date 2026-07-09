from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_from_payload
from backend.app.drafting.application.artifacts.draft_run_payloads import request_to_payload
from backend.app.drafting.application.generation.deterministic_draft_service import DeterministicDraftService
from backend.app.drafting.application.quality import DraftRunQualityFidelityReporter
from backend.app.domain.draft_run import create_queued_draft_run
from backend.app.drafting.application.workflow.legacy_pipeline import DraftRunPipeline
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_run_context_builder import make_context
from backend.tests.test_draft_run_pipeline import make_request


def test_retry_recovered_is_not_degraded() -> None:
    report = reporter().build(
        run_status="succeeded",
        steps=[
            step(
                "validation",
                {
                    "rankingRevision": {
                        "finalQualityGate": {"status": "passed"},
                        "providerOperation": {
                            "operationEnvelope": {
                                "operationId": "llmValidation",
                                "status": "accepted",
                                "attempts": [
                                    {"label": "primary", "status": "error", "model": "review-model", "error": "JSONDecodeError"},
                                    {"label": "primary-repair", "status": "accepted", "model": "review-model"},
                                ],
                            }
                        },
                    }
                },
            ),
            step("complete", {"status": "succeeded"}),
        ],
        final_draft=final_draft(),
    )

    assert report["providerRecoveryStatus"] == "retryRecovered"
    assert report["editorialStatus"] == "publishable"
    assert report["overallVerdict"] == "recoveredSuccess"


def test_backup_and_fallback_are_separate_recovery_levels() -> None:
    backup = reporter().build(
        run_status="succeeded",
        steps=[step("validation", {"rankingRevision": {"finalQualityGate": {"status": "passed"}, "op": envelope("accepted", backup=True)}}), step("complete", {})],
        final_draft=final_draft(),
    )
    fallback = reporter().build(
        run_status="succeeded",
        steps=[step("rulePack", {"evidenceInterpretation": {}, "op": envelope("fallback")}), step("validation", {"rankingRevision": {"finalQualityGate": {"status": "passed"}}}), step("complete", {})],
        final_draft=final_draft(),
    )

    assert backup["providerRecoveryStatus"] == "backupRecovered"
    assert backup["overallVerdict"] == "recoveredSuccess"
    assert fallback["providerRecoveryStatus"] == "fallbackRecovered"
    assert fallback["overallVerdict"] == "degradedSuccess"


def test_open_critical_requires_attention_but_suppressed_warning_allows_caution() -> None:
    critical = reporter().build(
        run_status="succeeded",
        steps=[
            step(
                "validation",
                {
                    "candidateReports": [
                        {"findings": [{"validatorId": "source.truth", "severity": "critical", "message": "Unsupported claim"}]}
                    ],
                    "rankingRevision": {"finalQualityGate": {"status": "passed"}},
                },
            ),
            step("complete", {}),
        ],
        final_draft=final_draft(),
    )
    warning = reporter().build(
        run_status="succeeded",
        steps=[
            step(
                "validation",
                {
                    "candidateReports": [
                        {"findings": [{"validatorId": "evidence.attribution", "severity": "warning", "suppressedReason": "diagnostic"}]}
                    ],
                    "rankingRevision": {"finalQualityGate": {"status": "warning"}},
                },
            ),
            step("complete", {}),
        ],
        final_draft=final_draft(),
    )

    assert critical["editorialStatus"] == "needsHumanReview"
    assert critical["overallVerdict"] == "needsAttention"
    assert warning["issueLifecycle"]["suppressedCount"] == 1
    assert warning["editorialStatus"] == "publishableWithCaution"
    assert warning["overallVerdict"] != "cleanSuccess"


def test_structured_evidence_fidelity_drives_editorial_verdict() -> None:
    partial = reporter().build(
        run_status="succeeded",
        steps=[
            step(
                "rulePack",
                {
                    "evidenceInterpretationFidelity": {
                        "acceptedEvidenceCount": 2,
                        "interpretedEvidenceCount": 0,
                        "fallbackUsed": False,
                        "coverageVerdict": "partial",
                        "fidelityImpact": "weak",
                        "acceptedRisk": True,
                        "needsFollowUp": True,
                        "reasonCodes": ["weak-interpreted-evidence"],
                    }
                },
            ),
            step("validation", {"rankingRevision": {"finalQualityGate": {"status": "passed"}}}),
            step("complete", {}),
        ],
        final_draft=final_draft(),
    )
    missing = reporter().build(
        run_status="succeeded",
        steps=[
            step(
                "rulePack",
                {
                    "evidenceInterpretationFidelity": {
                        "acceptedEvidenceCount": 0,
                        "interpretedEvidenceCount": 1,
                        "fallbackUsed": False,
                        "coverageVerdict": "missing",
                        "fidelityImpact": "blocked",
                        "acceptedRisk": False,
                        "needsFollowUp": True,
                        "reasonCodes": ["no-accepted-evidence"],
                    }
                },
            ),
            step("validation", {"rankingRevision": {"finalQualityGate": {"status": "passed"}}}),
            step("complete", {}),
        ],
        final_draft=final_draft(),
    )

    assert partial["evidenceFidelity"]["coverageVerdict"] == "partial"
    assert partial["editorialStatus"] == "publishableWithCaution"
    assert missing["evidenceFidelity"]["coverageVerdict"] == "missing"
    assert missing["editorialStatus"] == "needsHumanReview"
    assert missing["overallVerdict"] == "needsAttention"


def test_pipeline_writes_quality_fidelity_to_validation_and_complete(tmp_path) -> None:
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    request = make_request()
    draft_context = context_from_payload({"draftContext": make_context()})
    run = create_queued_draft_run(
        request_payload=request_to_payload(request, draft_context),
        input_summary={"title": request.brief.title},
    )
    repository.save(run)

    result = DraftRunPipeline(repository, DeterministicDraftService()).execute(run.id)
    validation = next(item.artifact_payload for item in result.steps if item.key.value == "validation")
    complete = next(item.artifact_payload for item in result.steps if item.key.value == "complete")

    assert complete["qualityFidelity"]["technicalStatus"] == "succeeded"
    assert complete["qualityFidelity"]["overallVerdict"] in {"cleanSuccess", "recoveredSuccess", "degradedSuccess", "needsAttention"}
    assert validation["rankingRevision"]["qualityFidelity"] == complete["qualityFidelity"]


def reporter() -> DraftRunQualityFidelityReporter:
    return DraftRunQualityFidelityReporter()


def step(key: str, artifact: dict) -> dict:
    return {"key": key, "status": "succeeded", "artifact": artifact}


def envelope(status: str, *, backup: bool = False) -> dict:
    return {
        "operationEnvelope": {
            "operationId": "operation",
            "status": status,
            "attempts": [{"label": "backup" if backup else status, "status": status, "backup": backup, "model": "model"}],
        }
    }


def final_draft() -> dict:
    return {"title": "Draft", "body": "Useful final public prose with a clear takeaway."}
