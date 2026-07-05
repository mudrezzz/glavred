from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.planning.deterministic_rhetorical_plan_service import DeterministicRhetoricalPlanService
from backend.app.drafting.application.planning.draft_rhetorical_plan_service import DraftRhetoricalPlanService
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings


@dataclass
class FakeOpenRouterResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


def rhetorical_service(tmp_path, adapter: object, *, configured: bool, backup_model: str = "", strategy_model: str = "") -> DraftRhetoricalPlanService:
    return DraftRhetoricalPlanService(
        settings=settings(configured, backup_model=backup_model, strategy_model=strategy_model),
        ai_run_service=ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
        deterministic_plan_service=DeterministicRhetoricalPlanService(),
    )


def ai_service(tmp_path) -> AiRunService:
    return AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))


def settings(configured: bool, backup_model: str = "", strategy_model: str = "") -> BackendSettings:
    return BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="sk-test-secret" if configured else "",
        OPENROUTER_DEFAULT_MODEL="test-model" if configured else "",
        OPENROUTER_BACKUP_MODEL=backup_model,
        DRAFT_STRATEGY_MODEL=strategy_model,
    )


def context_artifact() -> dict[str, Any]:
    return {
        "postContract": {
            "title": "Post",
            "thesis": "Thesis",
            "cta": "Check rollout quality",
            "claims": [{"id": "claim-1"}],
            "riskNotes": ["Overclaiming"],
        }
    }
