from dataclasses import dataclass
from typing import Any

from backend.app.application.draft_llm_validation_service import DraftLlmValidationService
from backend.app.application.draft_validator_orchestrator import DraftValidatorOrchestrator


@dataclass(frozen=True)
class DraftValidationStepResult:
    artifact_payload: dict[str, Any]
    ai_run_ids: list[str]


class DraftValidationStepService:
    def __init__(
        self,
        *,
        deterministic_orchestrator: DraftValidatorOrchestrator | None = None,
        llm_validator: DraftLlmValidationService | None = None,
    ) -> None:
        self._deterministic = deterministic_orchestrator or DraftValidatorOrchestrator()
        self._llm_validator = llm_validator

    def validate(
        self,
        *,
        draft_artifact: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
    ) -> DraftValidationStepResult:
        deterministic_report = self._deterministic.validate(
            draft_artifact=draft_artifact,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        ).to_payload()
        if not self._llm_validator:
            return DraftValidationStepResult(deterministic_report, [])
        llm_result = self._llm_validator.validate(
            draft_artifact=draft_artifact,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            deterministic_report=deterministic_report,
        )
        return DraftValidationStepResult(
            {**deterministic_report, "llmValidationReport": llm_result.artifact_payload},
            llm_result.ai_run_ids or [],
        )

    def not_run(self, *, reason: str) -> DraftValidationStepResult:
        return DraftValidationStepResult(self._deterministic.not_run(reason=reason).to_payload(), [])
