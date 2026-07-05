from backend.app.application.draft_candidate_result import DraftCandidateGenerationResult
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.domain.draft_generation import GeneratedDraft
from backend.app.drafting.application.steps.contracts import (
    DraftStepContext,
    DraftStepOutcome,
    DraftStepOutcomeStatus,
    DraftStepTrace,
)
from backend.app.drafting.application.steps.legacy_adapters import (
    DraftCandidateStepOutcomeAdapter,
    DraftPlanningStepOutcomeAdapter,
)


def test_draft_step_outcome_success_serializes_trace_and_ai_runs() -> None:
    trace = DraftStepTrace(
        step_key="materialPlan",
        operation_name="material-plan-json",
        ai_run_ids=("ai-1",),
        attempts=({"label": "primary", "status": "accepted"},),
        warnings=("trimmed evidence",),
        metadata={"profile": "standard"},
    )

    outcome = DraftStepOutcome.succeeded(
        artifact_payload={"materialPlan": {"sections": []}},
        ai_run_id="ai-1",
        ai_run_ids=["ai-1", "ai-2"],
        trace=trace,
        result_payload={"selected": "candidate-1"},
    )

    assert outcome.status is DraftStepOutcomeStatus.SUCCEEDED
    assert outcome.ai_run_ids == ("ai-1", "ai-2")
    assert outcome.to_payload() == {
        "status": "succeeded",
        "artifactPayload": {"materialPlan": {"sections": []}},
        "aiRunIds": ["ai-1", "ai-2"],
        "error": None,
        "trace": {
            "stepKey": "materialPlan",
            "operationName": "material-plan-json",
            "aiRunIds": ["ai-1"],
            "attempts": [{"label": "primary", "status": "accepted"}],
            "warnings": ["trimmed evidence"],
            "metadata": {"profile": "standard"},
        },
        "resultPayload": {"selected": "candidate-1"},
    }


def test_draft_step_outcome_failure_and_skip_keep_safe_reason() -> None:
    failed = DraftStepOutcome.failed(error="provider failed", ai_run_ids=["ai-1"])
    skipped = DraftStepOutcome.skipped(reason="provider not configured")

    assert failed.to_payload()["status"] == "failed"
    assert failed.to_payload()["error"] == "provider failed"
    assert failed.to_payload()["aiRunIds"] == ["ai-1"]
    assert skipped.to_payload()["status"] == "skipped"
    assert skipped.to_payload()["error"] == "provider not configured"


def test_draft_step_context_serializes_provider_free_payload() -> None:
    context = DraftStepContext(
        run_id="run-1",
        step_key="draft",
        request_payload={"briefId": "brief-1"},
        prior_artifacts={"context": {"topicId": "topic-1"}},
        metadata={"role": "writer"},
    )

    assert context.to_payload() == {
        "runId": "run-1",
        "stepKey": "draft",
        "requestPayload": {"briefId": "brief-1"},
        "priorArtifacts": {"context": {"topicId": "topic-1"}},
        "metadata": {"role": "writer"},
    }


def test_planning_step_adapter_round_trips_legacy_result() -> None:
    legacy = DraftPlanningStepResult(
        artifact_payload={"source": "openrouter"},
        ai_run_id="ai-primary",
        ai_run_ids=["ai-primary", "ai-repair"],
    )

    outcome = DraftPlanningStepOutcomeAdapter.from_legacy(legacy)
    restored = DraftPlanningStepOutcomeAdapter.to_legacy(outcome)

    assert outcome.status is DraftStepOutcomeStatus.SUCCEEDED
    assert outcome.ai_run_ids == ("ai-primary", "ai-repair")
    assert restored == legacy


def test_candidate_step_adapter_preserves_final_draft() -> None:
    final_draft = GeneratedDraft(
        id="draft-1",
        brief_id="brief-1",
        title="Title",
        body="Body",
        version=1,
        status="ready",
        updated_at="2026-07-03T00:00:00Z",
    )
    legacy = DraftCandidateGenerationResult(
        artifact_payload={"candidates": []},
        final_draft=final_draft,
        ai_run_ids=["ai-candidate"],
    )

    outcome = DraftCandidateStepOutcomeAdapter.from_legacy(legacy)
    restored = DraftCandidateStepOutcomeAdapter.to_legacy(outcome)

    assert outcome.result_payload["final_draft"] is final_draft
    assert restored == legacy
