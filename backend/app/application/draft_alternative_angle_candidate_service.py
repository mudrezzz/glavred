from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.draft_candidate_prompts import CANDIDATE_KEYS, CANDIDATE_TEMPERATURE, build_draft_candidate_messages
from backend.app.application.draft_material_plan_service import OpenRouterJsonStepAdapter
from backend.app.application.draft_model_role_resolver import select_model_for_role, unconfigured_model_selection
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
    ) -> tuple[dict[str, Any] | None, str | None, str]:
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return None, None, "provider-unconfigured"
        direction = _direction_from_route(route)
        selection = select_model_for_role(self._settings, DraftModelRole.WRITER)
        messages = build_draft_candidate_messages(
            context_summary=context_summary,
            rule_pack=rule_pack,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
            direction=direction,
            context_pack=context_pack,
        )
        request_payload = {
            "draftRunStep": "alternativeAngleCandidate",
            "route": route.to_payload(),
            "direction": direction.to_payload(),
            "contextPack": context_pack,
            "providerRequest": {
                "provider": AiRunProvider.OPENROUTER.value,
                "model": selection.model,
                "messages": messages,
                "temperature": CANDIDATE_TEMPERATURE,
                "responseFormat": {"type": "json_object"},
            },
            **selection.to_payload(),
        }
        try:
            result = self._openrouter_adapter.complete_json(
                settings=self._settings,
                messages=messages,
                expected_keys=CANDIDATE_KEYS,
                temperature=CANDIDATE_TEMPERATURE,
                model=selection.model,
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
                model=selection.model,
                request_payload=request_payload,
                result_payload={"draftRunStep": "alternativeAngleCandidate", "candidate": payload, "providerResponse": result.raw_response},
                fallback_used=False,
            )
            return {**payload, "aiRunId": run.id}, run.id, ""
        except Exception as exc:
            error = self._safe_error(exc)
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=selection.model,
                request_payload=request_payload,
                result_payload={"draftRunStep": "alternativeAngleCandidate", "candidate": None},
                fallback_used=False,
                error=error,
            )
            return None, run.id, error

    def unconfigured_metadata(self) -> dict[str, Any]:
        return unconfigured_model_selection(DraftModelRole.WRITER).to_payload()

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"


def _direction_from_route(route: AlternativeAngleRoute) -> DraftCandidateDirection:
    return DraftCandidateDirection(
        id=f"alternative-angle-{route.id}",
        title=route.title,
        angle=route.angle,
        instruction=route.opening_move or route.why_different,
        rhetorical_plan_id=route.id,
    )
