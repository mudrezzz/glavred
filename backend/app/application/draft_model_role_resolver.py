from typing import Any

from backend.app.domain.draft_model_roles import DraftModelRole, DraftModelSelection, DraftModelSelectionSource
from backend.app.settings import BackendSettings

RECOMMENDED_MODEL_PORTFOLIO = {
    "OPENROUTER_DEFAULT_MODEL": "deepseek/deepseek-v4-pro",
    "OPENROUTER_BACKUP_MODEL": "openai/gpt-4.1-mini",
    "OPENROUTER_WEB_SEARCH_MODEL": "perplexity/sonar-pro",
    "DRAFT_RESEARCH_MODEL": "google/gemini-3.1-pro-preview",
    "DRAFT_STRATEGY_MODEL": "z-ai/glm-5.2",
    "DRAFT_WRITER_MODEL": "openai/gpt-4.1",
    "DRAFT_REVIEW_MODEL": "openai/gpt-5.4-mini",
    "DRAFT_CRITIC_MODEL": "openai/gpt-4.1",
    "DRAFT_ANOTHER_ANGLE_MODEL": "qwen/qwen3.7-max",
}

_ROLE_FIELDS = {
    DraftModelRole.RESEARCH: "draft_research_model",
    DraftModelRole.STRATEGY: "draft_strategy_model",
    DraftModelRole.WRITER: "draft_writer_model",
    DraftModelRole.REVIEW: "draft_review_model",
    DraftModelRole.CRITIC: "draft_critic_model",
    DraftModelRole.ANOTHER_ANGLE: "draft_another_angle_model",
}


def select_model_for_role(settings: BackendSettings, role: DraftModelRole) -> DraftModelSelection:
    role_model = str(getattr(settings, _ROLE_FIELDS[role], "") or "").strip()
    if role_model:
        return DraftModelSelection(role=role, model=role_model, source=DraftModelSelectionSource.ROLE)
    default_model = settings.openrouter_default_model.strip()
    if default_model:
        return DraftModelSelection(role=role, model=default_model, source=DraftModelSelectionSource.DEFAULT)
    return unconfigured_model_selection(role)


def unconfigured_model_selection(role: DraftModelRole) -> DraftModelSelection:
    return DraftModelSelection(role=role, model=None, source=DraftModelSelectionSource.UNCONFIGURED)


def selection_for_attempt(
    *,
    role: DraftModelRole,
    model: str | None,
    backup: bool,
    primary_selection: DraftModelSelection,
) -> DraftModelSelection:
    if backup:
        return DraftModelSelection(role=role, model=model, source=DraftModelSelectionSource.BACKUP)
    return DraftModelSelection(role=role, model=model, source=primary_selection.source)


def with_model_selection(payload: dict[str, Any], selection: DraftModelSelection) -> dict[str, Any]:
    payload.update(selection.to_payload())
    return payload
