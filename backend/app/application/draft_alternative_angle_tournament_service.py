from typing import Any

from backend.app.application.draft_alternative_angle_candidate_service import DraftAlternativeAngleCandidateService
from backend.app.application.draft_alternative_angle_route_service import DraftAlternativeAngleRouteService
from backend.app.application.draft_article_memory_service import context_pack_from_payload
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.draft_validation_operation_safety import safe_call
from backend.app.domain.draft_alternative_angle import AlternativeAngleTournament
from backend.app.domain.draft_generation import DraftGenerationRequest
from backend.app.domain.draft_model_roles import DraftModelRole


class DraftAlternativeAngleTournamentService:
    def __init__(
        self,
        *,
        route_service: DraftAlternativeAngleRouteService,
        candidate_service: DraftAlternativeAngleCandidateService,
    ) -> None:
        self._route_service = route_service
        self._candidate_service = candidate_service

    def run(
        self,
        *,
        request: DraftGenerationRequest,
        draft_artifact: dict[str, Any],
        validation_report: dict[str, Any],
        context_summary: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        progress: DraftRunStepOperationSink | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
        if progress:
            progress.start_operation("alternative-angle-route", kind="alternativeAngle", label="Build alternative angle route")
        route, attempts, route_ai_run_ids, route_error = safe_call(
            progress=progress,
            operation_id="alternative-angle-route",
            fallback=lambda error: (None, [], [], error),
            call=lambda: self._route_service.create(
                draft_artifact=draft_artifact,
                validation_report=validation_report,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
            ),
        )
        if not route:
            if progress:
                progress.fail_operation("alternative-angle-route", route_error or "alternative angle route was not created", ai_run_id=_last(route_ai_run_ids))
            tournament = AlternativeAngleTournament(status="not-run" if route_error == "provider-unconfigured" else "failed", attempts=attempts, ai_run_ids=route_ai_run_ids, reason=route_error)
            return draft_artifact, {**tournament.to_payload(), "inputCritiqueSummary": _critique_summary(validation_report)}, route_ai_run_ids
        if progress:
            progress.complete_operation("alternative-angle-route", ai_run_id=_last(route_ai_run_ids), notes=[f"route={route.id}"])

        if progress:
            progress.start_operation("alternative-angle-candidate", kind="alternativeAngleCandidate", label="Generate alternative angle candidate", target=route.id)
        candidate, candidate_ai_run_id, candidate_error = safe_call(
            progress=progress,
            operation_id="alternative-angle-candidate",
            fallback=lambda error: (None, None, error),
            call=lambda: self._candidate_service.create(
                request=request,
                route=route,
                context_summary=context_summary,
                rule_pack=rule_pack,
                material_plan=material_plan,
                draft_strategy=draft_strategy,
                context_pack=context_pack_from_payload(context_artifact, DraftModelRole.WRITER),
            ),
        )
        ai_run_ids = [*route_ai_run_ids, *([candidate_ai_run_id] if candidate_ai_run_id else [])]
        if not candidate:
            if progress:
                progress.fail_operation("alternative-angle-candidate", candidate_error or "alternative angle candidate was not created", ai_run_id=candidate_ai_run_id)
            tournament = AlternativeAngleTournament(status="failed", route=route, attempts=attempts, ai_run_ids=ai_run_ids, reason=candidate_error)
            return draft_artifact, {**tournament.to_payload(), "inputCritiqueSummary": _critique_summary(validation_report)}, ai_run_ids
        if progress:
            progress.complete_operation("alternative-angle-candidate", ai_run_id=candidate_ai_run_id, notes=[f"candidate={candidate.get('id')}"])

        merged = _append_candidate(draft_artifact, candidate)
        tournament = AlternativeAngleTournament(status="succeeded", route=route, candidate=candidate, attempts=attempts, ai_run_ids=ai_run_ids)
        return merged, {**tournament.to_payload(), "inputCritiqueSummary": _critique_summary(validation_report)}, ai_run_ids


def _append_candidate(draft_artifact: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    candidates = [item for item in draft_artifact.get("candidates", []) if isinstance(item, dict)]
    directions = [item for item in draft_artifact.get("directions", []) if isinstance(item, dict)]
    direction = candidate.get("direction") if isinstance(candidate.get("direction"), dict) else None
    return {
        **draft_artifact,
        "candidates": [*candidates, candidate],
        "directions": [*directions, direction] if direction else directions,
        "alternativeAngleCandidateId": candidate.get("id"),
    }


def _critique_summary(validation_report: dict[str, Any]) -> dict[str, Any]:
    critique = validation_report.get("editorialCritiqueReport") if isinstance(validation_report.get("editorialCritiqueReport"), dict) else {}
    reports = [item for item in critique.get("candidateReports", []) if isinstance(item, dict)]
    return {
        "status": critique.get("status"),
        "highRiskCandidates": [item.get("candidateId") for item in reports if item.get("editorialRisk") == "high"],
        "weakestMoves": [item.get("weakestMove") for item in reports if item.get("weakestMove")],
        "recommendedMoves": [item.get("recommendedEditorialMove") for item in reports if item.get("recommendedEditorialMove")],
    }


def _last(values: list[str]) -> str | None:
    return values[-1] if values else None
