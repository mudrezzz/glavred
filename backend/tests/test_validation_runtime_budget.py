from datetime import UTC, datetime, timedelta

from backend.app.drafting.application.operations.validation_runtime_budget import (
    STOP_BUDGET_EXHAUSTED,
    STOP_MAX_ITERATIONS,
    STOP_NO_IMPROVEMENT,
    STOP_PROVIDER_INCIDENT,
    ValidationRuntimeBudgetPolicy,
    ValidationRuntimeGuard,
    normalize_validation_stop_reason,
)


def test_validation_runtime_budget_profiles_resolve_execution_mode_and_settings_caps() -> None:
    profile = ValidationRuntimeBudgetPolicy().profile_for(
        {"draftRunBudget": {"executionMode": "full"}},
        max_revision_iterations=2,
        max_final_repair_iterations=1,
    )

    assert profile.profile_id == "validationLoop:full"
    assert profile.max_wall_clock_seconds == 3600
    assert profile.max_revision_cycles == 2
    assert profile.max_final_gate_repair_cycles == 1


def test_validation_runtime_guard_denies_llm_calls_after_budget() -> None:
    profile = ValidationRuntimeBudgetPolicy().profile_for({"draftRunBudget": {"executionMode": "smoke"}})
    guard = ValidationRuntimeGuard(profile)

    for index in range(profile.max_llm_calls):
        assert guard.start_operation(f"llm-validation-{index}", "llmValidation") is True
        guard.complete_operation(f"llm-validation-{index}")

    assert guard.can_start_operation("llmValidation", "llm-validation-over-budget") is False
    assert guard.start_operation("llm-validation-over-budget", "llmValidation") is False
    assert guard.stop_reason == STOP_BUDGET_EXHAUSTED
    assert guard.snapshot()["exhausted"] is True


def test_validation_runtime_guard_denies_after_wall_clock_budget() -> None:
    current = datetime(2026, 7, 5, 10, 0, tzinfo=UTC)

    def now() -> datetime:
        return current

    profile = ValidationRuntimeBudgetPolicy().profile_for({"draftRunBudget": {"executionMode": "smoke"}})
    guard = ValidationRuntimeGuard(profile, now=now)
    current = current + timedelta(seconds=profile.max_wall_clock_seconds + 1)

    assert guard.start_operation("pairwise-ranking", "pairwiseRanking") is False
    assert guard.stop_reason == STOP_BUDGET_EXHAUSTED


def test_validation_runtime_guard_records_non_improving_stop() -> None:
    guard = ValidationRuntimeGuard(ValidationRuntimeBudgetPolicy().profile_for({"draftRunBudget": {"executionMode": "smoke"}}))

    guard.record_revision_outcome(accepted=False)

    assert guard.stop_reason == STOP_NO_IMPROVEMENT


def test_validation_stop_reason_normalization_maps_legacy_and_incident_reasons() -> None:
    assert normalize_validation_stop_reason("editorially-improved") == "acceptedQuality"
    assert normalize_validation_stop_reason("max-iterations") == STOP_MAX_ITERATIONS
    assert normalize_validation_stop_reason("provider-failed") == STOP_PROVIDER_INCIDENT
    assert normalize_validation_stop_reason("no-fresh-angle") == STOP_NO_IMPROVEMENT
