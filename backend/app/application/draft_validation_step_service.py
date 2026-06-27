from typing import Any

from backend.app.application.draft_alternative_angle_tournament_service import DraftAlternativeAngleTournamentService
from backend.app.application.draft_editorial_critique_service import DraftEditorialCritiqueService
from backend.app.application.draft_llm_validation_service import DraftLlmValidationService
from backend.app.application.draft_ranking_revision_service import DraftRankingRevisionService
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.draft_validation_alternative_flow import DraftValidationAlternativeFlow
from backend.app.application.draft_validation_ranking_bridge import DraftValidationRankingBridge, ValidationRankingResult
from backend.app.application.draft_validation_report_flow import DraftValidationReportFlow
from backend.app.application.draft_validator_orchestrator import DraftValidatorOrchestrator
from backend.app.domain.draft_generation import DraftGenerationRequest

DraftValidationStepResult = ValidationRankingResult


class DraftValidationStepService:
    def __init__(
        self,
        *,
        deterministic_orchestrator: DraftValidatorOrchestrator | None = None,
        llm_validator: DraftLlmValidationService | None = None,
        editorial_critic: DraftEditorialCritiqueService | None = None,
        alternative_tournament: DraftAlternativeAngleTournamentService | None = None,
        ranking_revision_service: DraftRankingRevisionService | None = None,
    ) -> None:
        self._reports = DraftValidationReportFlow(
            deterministic_orchestrator=deterministic_orchestrator,
            llm_validator=llm_validator,
            editorial_critic=editorial_critic,
        )
        self._alternative = DraftValidationAlternativeFlow(reports=self._reports, alternative=alternative_tournament)
        self._ranking = DraftValidationRankingBridge(ranking_revision_service)

    def validate(
        self,
        *,
        request: DraftGenerationRequest | None = None,
        context_summary: dict[str, Any] | None = None,
        draft_artifact: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any] | None = None,
        progress: DraftRunStepOperationSink | None = None,
    ) -> DraftValidationStepResult:
        initial = self._reports.run(
            draft_artifact=draft_artifact,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            progress=progress,
        )
        if progress:
            progress.merge_artifact(initial.artifact_payload)
        active_draft, artifact_payload, ai_run_ids = self._alternative.apply(
            request=request,
            context_summary=context_summary,
            draft_artifact=draft_artifact,
            initial_validation=initial.artifact_payload,
            initial_ai_run_ids=initial.ai_run_ids,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
            progress=progress,
        )
        if progress:
            progress.merge_artifact(artifact_payload)
        result = self._ranking.apply(
            request=request,
            artifact_payload=artifact_payload,
            ai_run_ids=ai_run_ids,
            draft_artifact=active_draft,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            progress=progress,
        )
        if progress:
            progress.merge_artifact(result.artifact_payload)
        return DraftValidationStepResult(result.artifact_payload, result.ai_run_ids, result.final_draft)

    def not_run(self, *, reason: str) -> DraftValidationStepResult:
        return DraftValidationStepResult(self._reports.not_run(reason=reason).artifact_payload, [])
