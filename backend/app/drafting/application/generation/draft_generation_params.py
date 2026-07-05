"""Owner: drafting.application.generation

Used by: DraftRun generation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from dataclasses import dataclass
from enum import StrEnum

from backend.app.application.json_step_retry_policy import JsonStepAttempt
from backend.app.settings import BackendSettings


class GenerationParamProfile(StrEnum):
    WRITER = "writer"
    REVISION = "revision"
    JSON_REPAIR = "jsonRepair"
    ANOTHER_ANGLE = "anotherAngle"


@dataclass(frozen=True)
class DraftGenerationParams:
    profile: GenerationParamProfile
    temperature: float
    top_p: float | None = None

    def to_payload(self) -> dict[str, float | str | None]:
        payload: dict[str, float | str | None] = {
            "generationParamProfile": self.profile.value,
            "temperature": self.temperature,
        }
        if self.top_p is not None:
            payload["topP"] = self.top_p
        return payload

    def to_provider_payload(self) -> dict[str, float | str | None]:
        payload = self.to_payload()
        if self.top_p is not None:
            payload["top_p"] = self.top_p
        return payload


DEFAULT_WRITER_TEMPERATURE = 0.65
DEFAULT_WRITER_TOP_P = 0.9
DEFAULT_REVISION_TEMPERATURE = 0.35
DEFAULT_REVISION_TOP_P = 0.85
DEFAULT_JSON_REPAIR_TEMPERATURE = 0.15
DEFAULT_ANOTHER_ANGLE_TEMPERATURE = 0.8


def generation_params_for_profile(settings: BackendSettings, profile: GenerationParamProfile) -> DraftGenerationParams:
    if profile is GenerationParamProfile.WRITER:
        return DraftGenerationParams(
            profile=profile,
            temperature=_float_in_range(settings.draft_writer_temperature, DEFAULT_WRITER_TEMPERATURE, minimum=0, maximum=2),
            top_p=_float_in_range(settings.draft_writer_top_p, DEFAULT_WRITER_TOP_P, minimum=0.01, maximum=1),
        )
    if profile is GenerationParamProfile.REVISION:
        return DraftGenerationParams(
            profile=profile,
            temperature=_float_in_range(settings.draft_revision_temperature, DEFAULT_REVISION_TEMPERATURE, minimum=0, maximum=2),
            top_p=_float_in_range(settings.draft_revision_top_p, DEFAULT_REVISION_TOP_P, minimum=0.01, maximum=1),
        )
    if profile is GenerationParamProfile.ANOTHER_ANGLE:
        return DraftGenerationParams(
            profile=profile,
            temperature=_float_in_range(settings.draft_another_angle_temperature, DEFAULT_ANOTHER_ANGLE_TEMPERATURE, minimum=0, maximum=2),
        )
    return DraftGenerationParams(
        profile=GenerationParamProfile.JSON_REPAIR,
        temperature=_float_in_range(settings.draft_json_repair_temperature, DEFAULT_JSON_REPAIR_TEMPERATURE, minimum=0, maximum=2),
    )


def generation_params_for_attempt(
    settings: BackendSettings,
    *,
    primary_profile: GenerationParamProfile,
    attempt: JsonStepAttempt,
) -> DraftGenerationParams:
    if attempt.repair or attempt.backup:
        return generation_params_for_profile(settings, GenerationParamProfile.JSON_REPAIR)
    return generation_params_for_profile(settings, primary_profile)


def _float_in_range(value: str, default: float, *, minimum: float, maximum: float) -> float:
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        return default
    if minimum <= parsed <= maximum:
        return parsed
    return default
