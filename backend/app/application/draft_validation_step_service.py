from dataclasses import dataclass
from typing import Any

from backend.app.application.draft_llm_validation_service import DraftLlmValidationService
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.draft_ranking_revision_service import DraftRankingRevisionService
from backend.app.application.draft_validation_ranking_bridge import DraftValidationRankingBridge
from backend.app.application.draft_validator_orchestrator import DraftValidatorOrchestrator
from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft


@dataclass(frozen=True)
class DraftValidationStepResult:
    artifact_payload: dict[str, Any]
    ai_run_ids: list[str]
    final_draft: GeneratedDraft | None = None


class DraftValidationStepService:
    def __init__(
        self,
        *,
        deterministic_orchestrator: DraftValidatorOrchestrator | None = None,
        llm_validator: DraftLlmValidationService | None = None,
        ranking_revision_service: DraftRankingRevisionService | None = None,
    ) -> None:
        self._deterministic = deterministic_orchestrator or DraftValidatorOrchestrator()
        self._llm_validator = llm_validator
        self._ranking = DraftValidationRankingBridge(ranking_revision_service)

    def validate(
        self,
        *,
        request: DraftGenerationRequest | None = None,
        draft_artifact: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        progress: DraftRunStepOperationSink | None = None,
    ) -> DraftValidationStepResult:
        if progress:
            progress.start_operation("deterministic-lint", kind="deterministicLint", label="Run deterministic validators")
        deterministic_report = self._deterministic.validate(
            draft_artifact=draft_artifact,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
        ).to_payload()
        if progress:
            progress.complete_operation("deterministic-lint")
        if not self._llm_validator:
            result = self._ranking.apply(
                request=request,
                artifact_payload=deterministic_report,
                ai_run_ids=[],
                draft_artifact=draft_artifact,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                progress=progress,
            )
            return DraftValidationStepResult(result.artifact_payload, result.ai_run_ids, result.final_draft)
        llm_result = self._llm_validator.validate(
            draft_artifact=draft_artifact,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            deterministic_report=deterministic_report,
            progress=progress,
        )
        result = self._ranking.apply(
            request=request,
            artifact_payload={**deterministic_report, "llmValidationReport": llm_result.artifact_payload},
            ai_run_ids=llm_result.ai_run_ids or [],
            draft_artifact=draft_artifact,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            progress=progress,
        )
        return DraftValidationStepResult(result.artifact_payload, result.ai_run_ids, result.final_draft)

    def not_run(self, *, reason: str) -> DraftValidationStepResult:
        return DraftValidationStepResult(self._deterministic.not_run(reason=reason).to_payload(), [])
