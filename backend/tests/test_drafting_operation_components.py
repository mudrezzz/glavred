from backend.app.drafting.application.operations.payload_budget_profiles import PayloadBudgetProfileRegistry
from backend.app.drafting.application.operations.payload_budget_runtime import PayloadBudgetAttemptStatsExtractor
from backend.app.drafting.application.operations.validation_progress_runtime import ValidationProgressRuntimePresenter
from backend.app.drafting.application.operations.validation_revision_loop_payloads import ValidationRevisionLoopPayloadFactory
from backend.app.drafting.application.operations.validation_runtime_budget import (
    STOP_BUDGET_EXHAUSTED,
    STOP_PROVIDER_INCIDENT,
    ValidationRuntimeBudgetIncidentFactory,
    ValidationRuntimeBudgetPolicy,
    ValidationRuntimeGuard,
    ValidationStopReasonPolicy,
)


def test_payload_budget_profile_registry_builds_execution_mode_caps() -> None:
    profile = PayloadBudgetProfileRegistry.build_profile("op", "kind", "writer", "smoke")

    assert profile.operation_id == "op"
    assert profile.execution_mode == "smoke"
    assert profile.max_prompt_chars == 12000
    assert profile.approx_token_budget == 3000


def test_payload_budget_attempt_stats_extractor_reads_last_attempt_stats() -> None:
    attempts = [
        {"inputStats": {"candidateCount": 1}, "payloadStats": {"old": True}},
        {"inputStats": {"candidateCount": 2}, "payloadStats": {"payloadBudget": {"profileId": "x"}}},
    ]

    extractor = PayloadBudgetAttemptStatsExtractor()

    assert extractor.last_input_stats(attempts) == {"candidateCount": 2}
    assert extractor.last_payload_stats(attempts) == {"payloadBudget": {"profileId": "x"}}


def test_validation_progress_runtime_presenter_attaches_budget_snapshot() -> None:
    guard = ValidationRuntimeGuard(ValidationRuntimeBudgetPolicy().profile_for({"draftRunBudget": {"executionMode": "smoke"}}))
    operation = {"id": "op-1"}

    presenter = ValidationProgressRuntimePresenter()
    assert presenter.start_runtime_operation(guard, operation, operation_id="op-1", kind="llmValidation", notes=["n"]) is True
    payload = presenter.attach_runtime_budget({"status": "running"}, guard)

    assert operation["status"] == "running"
    assert payload["runtimeBudget"]["currentOperationId"] == "op-1"
    assert presenter.runtime_progress_budget(guard, operation_count=1, expected_operation_count=2)["staleAfterSeconds"] == 180


def test_validation_stop_reason_and_budget_incident_policies() -> None:
    profile = ValidationRuntimeBudgetPolicy().profile_for({"draftRunBudget": {"executionMode": "smoke"}})
    guard = ValidationRuntimeGuard(profile)
    for index in range(profile.max_llm_calls):
        assert guard.start_operation(f"llm-{index}", "llmValidation") is True
        guard.complete_operation(f"llm-{index}")

    progress = type("Progress", (), {"runtime_guard": guard})()

    assert ValidationRuntimeBudgetIncidentFactory().operation_denied(
        progress,
        kind="llmValidation",
        operation_id="over-budget",
        detail="llm-budget-denied",
    )
    assert guard.stop_reason == STOP_BUDGET_EXHAUSTED
    assert ValidationStopReasonPolicy().normalize("provider-failed") == STOP_PROVIDER_INCIDENT


def test_validation_revision_loop_payload_factory_preserves_report_shape() -> None:
    factory = ValidationRevisionLoopPayloadFactory()

    cycle = factory.successful_cycle(
        cycle_number=1,
        current_id="c1",
        revised={"id": "r1"},
        validation_before={},
        validation_after={},
        comparison={"decision": {"winnerCandidateId": "r1"}},
        repair_goals=["g"],
        constraints=[],
        goal_result={"resolved": ["g"], "unresolved": []},
        editorial_goals=[],
        editorial_result={
            "editorialDimensionScores": {},
            "resolvedEditorialGoals": [],
            "unresolvedEditorialGoals": [],
        },
        new_rejected_moves=[],
        accepted=True,
        decision_reasons=["accepted"],
        stop_reason="acceptedQuality",
        ai_run_ids=["ai-1"],
    )
    report = factory.revision_loop_report(
        current={"id": "r1"},
        cycles=[cycle],
        max_iterations=3,
        stop_reason="acceptedQuality",
        constraints=[],
        detail_stop_reason=None,
        runtime_budget={"stopReason": "acceptedQuality"},
    )

    assert report.final_candidate_id == "r1"
    assert report.final_source == "revisionLoop"
    assert report.runtime_budget == {"stopReason": "acceptedQuality"}
