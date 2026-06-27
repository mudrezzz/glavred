from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.draft_directed_revision_prompts import (
    DIRECTED_REVISION_KEYS,
    DIRECTED_REVISION_TEMPERATURE,
    build_directed_revision_messages,
)
from backend.app.application.draft_model_role_resolver import select_model_for_role, selection_for_attempt
from backend.app.application.draft_article_memory_service import context_pack_from_payload
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


class DraftDirectedRevisionService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: Any,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter

    def revise(
        self,
        *,
        candidate: dict[str, Any] | None,
        instruction: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
    ) -> dict[str, Any]:
        if not candidate:
            return {"status": "not-run", "reason": "candidate-not-found", "attempts": [], "aiRunIds": []}
        if instruction.get("status") != "created":
            return {"status": "not-run", "reason": instruction.get("reason") or "no-actionable-findings", "attempts": [], "aiRunIds": []}
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return {"status": "not-run", "reason": "provider-unconfigured", "attempts": [], "aiRunIds": []}
        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.WRITER)
        for attempt in build_json_step_attempts(
            primary_model=primary_selection.model or self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(attempt, primary_selection, candidate, instruction, context_artifact, rule_pack, material_plan, repair_context)
            attempts.append(result["attempt"])
            if result["accepted"]:
                revised = {
                    **candidate,
                    "id": f"revised-{candidate.get('id')}",
                    "baseCandidateId": candidate.get("id"),
                    "title": str(result["payload"].get("title") or ""),
                    "body": str(result["payload"].get("body") or ""),
                    "source": "openrouterRevision",
                    "aiRunId": result["attempt"].get("aiRunId"),
                    "fallbackUsed": False,
                    "changeLog": _strings(result["payload"].get("changeLog")),
                }
                return {"status": "succeeded", "revisedCandidate": revised, "attempts": attempts, "aiRunIds": _ai_run_ids(attempts)}
            repair_context = {"previousAttempt": result["attempt"], "requiredShape": "title, body, changeLog[]"}
        return {"status": "failed", "reason": "directed-revision-provider-failed", "error": _last_error(attempts), "attempts": attempts, "aiRunIds": _ai_run_ids(attempts)}

    def _try_attempt(
        self,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        candidate: dict[str, Any],
        instruction: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(role=DraftModelRole.WRITER, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        context_pack = context_pack_from_payload(context_artifact, DraftModelRole.WRITER)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup, **selection.to_payload()}
        messages = build_directed_revision_messages(
            candidate=candidate,
            instruction=instruction,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            context_pack=context_pack,
            repair_context=repair_context if attempt.repair else None,
        )
        request_payload = {"draftRunStep": "directedRevision", "attempt": attempt_payload, "contextPack": context_pack, "messages": messages, **selection.to_payload()}
        try:
            result = self._openrouter_adapter.complete_json(
                settings=self._settings,
                messages=messages,
                expected_keys=DIRECTED_REVISION_KEYS,
                temperature=DIRECTED_REVISION_TEMPERATURE,
                model=attempt.model,
            )
            if not str(result.payload.get("title") or "").strip() or not str(result.payload.get("body") or "").strip():
                raise ValueError("Directed revision title/body is empty")
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload={"draftRunStep": "directedRevision", "attempt": attempt_payload, "result": result.payload, "providerResponse": result.raw_response},
                fallback_used=False,
            )
            return {"accepted": True, "payload": result.payload, "attempt": _attempt_record(attempt, run.id, "accepted", selection.to_payload())}
        except Exception as exc:
            return self._attempt_error(attempt, request_payload, self._safe_error(exc))

    def _attempt_error(self, attempt: JsonStepAttempt, request_payload: dict[str, Any], error: str) -> dict[str, Any]:
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload={"draftRunStep": "directedRevision", "attempt": {"label": attempt.label, "model": attempt.model}, "result": {}},
            fallback_used=False,
            error=error,
        )
        selection = {key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}
        return {"accepted": False, "payload": {}, "attempt": _attempt_record(attempt, run.id, "error", selection, error)}

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"


def _attempt_record(attempt: JsonStepAttempt, ai_run_id: str, status: str, model_selection: dict[str, Any], validation: Any | None = None) -> dict[str, Any]:
    record = {"label": attempt.label, "model": attempt.model, "status": status, "aiRunId": ai_run_id, "backup": attempt.backup, **model_selection}
    if validation:
        record["validation"] = validation
    return record


def _ai_run_ids(attempts: list[dict[str, Any]]) -> list[str]:
    return [str(attempt["aiRunId"]) for attempt in attempts if attempt.get("aiRunId")]


def _last_error(attempts: list[dict[str, Any]]) -> str | None:
    return next((str(item.get("validation")) for item in reversed(attempts) if item.get("validation")), None)


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in value if str(item).strip()] if isinstance(value, list) else []
