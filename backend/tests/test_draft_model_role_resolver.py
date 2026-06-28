from backend.app.application.draft_model_role_resolver import select_model_for_final_gate, select_model_for_role
from backend.app.domain.draft_model_roles import DraftModelRole, DraftModelSelectionSource
from backend.app.settings import BackendSettings


def test_resolver_chooses_configured_role_model() -> None:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_DEFAULT_MODEL="default-model",
        DRAFT_WRITER_MODEL="writer-model",
    )

    selection = select_model_for_role(settings, DraftModelRole.WRITER)

    assert selection.model == "writer-model"
    assert selection.source == DraftModelSelectionSource.ROLE


def test_resolver_falls_back_to_default_model() -> None:
    settings = BackendSettings(_env_file=None, OPENROUTER_DEFAULT_MODEL="default-model")

    selection = select_model_for_role(settings, DraftModelRole.REVIEW)

    assert selection.model == "default-model"
    assert selection.source == DraftModelSelectionSource.DEFAULT


def test_resolver_reports_unconfigured_without_default() -> None:
    settings = BackendSettings(_env_file=None, OPENROUTER_DEFAULT_MODEL="")

    selection = select_model_for_role(settings, DraftModelRole.RESEARCH)

    assert selection.model is None
    assert selection.source == DraftModelSelectionSource.UNCONFIGURED


def test_final_gate_resolver_uses_explicit_final_gate_model() -> None:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_DEFAULT_MODEL="default-model",
        DRAFT_WRITER_MODEL="writer-model",
        DRAFT_CRITIC_MODEL="critic-model",
        DRAFT_FINAL_GATE_MODEL="final-gate-model",
    )

    selection = select_model_for_final_gate(settings)

    assert selection.model == "final-gate-model"
    assert selection.source == DraftModelSelectionSource.ROLE


def test_final_gate_resolver_prefers_independent_critic_when_explicit_model_missing() -> None:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_DEFAULT_MODEL="default-model",
        DRAFT_WRITER_MODEL="writer-model",
        DRAFT_CRITIC_MODEL="critic-model",
        DRAFT_REVIEW_MODEL="review-model",
    )

    selection = select_model_for_final_gate(settings)

    assert selection.model == "critic-model"
    assert selection.source == DraftModelSelectionSource.ROLE


def test_final_gate_resolver_avoids_writer_and_falls_back_to_review_model() -> None:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_DEFAULT_MODEL="default-model",
        DRAFT_WRITER_MODEL="shared-model",
        DRAFT_CRITIC_MODEL="shared-model",
        DRAFT_REVIEW_MODEL="review-model",
    )

    selection = select_model_for_final_gate(settings)

    assert selection.model == "review-model"
    assert selection.source == DraftModelSelectionSource.ROLE
