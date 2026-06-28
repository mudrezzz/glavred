from backend.app.settings import BackendSettings


def test_settings_loads_draft_role_models() -> None:
    settings = BackendSettings(
        _env_file=None,
        DRAFT_RESEARCH_MODEL="research-model",
        DRAFT_STRATEGY_MODEL="strategy-model",
        DRAFT_WRITER_MODEL="writer-model",
        DRAFT_REVIEW_MODEL="review-model",
        DRAFT_CRITIC_MODEL="critic-model",
        DRAFT_FINAL_GATE_MODEL="final-gate-model",
        DRAFT_ANOTHER_ANGLE_MODEL="angle-model",
    )

    assert settings.draft_research_model == "research-model"
    assert settings.draft_strategy_model == "strategy-model"
    assert settings.draft_writer_model == "writer-model"
    assert settings.draft_review_model == "review-model"
    assert settings.draft_critic_model == "critic-model"
    assert settings.draft_final_gate_model == "final-gate-model"
    assert settings.draft_another_angle_model == "angle-model"
