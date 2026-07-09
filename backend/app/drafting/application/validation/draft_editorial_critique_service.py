"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.validation.draft_editorial_critique_audit import EditorialCritiqueTraceBuilder
from backend.app.drafting.application.validation.draft_editorial_critique_attempts import EditorialCritiqueAttemptMapper
from backend.app.drafting.application.validation.draft_editorial_critique_parser import EditorialCritiqueParser
from backend.app.drafting.application.validation.draft_editorial_critique_prompts import (
    EDITORIAL_CRITIQUE_KEYS,
    EDITORIAL_CRITIQUE_TEMPERATURE,
    EditorialCritiquePromptBuilder,
)
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, selection_for_attempt
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.drafting.application.operations.payload_budget_runtime import DraftRunPayloadBudgetRuntime
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_editorial_critique import (
    EditorialCandidateCritique,
    EditorialCriticAttempt,
    EditorialCritiqueReport,
    editorial_critique_status,
)
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_validation import DraftValidatorStatus, validation_status_for
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings


class DraftEditorialCritiqueService:
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
        self._payload_budget_runtime = DraftRunPayloadBudgetRuntime()
        self._parser = EditorialCritiqueParser()
        self._prompts = EditorialCritiquePromptBuilder()
        self._traces = EditorialCritiqueTraceBuilder()
        self._attempts = EditorialCritiqueAttemptMapper()

    def critique(
        self,
        *,
        draft_artifact: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        deterministic_report: dict[str, Any],
        llm_validation_report: dict[str, Any],
        progress: DraftRunStepOperationSink | None = None,
    ) -> DraftPlanningStepResult:
        candidates = [item for item in _list(draft_artifact.get("candidates")) if isinstance(item, dict)]
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return DraftPlanningStepResult(
                artifact_payload=EditorialCritiqueReport(
                    status=DraftValidatorStatus.NOT_RUN,
                    metadata={"reason": "provider-unconfigured", "operationEnvelope": self._attempts.not_configured_envelope(len(candidates))},
                ).to_payload(),
                ai_run_id=None,
                ai_run_ids=[],
            )
        reports: list[EditorialCandidateCritique] = []
        for candidate in candidates:
            candidate_id = str(candidate.get("id") or "unknown-candidate")
            operation_id = f"editorial-critique-{candidate_id}"
            if progress:
                progress.start_operation(operation_id, kind="editorialCritique", label=f"Editorial critique: {candidate_id}", target=candidate_id)
            report = self._critique_candidate(
                candidate=candidate,
                draft_artifact=draft_artifact,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                deterministic_report=self._attempts.candidate_report(deterministic_report, candidate_id),
                llm_validation_report=self._attempts.candidate_report(llm_validation_report, candidate_id),
            )
            reports.append(report)
            ai_run_id = next((attempt.ai_run_id for attempt in reversed(report.attempts) if attempt.ai_run_id), None)
            if progress:
                if report.status == DraftValidatorStatus.NOT_RUN:
                    progress.fail_operation(operation_id, "Editorial critique attempts did not produce a usable report.", ai_run_id=ai_run_id)
                else:
                    progress.complete_operation(operation_id, ai_run_id=ai_run_id, notes=[f"status={report.status}", f"risk={report.editorial_risk}"])
        ai_run_ids = [attempt.ai_run_id for report in reports for attempt in report.attempts if attempt.ai_run_id]
        return DraftPlanningStepResult(
            artifact_payload=EditorialCritiqueReport(status=editorial_critique_status(reports), candidate_reports=tuple(reports)).to_payload(),
            ai_run_id=ai_run_ids[-1] if ai_run_ids else None,
            ai_run_ids=ai_run_ids,
        )

    def _critique_candidate(
        self,
        *,
        candidate: dict[str, Any],
        draft_artifact: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        deterministic_report: dict[str, Any],
        llm_validation_report: dict[str, Any],
    ) -> EditorialCandidateCritique:
        candidate_id = str(candidate.get("id") or "unknown-candidate")
        attempts: list[EditorialCriticAttempt] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.CRITIC)
        for attempt in build_json_step_attempts(
            primary_model=primary_selection.model or self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(
                attempt=attempt,
                primary_selection=primary_selection,
                candidate=candidate,
                draft_artifact=draft_artifact,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                deterministic_report=deterministic_report,
                llm_validation_report=llm_validation_report,
                repair_context=repair_context,
            )
            attempts.append(result["attempt"])
            if result["accepted"]:
                payload = result["payload"]
                findings, observations = self._parser.parse(candidate_id=candidate_id, payload=payload)
                return EditorialCandidateCritique(
                    candidate_id=candidate_id,
                    status=validation_status_for(findings),
                    editorial_risk=self._parser.editorial_risk(payload.get("editorialRisk")),
                    overall_judgment=str(payload.get("overallJudgment") or payload.get("summary") or ""),
                    strongest_move=str(payload.get("strongestMove") or ""),
                    weakest_move=str(payload.get("weakestMove") or ""),
                    recommended_editorial_move=str(payload.get("recommendedEditorialMove") or ""),
                    findings=tuple(findings),
                    observations=tuple(observations),
                    attempts=tuple(attempts),
                    operation_envelope=self._attempts.candidate_envelope(candidate_id, attempts, "accepted", payload=payload),
                )
            repair_context = {
                "previousAttempt": result["attempt"].to_payload(),
                "previousError": result["attempt"].validation,
                "requiredShape": "object with all editorial critique keys",
                "requiredKeys": sorted(EDITORIAL_CRITIQUE_KEYS),
                "repairInstructions": [
                    "Return one JSON object only.",
                    "Include every required key even if findings or observations are empty arrays.",
                    "Use findings=[] and observations=[] instead of omitting either field.",
                    "Do not wrap JSON in markdown or prose.",
                ],
            }
        safe_error = self._attempts.last_attempt_error(attempts) or "Editorial critique attempts did not produce a usable report"
        return EditorialCandidateCritique(
            candidate_id=candidate_id,
            status=DraftValidatorStatus.NOT_RUN,
            attempts=tuple(attempts),
            operation_envelope=self._attempts.candidate_envelope(
                candidate_id,
                attempts,
                "notRun",
                safe_error=safe_error,
                failure_reason="editorial-critique-provider-failed",
            ),
        )

    def _try_attempt(
        self,
        *,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        candidate: dict[str, Any],
        draft_artifact: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        deterministic_report: dict[str, Any],
        llm_validation_report: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        candidate_id = str(candidate.get("id") or "unknown-candidate")
        selection = selection_for_attempt(role=DraftModelRole.CRITIC, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        context_pack = self._attempts.critic_context_pack(draft_artifact, material_plan, rule_pack, context_artifact)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup, **selection.to_payload()}
        budget_input = self._payload_budget_runtime.compact(
            "editorialCritique",
            {
                "candidate": candidate,
                "draft_artifact": draft_artifact,
                "context_artifact": context_artifact,
                "rule_pack": rule_pack,
                "material_plan": material_plan,
                "deterministic_report": deterministic_report,
                "llm_validation_report": llm_validation_report,
            },
            execution_mode=self._settings.draft_run_execution_mode,
            model=attempt.model,
            model_role=DraftModelRole.CRITIC.value,
        )
        compact_payload = budget_input.payload
        messages = self._prompts.build_messages(
            candidate=compact_payload["candidate"],
            context_artifact=compact_payload["context_artifact"],
            rule_pack=compact_payload["rule_pack"],
            material_plan=compact_payload.get("material_plan", {}),
            deterministic_report=compact_payload.get("deterministic_report", deterministic_report),
            llm_validation_report=compact_payload.get("llm_validation_report", llm_validation_report),
            context_pack=context_pack,
            repair_context=repair_context if attempt.repair else None,
        )
        request_payload = self._traces.request_trace(
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            messages=messages,
            candidate_id=candidate_id,
            attempt=attempt_payload,
            context_pack=context_pack,
            model_selection=selection.to_payload(),
            input_stats=budget_input.input_stats,
            payload_stats=budget_input.payload_stats,
        )
        try:
            result = DraftingJsonOperationClient(self._openrouter_adapter).complete(
                settings=self._settings,
                messages=messages,
                expected_keys=EDITORIAL_CRITIQUE_KEYS,
                temperature=EDITORIAL_CRITIQUE_TEMPERATURE,
                model=attempt.model,
            )
            if not isinstance(result.payload.get("findings"), list) or not isinstance(result.payload.get("observations"), list):
                raise ValueError("OpenRouter editorial critique response findings/observations are not lists")
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload=self._traces.result_trace(result_payload=result.payload, provider_response=result.raw_response, attempt=attempt_payload),
                fallback_used=False,
            )
            return {
                "accepted": True,
                "payload": result.payload,
                "attempt": self._attempts.attempt(
                    attempt,
                    candidate_id,
                    "accepted",
                    run.id,
                    selection.to_payload(),
                    input_stats=budget_input.input_stats,
                    payload_stats=budget_input.payload_stats,
                ),
            }
        except Exception as exc:
            return self._attempt_error(attempt, candidate_id, request_payload, self._safe_error(exc))

    def _attempt_error(self, attempt: JsonStepAttempt, candidate_id: str, request_payload: dict[str, Any], error: str) -> dict[str, Any]:
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup}
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload=self._traces.result_trace(result_payload={"summary": "", "findings": [], "observations": []}, provider_response=None, attempt=attempt_payload),
            fallback_used=False,
            error=error,
        )
        selection = {key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}
        return {
            "accepted": False,
            "payload": {},
            "attempt": self._attempts.attempt(
                attempt,
                candidate_id,
                "error",
                run.id,
                selection,
                error,
                input_stats=request_payload.get("inputStats"),
                payload_stats=request_payload.get("payloadStats"),
            ),
        }

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"

def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
