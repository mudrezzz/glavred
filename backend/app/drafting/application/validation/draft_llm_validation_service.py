"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.validation.draft_llm_validation_audit import LlmValidationTraceBuilder
from backend.app.drafting.application.validation.draft_llm_validation_attempts import LlmValidationAttemptMapper
from backend.app.drafting.application.validation.draft_llm_validation_parser import LlmValidationParser
from backend.app.drafting.application.validation.draft_llm_validation_prompts import (
    LLM_VALIDATION_KEYS,
    LLM_VALIDATION_TEMPERATURE,
    LlmValidationPromptBuilder,
)
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, selection_for_attempt
from backend.app.drafting.application.artifacts.draft_article_memory_service import context_pack_from_payload
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_llm_validation import (
    LlmCandidateValidationReport,
    LlmDraftValidationReport,
    LlmValidatorAttempt,
    llm_report_status,
)
from backend.app.domain.draft_validation import DraftValidatorStatus
from backend.app.domain.draft_validation import validation_status_for
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


class DraftLlmValidationService:
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
        self._parser = LlmValidationParser()
        self._prompts = LlmValidationPromptBuilder()
        self._traces = LlmValidationTraceBuilder()
        self._attempts = LlmValidationAttemptMapper()

    def validate(
        self,
        *,
        draft_artifact: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        deterministic_report: dict[str, Any],
        progress: DraftRunStepOperationSink | None = None,
    ) -> DraftPlanningStepResult:
        candidates = [item for item in _list(draft_artifact.get("candidates")) if isinstance(item, dict)]
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return DraftPlanningStepResult(
                artifact_payload=LlmDraftValidationReport(
                    status=DraftValidatorStatus.NOT_RUN,
                    metadata={"reason": "provider-unconfigured"},
                ).to_payload(),
                ai_run_id=None,
                ai_run_ids=[],
            )
        reports: list[LlmCandidateValidationReport] = []
        for candidate in candidates:
            candidate_id = str(candidate.get("id") or "unknown-candidate")
            operation_id = f"llm-validation-{candidate_id}"
            if progress:
                progress.start_operation(operation_id, kind="llmValidation", label=f"LLM validation: {candidate_id}", target=candidate_id)
            report = self._validate_candidate(
                candidate=candidate,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                deterministic_report=self._attempts.candidate_deterministic_report(deterministic_report, str(candidate.get("id") or "")),
            )
            reports.append(report)
            ai_run_id = next((attempt.ai_run_id for attempt in reversed(report.attempts) if attempt.ai_run_id), None)
            if progress:
                if report.status == DraftValidatorStatus.NOT_RUN and report.attempts:
                    progress.fail_operation(operation_id, "LLM validation attempts did not produce a usable report.", ai_run_id=ai_run_id)
                else:
                    progress.complete_operation(operation_id, ai_run_id=ai_run_id, notes=[f"status={report.status}"])
        ai_run_ids = [attempt.ai_run_id for report in reports for attempt in report.attempts if attempt.ai_run_id]
        return DraftPlanningStepResult(
            artifact_payload=LlmDraftValidationReport(status=llm_report_status(reports), candidate_reports=reports).to_payload(),
            ai_run_id=ai_run_ids[-1] if ai_run_ids else None,
            ai_run_ids=ai_run_ids,
        )

    def _validate_candidate(
        self,
        *,
        candidate: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        deterministic_report: dict[str, Any],
    ) -> LlmCandidateValidationReport:
        candidate_id = str(candidate.get("id") or "unknown-candidate")
        attempts: list[LlmValidatorAttempt] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.REVIEW)
        for attempt in build_json_step_attempts(
            primary_model=primary_selection.model or self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_candidate_attempt(
                attempt=attempt,
                primary_selection=primary_selection,
                candidate=candidate,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                deterministic_report=deterministic_report,
                repair_context=repair_context,
            )
            attempts.append(result["attempt"])
            if result["accepted"]:
                findings, observations = self._parser.parse_report(candidate_id=candidate_id, payload=result["payload"])
                return LlmCandidateValidationReport(
                    candidate_id=candidate_id,
                    status=validation_status_for(findings),
                    findings=findings,
                    observations=observations,
                    attempts=attempts,
                )
            repair_context = {"previousAttempt": result["attempt"].to_payload(), "requiredShape": "object with summary and findings[]"}
        return LlmCandidateValidationReport(
            candidate_id=candidate_id,
            status=DraftValidatorStatus.NOT_RUN,
            attempts=attempts,
        )

    def _try_candidate_attempt(
        self,
        *,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        candidate: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        deterministic_report: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        candidate_id = str(candidate.get("id") or "unknown-candidate")
        selection = selection_for_attempt(role=DraftModelRole.REVIEW, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        context_pack = context_pack_from_payload(context_artifact, DraftModelRole.REVIEW)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup, **selection.to_payload()}
        messages = self._prompts.build_messages(
            candidate=candidate,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            material_plan=material_plan,
            deterministic_report=deterministic_report,
            context_pack=context_pack,
            repair_context=repair_context if attempt.repair else None,
        )
        request_payload = self._traces.request_trace(
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            messages=messages,
            candidate_id=candidate_id,
            attempt=attempt_payload,
            deterministic_report=deterministic_report,
            context_pack=context_pack,
            model_selection=selection.to_payload(),
        )
        try:
            result = DraftingJsonOperationClient(self._openrouter_adapter).complete(
                settings=self._settings,
                messages=messages,
                expected_keys=LLM_VALIDATION_KEYS,
                temperature=LLM_VALIDATION_TEMPERATURE,
                model=attempt.model,
            )
            if not isinstance(result.payload.get("findings"), list):
                raise ValueError("OpenRouter validation response findings is not a list")
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload=self._traces.result_trace(result_payload=result.payload, provider_response=result.raw_response, attempt=attempt_payload),
                fallback_used=False,
            )
            return {"accepted": True, "payload": result.payload, "attempt": self._attempts.attempt(attempt, candidate_id, "accepted", run.id, selection.to_payload())}
        except Exception as exc:
            return self._attempt_error(attempt, candidate_id, request_payload, self._safe_error(exc))

    def _attempt_error(self, attempt: JsonStepAttempt, candidate_id: str, request_payload: dict[str, Any], error: str) -> dict[str, Any]:
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup}
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload=self._traces.result_trace(result_payload={"summary": "", "findings": []}, provider_response=None, attempt=attempt_payload),
            fallback_used=False,
            error=error,
        )
        selection = {key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}
        return {"accepted": False, "payload": {}, "attempt": self._attempts.attempt(attempt, candidate_id, "error", run.id, selection, error)}

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"

def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
