from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_rhetorical_plan_service import DeterministicRhetoricalPlanService
from backend.app.application.draft_planning_result import DraftPlanningStepResult
from backend.app.application.draft_rhetorical_plan_audit import (
    build_rhetorical_plan_request_trace,
    build_rhetorical_plan_result_trace,
)
from backend.app.application.draft_rhetorical_plan_prompts import (
    RHETORICAL_PLAN_KEYS,
    RHETORICAL_PLAN_TEMPERATURE,
    build_rhetorical_plan_messages,
)
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_rhetorical_plan import rhetorical_plan_set_from_payload
from backend.app.settings import BackendSettings


class DraftRhetoricalPlanRetryOrchestrator:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_adapter: Any,
        deterministic_plan_service: DeterministicRhetoricalPlanService,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_adapter = openrouter_adapter
        self._deterministic_plan_service = deterministic_plan_service

    def create_with_retry(
        self,
        *,
        context_summary: dict[str, Any],
        rule_registry: dict[str, Any],
        post_contract: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
    ) -> DraftPlanningStepResult:
        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        for attempt in build_json_step_attempts(
            primary_model=self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(attempt, context_summary, rule_registry, post_contract, material_plan, draft_strategy, repair_context)
            attempts.append(result["attempt"])
            if result["accepted"]:
                return DraftPlanningStepResult(
                    artifact_payload=self._artifact("openrouter", result["payload"], result["aiRunId"], False, attempts=attempts),
                    ai_run_id=result["aiRunId"],
                    ai_run_ids=[str(item["aiRunId"]) for item in attempts if item.get("aiRunId")],
                )
            repair_context = {"previousAttempt": result["attempt"], "requiredShape": "object with plans[2..3]"}
        return self._fallback(context_summary, rule_registry, post_contract, material_plan, draft_strategy, attempts)

    def _try_attempt(
        self,
        attempt: JsonStepAttempt,
        context_summary: dict[str, Any],
        rule_registry: dict[str, Any],
        post_contract: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup}
        messages = build_rhetorical_plan_messages(
            context_summary=context_summary,
            rule_registry=rule_registry,
            post_contract=post_contract,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
            repair_context=repair_context if attempt.repair else None,
        )
        request_payload = build_rhetorical_plan_request_trace(
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            messages=messages,
            context_summary=context_summary,
            post_contract=post_contract,
            rule_registry=rule_registry,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
            attempt=attempt_payload,
        )
        try:
            result = self._openrouter_adapter.complete_json(
                settings=self._settings,
                messages=messages,
                expected_keys=RHETORICAL_PLAN_KEYS,
                temperature=RHETORICAL_PLAN_TEMPERATURE,
                model=attempt.model,
            )
            payload = rhetorical_plan_set_from_payload(result.payload).to_payload()
            if len(payload.get("plans") or []) < 2:
                raise ValueError("OpenRouter returned fewer than two rhetorical plans")
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload=build_rhetorical_plan_result_trace(result_payload=payload, provider_response=result.raw_response, attempt=attempt_payload),
                fallback_used=False,
            )
            return {"accepted": True, "payload": payload, "aiRunId": run.id, "attempt": self._attempt_record(attempt, run.id, "accepted")}
        except Exception as exc:
            return self._record_attempt_error(attempt, request_payload, self._safe_error(exc))

    def _record_attempt_error(self, attempt: JsonStepAttempt, request_payload: dict[str, Any], error: str) -> dict[str, Any]:
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload=build_rhetorical_plan_result_trace(
                result_payload={"plans": []},
                provider_response=None,
                attempt={"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup},
            ),
            fallback_used=False,
            error=error,
        )
        return {"accepted": False, "payload": {}, "aiRunId": run.id, "attempt": self._attempt_record(attempt, run.id, "error", error)}

    def _fallback(
        self,
        context_summary: dict[str, Any],
        rule_registry: dict[str, Any],
        post_contract: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        attempts: list[dict[str, Any]],
    ) -> DraftPlanningStepResult:
        payload = self._deterministic_plan_service.create_plans(
            context_summary=context_summary,
            rule_registry=rule_registry,
            post_contract=post_contract,
            material_plan=material_plan,
            draft_strategy=draft_strategy,
        ).to_payload()
        error = "RhetoricalPlans JSON generation failed after all LLM attempts"
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=self._settings.openrouter_default_model,
            request_payload={"draftRunStep": "rhetoricalPlans", "attempts": attempts},
            result_payload=build_rhetorical_plan_result_trace(result_payload=payload, provider_response=None, fallback="deterministic"),
            fallback_used=True,
            error=error,
        )
        fallback_attempt = {"label": "deterministic-fallback", "model": "deterministic", "status": "fallback", "aiRunId": run.id, "backup": False}
        return DraftPlanningStepResult(
            artifact_payload=self._artifact("deterministicFallback", payload, run.id, True, error=error, attempts=[*attempts, fallback_attempt]),
            ai_run_id=run.id,
            ai_run_ids=[str(item["aiRunId"]) for item in attempts if item.get("aiRunId")] + [run.id],
        )

    def _artifact(self, source: str, payload: dict[str, Any], ai_run_id: str, fallback_used: bool, *, attempts: list[dict[str, Any]], error: str | None = None) -> dict[str, Any]:
        artifact = {"source": source, "aiRunId": ai_run_id, "fallbackUsed": fallback_used, "rhetoricalPlanSet": payload, "attempts": attempts}
        if error:
            artifact["error"] = error
        return artifact

    def _attempt_record(self, attempt: JsonStepAttempt, ai_run_id: str, status: str, validation: Any | None = None) -> dict[str, Any]:
        record = {"label": attempt.label, "model": attempt.model, "status": status, "aiRunId": ai_run_id, "backup": attempt.backup}
        if validation:
            record["validation"] = validation
        return record

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"
