from backend.app.drafting.application.revision.draft_revision_acceptance_policy import RevisionAcceptancePolicy


def test_revision_acceptance_records_pairwise_reason_without_resolved_goals() -> None:
    accepted, reasons = RevisionAcceptancePolicy().acceptance_decision(
        current_id="candidate-1",
        revised_id="revised-candidate-1",
        regression_reasons=["revision-preserves-or-improves-deterministic-validation"],
        resolved_goals=[],
        resolved_editorial_goals=[],
        regressed_editorial_dimensions=[],
        pairwise_winner="revised-candidate-1",
    )

    assert accepted is True
    assert "pairwise-selected-revised" in reasons
    assert "no-deterministic-regression" in reasons


def test_revision_without_goals_or_pairwise_win_is_rejected() -> None:
    accepted, reasons = RevisionAcceptancePolicy().acceptance_decision(
        current_id="candidate-1",
        revised_id="revised-candidate-1",
        regression_reasons=["revision-preserves-or-improves-deterministic-validation"],
        resolved_goals=[],
        resolved_editorial_goals=[],
        regressed_editorial_dimensions=[],
        pairwise_winner="candidate-1",
    )

    assert accepted is False
    assert "revision-did-not-prove-improvement" in reasons
    assert "previous-best-won-pairwise" in reasons


def test_revision_with_regression_is_rejected_even_if_pairwise_wins() -> None:
    accepted, reasons = RevisionAcceptancePolicy().acceptance_decision(
        current_id="candidate-1",
        revised_id="revised-candidate-1",
        regression_reasons=["critical-count-increased"],
        resolved_goals=[],
        resolved_editorial_goals=[],
        regressed_editorial_dimensions=[],
        pairwise_winner="revised-candidate-1",
    )

    assert accepted is False
    assert "critical-count-increased" in reasons
