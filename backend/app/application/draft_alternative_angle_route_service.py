from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.draft_alternative_angle_audit import (
    build_alternative_angle_request_trace,
    build_alternative_angle_result_trace,
)
from backend.app.application.draft_alternative_angle_prompts import (
    ALTERNATIVE_ANGLE_KEYS,
    ALTERNATIVE_ANGLE_TEMPERATURE,
    build_alternative_angle_messages,
)
from backend.app.application.draft_article_memory_service import context_pack_from_payload
from backend.app.application.draft_material_plan_service import OpenRouterJsonStepAdapter
from backend.app.application.draft_model_role_resolver import select_model_for_role, selection_for_attempt
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_alternative_angle import AlternativeAngleRoute, alternative_route_from_payload
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


class DraftAlternativeAngleRouteService:
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
        draft_artifact: dict[str, Any],
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
    ) -> tuple[AlternativeAngleRoute | None, list[dict[str, Any]], list[str], str]:
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return None, [], [], "provider-unconfigured"
        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.ANOTHER_ANGLE)
        for attempt in build_json_step_attempts(
            primary_model=primary_selection.model or self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(attempt, primary_selection, draft_artifact, validation_report, context_artifact, rule_pack, material_plan, repair_context)
            attempts.append(result["attempt"])
            if result["route"]:
                return result["route"], attempts, [str(item["aiRunId"]) for item in attempts if item.get("aiRunId")], ""
            repair_context = {"previousAttempt": result["attempt"], "requiredShape": "object with one alternative route"}
        return None, attempts, [str(item["aiRunId"]) for item in attempts if item.get("aiRunId")], "alternative-angle-provider-failed"

    def _try_attempt(
        self,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        draft_artifact: dict[str, Any],
        validation_report: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(role=DraftModelRole.ANOTHER_ANGLE, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        context_pack = context_pack_from_payload(context_artifact, DraftModelRole.ANOTHER_ANGLE)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup, **selection.to_payload()}
        messages = build_alternative_angle_messages(
            draft_artifact=draft_artifact,
            validation_report=validation_report,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            context_pack=context_pack,
            repair_context=repair_context if attempt.repair else None,
        )
        request_payload = build_alternative_angle_request_trace(
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            messages=messages,
            context_pack=context_pack,
            attempt=attempt_payload,
            model_selection=selection.to_payload(),
        )
        try:
            result = self._openrouter_adapter.complete_json(
                settings=self._settings,
                messages=messages,
                expected_keys=ALTERNATIVE_ANGLE_KEYS,
                temperature=ALTERNATIVE_ANGLE_TEMPERATURE,
                model=attempt.model,
            )
            route = alternative_route_from_payload(result.payload)
            _validate_route(route)
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload=build_alternative_angle_result_trace(result_payload=route.to_payload(), provider_response=result.raw_response, attempt=attempt_payload),
                fallback_used=False,
            )
            return {"route": route, "attempt": _attempt_record(attempt, run.id, "accepted", selection.to_payload())}
        except Exception as exc:
            return self._record_attempt_error(attempt, request_payload, self._safe_error(exc))

    def _record_attempt_error(self, attempt: JsonStepAttempt, request_payload: dict[str, Any], error: str) -> dict[str, Any]:
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload=build_alternative_angle_result_trace(result_payload={}, provider_response=None, attempt=request_payload.get("attempt")),
            fallback_used=False,
            error=error,
        )
        selection = {key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}
        return {"route": None, "attempt": _attempt_record(attempt, run.id, "error", selection, error)}

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"


def _validate_route(route: AlternativeAngleRoute) -> None:
    if not route.angle.strip() or not route.why_different.strip():
        raise ValueError("Alternative angle route must include angle and whyDifferent")


def _attempt_record(attempt: JsonStepAttempt, ai_run_id: str, status: str, model_selection: dict[str, Any], validation: str | None = None) -> dict[str, Any]:
    record = {"label": attempt.label, "model": attempt.model, "status": status, "aiRunId": ai_run_id, "backup": attempt.backup, **model_selection}
    if validation:
        record["validation"] = validation
    return record
