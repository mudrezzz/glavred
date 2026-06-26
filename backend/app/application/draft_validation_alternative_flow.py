from typing import Any

from backend.app.application.draft_alternative_angle_tournament_service import DraftAlternativeAngleTournamentService
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.draft_validation_report_flow import DraftValidationReportFlow
from backend.app.domain.draft_generation import DraftGenerationRequest


class DraftValidationAlternativeFlow:
    def __init__(self, *, reports: DraftValidationReportFlow, alternative: DraftAlternativeAngleTournamentService | None = None) -> None:
        self._reports = reports
        self._alternative = alternative

    def apply(
        self,
        *,
        request: DraftGenerationRequest | None,
        context_summary: dict[str, Any] | None,
        draft_artifact: dict[str, Any],
        initial_validation: dict[str, Any],
        initial_ai_run_ids: list[str],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any] | None,
        progress: DraftRunStepOperationSink | None,
    ) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
        if not (self._alternative and request and context_summary is not None and draft_strategy is not None):
            return draft_artifact, initial_validation, initial_ai_run_ids
        merged, tournament, tournament_ids = self._alternative.run(
            request=request,
            draft_artifact=draft_artifact,
            validation_report=initial_validation,
            context_summary=context_summary,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
            progress=progress,
        )
        ai_run_ids = [*initial_ai_run_ids, *tournament_ids]
        if not merged.get("alternativeAngleCandidateId"):
            return merged, _with_tournament(initial_validation, initial_validation, tournament), ai_run_ids
        final = self._reports.run(
            draft_artifact=merged,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            progress=progress,
        )
        return merged, _with_tournament(final.artifact_payload, initial_validation, tournament), [*ai_run_ids, *final.ai_run_ids]


def _with_tournament(report: dict[str, Any], initial_validation: dict[str, Any], tournament: dict[str, Any]) -> dict[str, Any]:
    return {**report, "initialValidation": initial_validation, "alternativeAngleTournament": tournament}
