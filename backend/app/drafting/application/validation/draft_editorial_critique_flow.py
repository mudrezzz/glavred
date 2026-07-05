"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from dataclasses import dataclass
from typing import Any

from backend.app.drafting.application.validation.draft_editorial_critique_service import DraftEditorialCritiqueService
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink


@dataclass(frozen=True)
class EditorialCritiqueFlowResult:
    artifact_payload: dict[str, Any]
    ai_run_ids: list[str]


def append_editorial_critique(
    editorial_critic: DraftEditorialCritiqueService | None,
    *,
    artifact_payload: dict[str, Any],
    ai_run_ids: list[str],
    draft_artifact: dict[str, Any],
    context_artifact: dict[str, Any],
    rule_pack: dict[str, Any],
    material_plan: dict[str, Any],
    deterministic_report: dict[str, Any],
    llm_validation_report: dict[str, Any],
    progress: DraftRunStepOperationSink | None = None,
) -> EditorialCritiqueFlowResult:
    if not editorial_critic:
        return EditorialCritiqueFlowResult(artifact_payload, ai_run_ids)

    critique_result = editorial_critic.critique(
        draft_artifact=draft_artifact,
        context_artifact=context_artifact,
        rule_pack=rule_pack,
        material_plan=material_plan,
        deterministic_report=deterministic_report,
        llm_validation_report=llm_validation_report,
        progress=progress,
    )
    return EditorialCritiqueFlowResult(
        {**artifact_payload, "editorialCritiqueReport": critique_result.artifact_payload},
        [*ai_run_ids, *(critique_result.ai_run_ids or [])],
    )
