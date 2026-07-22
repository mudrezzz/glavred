from backend.app.settings import BackendSettings


def test_signal_extraction_model_prefers_dedicated_setting() -> None:
    settings = BackendSettings(
        _env_file=None,
        UPSTREAM_SIGNAL_EXTRACTION_MODEL="provider/extraction",
        DRAFT_REVIEW_MODEL="provider/review",
        OPENROUTER_DEFAULT_MODEL="provider/default",
    )

    assert settings.upstream_signal_extraction_model_or_default == "provider/extraction"


def test_signal_extraction_model_falls_back_to_review_then_default() -> None:
    review = BackendSettings(
        _env_file=None,
        DRAFT_REVIEW_MODEL="provider/review",
        OPENROUTER_DEFAULT_MODEL="provider/default",
    )
    default = BackendSettings(_env_file=None, OPENROUTER_DEFAULT_MODEL="provider/default")

    assert review.upstream_signal_extraction_model_or_default == "provider/review"
    assert default.upstream_signal_extraction_model_or_default == "provider/default"


def test_signal_scoring_model_uses_dedicated_then_extraction_fallback() -> None:
    dedicated = BackendSettings(
        _env_file=None,
        UPSTREAM_SIGNAL_SCORING_MODEL="provider/scoring",
        UPSTREAM_SIGNAL_EXTRACTION_MODEL="provider/extraction",
    )
    fallback = BackendSettings(
        _env_file=None,
        UPSTREAM_SIGNAL_EXTRACTION_MODEL="provider/extraction",
        DRAFT_REVIEW_MODEL="provider/review",
    )

    assert dedicated.upstream_signal_scoring_model_or_default == "provider/scoring"
    assert fallback.upstream_signal_scoring_model_or_default == "provider/extraction"
