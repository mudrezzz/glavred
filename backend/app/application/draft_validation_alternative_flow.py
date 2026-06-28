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
            draft_artifact=_only_candidate(merged, str(merged.get("alternativeAngleCandidateId"))),
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            progress=progress,
        )
        final_payload = _merge_validation_reports(initial_validation, final.artifact_payload)
        return merged, _with_tournament(final_payload, initial_validation, tournament), [*ai_run_ids, *final.ai_run_ids]


def _with_tournament(report: dict[str, Any], initial_validation: dict[str, Any], tournament: dict[str, Any]) -> dict[str, Any]:
    return {**report, "initialValidation": initial_validation, "alternativeAngleTournament": tournament}


def _only_candidate(draft_artifact: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    candidates = [item for item in draft_artifact.get("candidates", []) if isinstance(item, dict) and item.get("id") == candidate_id]
    return {**draft_artifact, "candidates": candidates}


def _merge_validation_reports(initial: dict[str, Any], challenger: dict[str, Any]) -> dict[str, Any]:
    merged = {**initial, "candidateReports": _merge_candidate_reports(initial, challenger)}
    if challenger.get("llmValidationReport"):
        merged["llmValidationReport"] = _merge_nested_reports(initial.get("llmValidationReport"), challenger.get("llmValidationReport"))
    if challenger.get("editorialCritiqueReport"):
        merged["editorialCritiqueReport"] = _merge_nested_reports(initial.get("editorialCritiqueReport"), challenger.get("editorialCritiqueReport"))
    merged["status"] = _worst_status(merged.get("candidateReports", []))
    return merged


def _merge_nested_reports(initial: Any, challenger: Any) -> dict[str, Any]:
    base = initial if isinstance(initial, dict) else {}
    extra = challenger if isinstance(challenger, dict) else {}
    return {**base, "status": _worst_status(_merge_candidate_reports(base, extra)), "candidateReports": _merge_candidate_reports(base, extra)}


def _merge_candidate_reports(initial: dict[str, Any], challenger: dict[str, Any]) -> list[dict[str, Any]]:
    reports = [item for item in initial.get("candidateReports", []) if isinstance(item, dict)]
    by_id = {str(item.get("candidateId")): item for item in reports if item.get("candidateId")}
    for item in challenger.get("candidateReports", []):
        if isinstance(item, dict) and item.get("candidateId"):
            by_id[str(item["candidateId"])] = item
    return list(by_id.values())


def _worst_status(reports: list[dict[str, Any]]) -> str:
    statuses = [str(item.get("status") or "passed") for item in reports]
    if "critical" in statuses:
        return "critical"
    if "warning" in statuses:
        return "warning"
    return statuses[0] if statuses else "not-run"
