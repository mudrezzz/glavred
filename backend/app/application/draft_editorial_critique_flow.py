from dataclasses import dataclass
from typing import Any

from backend.app.application.draft_editorial_critique_service import DraftEditorialCritiqueService
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
