from backend.app.application.draft_generation_params import GenerationParamProfile, generation_params_for_profile
from backend.app.settings import BackendSettings


def test_generation_params_use_defaults() -> None:
    settings = BackendSettings(_env_file=None)

    writer = generation_params_for_profile(settings, GenerationParamProfile.WRITER)
    revision = generation_params_for_profile(settings, GenerationParamProfile.REVISION)
    repair = generation_params_for_profile(settings, GenerationParamProfile.JSON_REPAIR)
    another_angle = generation_params_for_profile(settings, GenerationParamProfile.ANOTHER_ANGLE)

    assert writer.temperature == 0.65
    assert writer.top_p == 0.9
    assert revision.temperature == 0.35
    assert revision.top_p == 0.85
    assert repair.temperature == 0.15
    assert repair.top_p is None
    assert another_angle.temperature == 0.8


def test_generation_params_normalize_invalid_values() -> None:
    settings = BackendSettings(
        _env_file=None,
        DRAFT_WRITER_TEMPERATURE="bad",
        DRAFT_WRITER_TOP_P="2",
        DRAFT_REVISION_TEMPERATURE="-1",
        DRAFT_REVISION_TOP_P="bad",
        DRAFT_JSON_REPAIR_TEMPERATURE="3",
        DRAFT_ANOTHER_ANGLE_TEMPERATURE="oops",
    )

    assert generation_params_for_profile(settings, GenerationParamProfile.WRITER).temperature == 0.65
    assert generation_params_for_profile(settings, GenerationParamProfile.WRITER).top_p == 0.9
    assert generation_params_for_profile(settings, GenerationParamProfile.REVISION).temperature == 0.35
    assert generation_params_for_profile(settings, GenerationParamProfile.REVISION).top_p == 0.85
    assert generation_params_for_profile(settings, GenerationParamProfile.JSON_REPAIR).temperature == 0.15
    assert generation_params_for_profile(settings, GenerationParamProfile.ANOTHER_ANGLE).temperature == 0.8


def test_generation_params_load_env_overrides() -> None:
    settings = BackendSettings(
        _env_file=None,
        DRAFT_WRITER_TEMPERATURE="0.7",
        DRAFT_WRITER_TOP_P="0.95",
        DRAFT_REVISION_TEMPERATURE="0.4",
        DRAFT_REVISION_TOP_P="0.8",
        DRAFT_JSON_REPAIR_TEMPERATURE="0.1",
        DRAFT_ANOTHER_ANGLE_TEMPERATURE="0.85",
    )

    assert generation_params_for_profile(settings, GenerationParamProfile.WRITER).temperature == 0.7
    assert generation_params_for_profile(settings, GenerationParamProfile.WRITER).top_p == 0.95
    assert generation_params_for_profile(settings, GenerationParamProfile.REVISION).temperature == 0.4
    assert generation_params_for_profile(settings, GenerationParamProfile.REVISION).top_p == 0.8
    assert generation_params_for_profile(settings, GenerationParamProfile.JSON_REPAIR).temperature == 0.1
    assert generation_params_for_profile(settings, GenerationParamProfile.ANOTHER_ANGLE).temperature == 0.85
