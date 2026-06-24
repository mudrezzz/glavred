from typing import Any

from backend.app.application.draft_validator_orchestrator import DraftValidatorOrchestrator


def validation_artifact(
    *,
    draft_artifact: dict[str, Any],
    context_artifact: dict[str, Any],
    rule_pack: dict[str, Any],
    material_plan: dict[str, Any],
) -> dict[str, Any]:
    return DraftValidatorOrchestrator().validate(
        draft_artifact=draft_artifact,
        context_artifact=context_artifact,
        rule_pack=rule_pack,
        material_plan=material_plan,
    ).to_payload()


def validation_not_run_artifact(reason: str) -> dict[str, Any]:
    return DraftValidatorOrchestrator().not_run(reason=reason).to_payload()
