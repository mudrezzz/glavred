"""Owner: drafting.application.generation

Used by: DraftRun generation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.generation.draft_candidate_prompts import CANDIDATE_KEYS
from backend.app.drafting.application.generation.draft_writer_dossier_attempt import WriterDossierAttemptBuilder
from backend.app.drafting.application.generation.draft_candidate_attempt_records import CandidateAttemptRecordComponent
from backend.app.drafting.application.operations.draft_provider_error_utils import DraftProviderErrorUtilsComponent
from backend.app.drafting.application.generation.draft_generation_params import GenerationParamProfile, generation_params_for_attempt
from backend.app.drafting.application.operations.json_step_adapter import OpenRouterJsonStepAdapter
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, selection_for_attempt, unconfigured_model_selection
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_alternative_angle import AlternativeAngleRoute
from backend.app.domain.draft_candidates import DraftCandidateDirection, candidate_from_payload
from backend.app.domain.draft_generation import DraftGenerationRequest
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings
from backend.app.drafting.domain.provider_dossier import DossierReadinessStatus, ProviderDossier


class DraftAlternativeAngleCandidateService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: OpenRouterJsonStepAdapter,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._attempt_builder = WriterDossierAttemptBuilder()

    def create(
        self,
        *,
        request: DraftGenerationRequest,
        route: AlternativeAngleRoute,
        context_summary: dict[str, Any],
        provider_dossier: ProviderDossier,
    ) -> tuple[dict[str, Any] | None, list[str], str, list[dict[str, Any]]]:
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return None, [], "provider-unconfigured", []
        direction = _direction_from_route(route)
        primary_selection = select_model_for_role(self._settings, DraftModelRole.WRITER)
        if provider_dossier.readiness_status is DossierReadinessStatus.BLOCKED:
            attempt = JsonStepAttempt(label="dossier-blocked", model=primary_selection.model or self._settings.openrouter_default_model)
            result = self._blocked_attempt(attempt, primary_selection, route, direction, context_summary, provider_dossier)
            return None, CandidateAttemptRecordComponent.ai_run_ids([result["attempt"]]), "dossier-blocked", [result["attempt"]]
        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        for attempt in build_json_step_attempts(
            primary_model=primary_selection.model or self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(
                attempt=attempt,
                primary_selection=primary_selection,
                request=request,
                route=route,
                direction=direction,
                context_summary=context_summary,
                provider_dossier=provider_dossier,
                repair_context=repair_context,
            )
            attempts.append(result["attempt"])
            if result["candidate"]:
                return result["candidate"], CandidateAttemptRecordComponent.ai_run_ids(attempts), "", attempts
            repair_context = {"previousAttempt": result["attempt"], "requiredShape": "title, body, rationale, usedEvidence, ruleCoverage, risks, weaknesses"}
        return None, CandidateAttemptRecordComponent.ai_run_ids(attempts), CandidateAttemptRecordComponent.last_error(attempts) or "alternative-angle-candidate-provider-failed", attempts

    def _try_attempt(
        self,
        *,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        request: DraftGenerationRequest,
        route: AlternativeAngleRoute,
        direction: DraftCandidateDirection,
        context_summary: dict[str, Any],
        provider_dossier: ProviderDossier,
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(role=DraftModelRole.WRITER, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        generation_params = generation_params_for_attempt(self._settings, primary_profile=GenerationParamProfile.WRITER, attempt=attempt)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup, **selection.to_payload()}
        prepared = self._attempt_builder.prepare(
            operation_id="alternativeAngleCandidate",
            draft_run_step="alternativeAngleCandidate",
            dossier=provider_dossier,
            context_summary=context_summary,
            direction=direction,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            model_role=DraftModelRole.WRITER.value,
            model_selection=selection.to_payload(),
            attempt=attempt_payload,
            generation_params=generation_params.to_payload(),
            execution_mode=self._settings.draft_run_execution_mode,
            repair_context=repair_context if attempt.repair else None,
            route=route.to_payload(),
        )
        messages = prepared.messages
        request_payload = prepared.request_payload
        try:
            result = DraftingJsonOperationClient(self._openrouter_adapter).complete(
                settings=self._settings,
                messages=messages,
                expected_keys=CANDIDATE_KEYS,
                temperature=generation_params.temperature,
                top_p=generation_params.top_p,
                model=attempt.model,
            )
            candidate = candidate_from_payload(f"alternative-angle-1-{request.brief.id}", direction, result.payload)
            if not candidate.body.strip():
                raise ValueError("Alternative angle candidate body is empty")
            payload = {
                **candidate.to_payload(source="openrouter", ai_run_id=None, fallback_used=False),
                "routeType": "alternativeAngle",
                "alternativeAngleRouteId": route.id,
                **selection.to_payload(),
            }
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload={"draftRunStep": "alternativeAngleCandidate", "attempt": attempt_payload, "candidate": payload, "providerResponse": result.raw_response},
                fallback_used=False,
            )
            return {"candidate": {**payload, "aiRunId": run.id}, "attempt": CandidateAttemptRecordComponent.record(attempt, run.id, "accepted", selection.to_payload())}
        except Exception as exc:
            return self._attempt_error(attempt, request_payload, DraftProviderErrorUtilsComponent.safe_provider_error(self._settings, exc), DraftProviderErrorUtilsComponent.raw_response_excerpt(exc))

    def _blocked_attempt(
        self,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        route: AlternativeAngleRoute,
        direction: DraftCandidateDirection,
        context_summary: dict[str, Any],
        provider_dossier: ProviderDossier,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(role=DraftModelRole.WRITER, model=attempt.model, backup=False, primary_selection=primary_selection)
        generation_params = generation_params_for_attempt(self._settings, primary_profile=GenerationParamProfile.WRITER, attempt=attempt)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": False, "backup": False, **selection.to_payload()}
        prepared = self._attempt_builder.prepare(
            operation_id="alternativeAngleCandidate",
            draft_run_step="alternativeAngleCandidate",
            dossier=provider_dossier,
            context_summary=context_summary,
            direction=direction,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            model_role=DraftModelRole.WRITER.value,
            model_selection=selection.to_payload(),
            attempt=attempt_payload,
            generation_params=generation_params.to_payload(),
            execution_mode=self._settings.draft_run_execution_mode,
            repair_context=None,
            route=route.to_payload(),
        )
        prepared.request_payload["dossierBlocked"] = True
        return self._attempt_error(attempt, prepared.request_payload, "alternative-angle-writer-dossier-blocked")

    def unconfigured_metadata(self) -> dict[str, Any]:
        return unconfigured_model_selection(DraftModelRole.WRITER).to_payload()

    def _attempt_error(self, attempt: JsonStepAttempt, request_payload: dict[str, Any], error: str, raw_response_excerpt: str | None = None) -> dict[str, Any]:
        result_payload: dict[str, Any] = {"draftRunStep": "alternativeAngleCandidate", "attempt": request_payload.get("attempt"), "candidate": None}
        if raw_response_excerpt:
            result_payload["rawResponseExcerpt"] = raw_response_excerpt
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload=result_payload,
            fallback_used=False,
            error=error,
        )
        selection = {key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}
        return {"candidate": None, "attempt": CandidateAttemptRecordComponent.record(attempt, run.id, "error", selection, error)}


def _direction_from_route(route: AlternativeAngleRoute) -> DraftCandidateDirection:
    return DraftCandidateDirection(
        id=f"alternative-angle-{route.id}",
        title=route.title,
        angle=route.angle,
        instruction=route.opening_move or route.why_different,
        rhetorical_plan_id=route.id,
    )
