from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.draft_candidate_prompts import CANDIDATE_KEYS, build_draft_candidate_messages
from backend.app.application.draft_generation_params import GenerationParamProfile, generation_params_for_attempt
from backend.app.drafting.application.planning.draft_material_plan_service import OpenRouterJsonStepAdapter
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, selection_for_attempt, unconfigured_model_selection
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_alternative_angle import AlternativeAngleRoute
from backend.app.domain.draft_candidates import DraftCandidateDirection, candidate_from_payload
from backend.app.domain.draft_generation import DraftGenerationRequest
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


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

    def create(
        self,
        *,
        request: DraftGenerationRequest,
        route: AlternativeAngleRoute,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        context_pack: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any] | None, list[str], str, list[dict[str, Any]]]:
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return None, [], "provider-unconfigured", []
        direction = _direction_from_route(route)
        primary_selection = select_model_for_role(self._settings, DraftModelRole.WRITER)
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
                rule_pack=rule_pack,
                material_plan=material_plan,
                draft_strategy=draft_strategy,
                context_pack=context_pack,
                repair_context=repair_context,
            )
            attempts.append(result["attempt"])
            if result["candidate"]:
                return result["candidate"], _ai_run_ids(attempts), "", attempts
            repair_context = {"previousAttempt": result["attempt"], "requiredShape": "title, body, rationale, usedEvidence, ruleCoverage, risks, weaknesses"}
        return None, _ai_run_ids(attempts), _last_error(attempts) or "alternative-angle-candidate-provider-failed", attempts

    def _try_attempt(
        self,
        *,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        request: DraftGenerationRequest,
        route: AlternativeAngleRoute,
        direction: DraftCandidateDirection,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        context_pack: dict[str, Any] | None,
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(role=DraftModelRole.WRITER, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        generation_params = generation_params_for_attempt(self._settings, primary_profile=GenerationParamProfile.WRITER, attempt=attempt)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup, **selection.to_payload()}
        messages = build_draft_candidate_messages(
            context_summary=context_summary,
            rule_pack=rule_pack,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
            direction=direction,
            context_pack=context_pack,
            repair_context=repair_context if attempt.repair else None,
        )
        request_payload = {
            "draftRunStep": "alternativeAngleCandidate",
            "attempt": attempt_payload,
            "route": route.to_payload(),
            "direction": direction.to_payload(),
            "contextPack": context_pack,
            "providerRequest": {
                "provider": AiRunProvider.OPENROUTER.value,
                "model": attempt.model,
                "messages": messages,
                "temperature": generation_params.temperature,
                "responseFormat": {"type": "json_object"},
            },
            "generationParams": generation_params.to_payload(),
            **selection.to_payload(),
        }
        if generation_params.top_p is not None:
            request_payload["providerRequest"]["topP"] = generation_params.top_p
        try:
            result = self._openrouter_adapter.complete_json(
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
            return {"candidate": {**payload, "aiRunId": run.id}, "attempt": _attempt_record(attempt, run.id, "accepted", selection.to_payload())}
        except Exception as exc:
            return self._attempt_error(attempt, request_payload, self._safe_error(exc), _raw_excerpt(exc))

    def unconfigured_metadata(self) -> dict[str, Any]:
        return unconfigured_model_selection(DraftModelRole.WRITER).to_payload()

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"

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
        return {"candidate": None, "attempt": _attempt_record(attempt, run.id, "error", selection, error)}


def _direction_from_route(route: AlternativeAngleRoute) -> DraftCandidateDirection:
    return DraftCandidateDirection(
        id=f"alternative-angle-{route.id}",
        title=route.title,
        angle=route.angle,
        instruction=route.opening_move or route.why_different,
        rhetorical_plan_id=route.id,
    )


def _attempt_record(attempt: JsonStepAttempt, ai_run_id: str, status: str, model_selection: dict[str, Any], validation: str | None = None) -> dict[str, Any]:
    record = {"label": attempt.label, "model": attempt.model, "status": status, "aiRunId": ai_run_id, "backup": attempt.backup, **model_selection}
    if validation:
        record["validation"] = validation
    return record


def _ai_run_ids(attempts: list[dict[str, Any]]) -> list[str]:
    return [str(attempt["aiRunId"]) for attempt in attempts if attempt.get("aiRunId")]


def _last_error(attempts: list[dict[str, Any]]) -> str | None:
    return next((str(item.get("validation")) for item in reversed(attempts) if item.get("validation")), None)


def _raw_excerpt(error: Exception) -> str | None:
    value = getattr(error, "raw_response_excerpt", None)
    return str(value) if value else None
