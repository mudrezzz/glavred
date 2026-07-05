"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from time import perf_counter
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.evidence.deterministic_evidence_interpretation import DeterministicEvidenceInterpretationService
from backend.app.drafting.application.operations.json_step_adapter import OpenRouterJsonStepAdapter
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, selection_for_attempt, unconfigured_model_selection
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.drafting.application.evidence.evidence_interpretation_audit import (
    build_evidence_interpretation_request_trace,
    build_evidence_interpretation_result_trace,
)
from backend.app.drafting.application.evidence.evidence_interpretation_prompts import (
    EVIDENCE_INTERPRETATION_KEYS,
    EVIDENCE_INTERPRETATION_TEMPERATURE,
    build_evidence_interpretation_messages,
)
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.drafting.application.operations.evidence_interpretation_payload import EvidenceInterpretationPayloadCompactor
from backend.app.drafting.application.operations.timeout import OperationTimeoutError, TimedOperationRunner
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_evidence_interpretation import evidence_interpretation_from_payload
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.shared.llm_operations import LlmOperationIncidentType, LlmOperationTimeoutProfile, build_operation_envelope, incident_from_safe_error
from backend.app.settings import BackendSettings
from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient


class EvidenceInterpretationService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: OpenRouterJsonStepAdapter,
        deterministic_service: DeterministicEvidenceInterpretationService | None = None,
        timeout_runner: TimedOperationRunner | None = None,
        payload_compactor: EvidenceInterpretationPayloadCompactor | None = None,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._deterministic_service = deterministic_service or DeterministicEvidenceInterpretationService()
        self._timeout_runner = timeout_runner or TimedOperationRunner()
        self._payload_compactor = payload_compactor or EvidenceInterpretationPayloadCompactor()

    def create(
        self,
        *,
        context_summary: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        context_pack: dict[str, Any] | None = None,
        progress: DraftRunStepOperationSink | None = None,
    ) -> DraftPlanningStepResult:
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return self._fallback(
                context_summary=context_summary,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                context_pack=context_pack,
                attempts=[],
                provider=AiRunProvider.DETERMINISTIC,
                model=None,
                error="OpenRouter is not configured",
            )

        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.STRATEGY)
        for attempt in build_json_step_attempts(
            primary_model=primary_selection.model or self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(
                attempt=attempt,
                primary_selection=primary_selection,
                context_summary=context_summary,
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                context_pack=context_pack,
                repair_context=repair_context,
                progress=progress,
            )
            attempts.append(result["attempt"])
            if result["accepted"]:
                return DraftPlanningStepResult(
                    artifact_payload=self._artifact("openrouter", result["payload"], result["aiRunId"], False, attempts=attempts),
                    ai_run_id=result["aiRunId"],
                    ai_run_ids=[str(item["aiRunId"]) for item in attempts if item.get("aiRunId")],
                )
            repair_context = {"previousAttempt": result["attempt"], "requiredShape": "EvidenceInterpretation with at least one useful item or warning"}

        return self._fallback(
            context_summary=context_summary,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            context_pack=context_pack,
            attempts=attempts,
            provider=AiRunProvider.OPENROUTER,
            model=primary_selection.model,
            error="EvidenceInterpretation JSON generation failed after all LLM attempts",
        )

    def _try_attempt(
        self,
        *,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        context_summary: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        context_pack: dict[str, Any] | None,
        repair_context: dict[str, Any] | None,
        progress: DraftRunStepOperationSink | None,
    ) -> dict[str, Any]:
        timeout_seconds = max(0.001, float(self._settings.draft_evidence_interpretation_timeout_seconds or 75))
        selection = selection_for_attempt(role=DraftModelRole.STRATEGY, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup, **selection.to_payload()}
        operation_id = f"evidence-interpretation-{attempt.label}"
        if progress:
            progress.start_operation(
                operation_id,
                kind="evidenceInterpretation",
                label=f"Evidence interpretation {attempt.label}",
                target=attempt.model,
                notes=["Interpreting accepted public/internal evidence before material planning."],
            )
        timings: dict[str, int] = {}
        request_payload: dict[str, Any] = {
            "draftRunStep": "evidenceInterpretation",
            "requestSummary": {"title": _get(context_summary, "brief", "title")},
            "attempt": attempt_payload,
            **selection.to_payload(),
        }
        try:
            build_start = perf_counter()
            compact_input = self._payload_compactor.compact(
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                timeout_seconds=timeout_seconds,
                execution_mode=self._settings.draft_run_execution_mode,
            )
            messages = build_evidence_interpretation_messages(
                context_summary=context_summary,
                context_artifact=compact_input.context_artifact,
                rule_pack=compact_input.rule_pack,
                context_pack=context_pack,
                repair_context=repair_context if attempt.repair else None,
            )
            compact_input.input_stats["selectedModel"] = attempt.model
            request_payload = build_evidence_interpretation_request_trace(
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                messages=messages,
                context_summary=context_summary,
                context_artifact=compact_input.context_artifact,
                rule_pack=compact_input.rule_pack,
                context_pack=context_pack,
                attempt=attempt_payload,
                model_selection=selection.to_payload(),
                input_stats=compact_input.input_stats,
                payload_stats=compact_input.payload_stats,
            )
            request_payload["payloadBudget"] = compact_input.payload_stats.get("payloadBudget")
            timings["buildPromptMs"] = _elapsed_ms(build_start)

            def provider_operation() -> tuple[dict[str, Any], dict[str, Any] | None, int, int]:
                provider_start = perf_counter()
                provider_result = DraftingJsonOperationClient(self._openrouter_adapter).complete(
                    settings=self._settings,
                    messages=messages,
                    expected_keys=EVIDENCE_INTERPRETATION_KEYS,
                    temperature=EVIDENCE_INTERPRETATION_TEMPERATURE,
                    model=attempt.model,
                )
                provider_ms = _elapsed_ms(provider_start)
                validation_start = perf_counter()
                normalized_payload = evidence_interpretation_from_payload(provider_result.payload).to_payload()
                if not _has_interpretation_signal(normalized_payload):
                    raise ValueError("OpenRouter returned empty evidence interpretation")
                return normalized_payload, provider_result.raw_response, provider_ms, _elapsed_ms(validation_start)

            timed_result = self._timeout_runner.run(provider_operation, timeout_seconds=timeout_seconds)
            payload, raw_response, provider_ms, validation_ms = timed_result.value
            timings["providerRequestMs"] = provider_ms
            timings["jsonParseAndShapeValidationMs"] = validation_ms
            timings["timeoutEnvelopeMs"] = timed_result.elapsed_ms

            persist_start = perf_counter()
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload=build_evidence_interpretation_result_trace(
                    result_payload=payload,
                    provider_response=raw_response,
                    attempt=attempt_payload,
                ),
                fallback_used=False,
            )
            timings["aiRunPersistMs"] = _elapsed_ms(persist_start)
            if progress:
                progress.complete_operation(operation_id, ai_run_id=run.id, notes=["Evidence interpretation accepted.", *_timing_notes(timings)])
            return {
                "accepted": True,
                "payload": payload,
                "aiRunId": run.id,
                "attempt": _attempt_record(
                    attempt,
                    run.id,
                    "accepted",
                    selection.to_payload(),
                    input_stats=compact_input.input_stats,
                    payload_stats=compact_input.payload_stats,
                    timings=timings,
                ),
            }
        except Exception as exc:
            status = "timeout" if isinstance(exc, OperationTimeoutError) else "error"
            result = self._record_attempt_error(attempt, request_payload, self._safe_error(exc), status=status, timings=timings)
            if progress:
                progress.fail_operation(
                    operation_id,
                    result["attempt"].get("error") or "Evidence interpretation attempt failed.",
                    ai_run_id=result["aiRunId"],
                    notes=_timing_notes(timings),
                )
            return result

    def _record_attempt_error(
        self,
        attempt: JsonStepAttempt,
        request_payload: dict[str, Any],
        error: str,
        *,
        status: str = "error",
        timings: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            request_payload=request_payload,
            result_payload=build_evidence_interpretation_result_trace(result_payload={}, provider_response=None, attempt=request_payload.get("attempt")),
            fallback_used=False,
            error=error,
        )
        model_selection = {key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}
        return {
            "accepted": False,
            "payload": {},
            "aiRunId": run.id,
            "attempt": _attempt_record(
                attempt,
                run.id,
                status,
                model_selection,
                error,
                input_stats=request_payload.get("inputStats"),
                payload_stats=request_payload.get("payloadStats"),
                timings=timings,
            ),
        }

    def _fallback(
        self,
        *,
        context_summary: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        context_pack: dict[str, Any] | None,
        attempts: list[dict[str, Any]],
        provider: AiRunProvider,
        model: str | None,
        error: str,
    ) -> DraftPlanningStepResult:
        payload = self._deterministic_service.interpret(context_artifact=context_artifact, rule_pack=rule_pack).to_payload()
        selection = unconfigured_model_selection(DraftModelRole.STRATEGY) if model is None else select_model_for_role(self._settings, DraftModelRole.STRATEGY)
        request_payload = build_evidence_interpretation_request_trace(
            provider=provider,
            model=model,
            messages=[],
            context_summary=context_summary,
            context_artifact=context_artifact,
            rule_pack=rule_pack,
            context_pack=context_pack,
            attempt={"label": "deterministic-fallback", "model": model or "deterministic", "repair": False, "backup": False},
            model_selection=selection.to_payload(),
            input_stats={},
            payload_stats={},
        )
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=provider,
            model=model,
            request_payload=request_payload,
            result_payload=build_evidence_interpretation_result_trace(result_payload=payload, provider_response=None, fallback="deterministic"),
            fallback_used=True,
            error=error,
        )
        fallback_attempt = {
            "label": "deterministic-fallback",
            "model": model or "deterministic",
            "status": "fallback",
            "aiRunId": run.id,
            "backup": False,
            **selection.to_payload(),
            "incident": incident_from_safe_error(
                safe_error=error,
                probable_cause="deterministic-fallback",
                incident_type=LlmOperationIncidentType.DETERMINISTIC_FALLBACK,
                provider=provider.value,
                model=model,
                attempt_label="deterministic-fallback",
            ).to_payload(),
        }
        return DraftPlanningStepResult(
            artifact_payload=self._artifact("deterministicFallback", payload, run.id, True, error=error, attempts=[*attempts, fallback_attempt]),
            ai_run_id=run.id,
            ai_run_ids=[str(item["aiRunId"]) for item in attempts if item.get("aiRunId")] + [run.id],
        )

    def _artifact(self, source: str, payload: dict[str, Any], ai_run_id: str, fallback_used: bool, *, attempts: list[dict[str, Any]], error: str | None = None) -> dict[str, Any]:
        status = "fallback" if fallback_used else "accepted"
        timeout_seconds = max(0.001, float(self._settings.draft_evidence_interpretation_timeout_seconds or 75))
        artifact = {"source": source, "aiRunId": ai_run_id, "fallbackUsed": fallback_used, "evidenceInterpretation": payload, "attempts": attempts}
        artifact["operationEnvelope"] = build_operation_envelope(
            operation_id="evidenceInterpretation",
            operation_kind="evidenceInterpretation",
            owner="backend.app.drafting.application.evidence.evidence_interpretation_service",
            status=status,
            attempts=attempts,
            result_payload=payload,
            safe_error=error,
            failure_reason=error,
            provider=AiRunProvider.DETERMINISTIC.value if fallback_used else AiRunProvider.OPENROUTER.value,
            model=_last_model(attempts),
            timeout_profile=LlmOperationTimeoutProfile(
                profile="evidence-interpretation-provider-attempt",
                attempt_timeout_seconds=timeout_seconds,
            ),
            input_stats=_last_input_stats(attempts),
            payload_stats=_last_payload_stats(attempts),
        )
        if error:
            artifact["error"] = error
        return artifact

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"


def _get(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for key in path:
        current = current.get(key) if isinstance(current, dict) else None
    return current


def _elapsed_ms(start: float) -> int:
    return int((perf_counter() - start) * 1000)


def _timing_notes(timings: dict[str, int] | None) -> list[str]:
    if not timings:
        return []
    return [f"{key}={value}ms" for key, value in timings.items()]


def _has_interpretation_signal(payload: dict[str, Any]) -> bool:
    return any(payload.get(key) for key in ("implications", "tensions", "usableExamples", "limits", "forbiddenOverclaims", "rejectedEvidenceUses", "warnings"))


def _attempt_record(
    attempt: JsonStepAttempt,
    ai_run_id: str,
    status: str,
    model_selection: dict[str, Any],
    error: str | None = None,
    *,
    input_stats: dict[str, Any] | None = None,
    payload_stats: dict[str, Any] | None = None,
    timings: dict[str, int] | None = None,
) -> dict[str, Any]:
    record = {"label": attempt.label, "model": attempt.model, "status": status, "aiRunId": ai_run_id, "backup": attempt.backup, **model_selection}
    if input_stats:
        record["inputStats"] = input_stats
    if payload_stats:
        record["payloadStats"] = payload_stats
    if timings:
        record["timings"] = timings
    if error:
        record["error"] = error
        record["incident"] = incident_from_safe_error(
            safe_error=error,
            probable_cause=status,
            provider=AiRunProvider.OPENROUTER.value if status != "fallback" else AiRunProvider.DETERMINISTIC.value,
            model=attempt.model,
            attempt_label=attempt.label,
        ).to_payload()
    return record


def _last_model(attempts: list[dict[str, Any]]) -> str | None:
    return next((str(item.get("model")) for item in reversed(attempts) if item.get("model")), None)


def _last_input_stats(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    return next((dict(item.get("inputStats")) for item in reversed(attempts) if isinstance(item.get("inputStats"), dict)), {})


def _last_payload_stats(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    return next((dict(item.get("payloadStats")) for item in reversed(attempts) if isinstance(item.get("payloadStats"), dict)), {})


__all__ = (
    'EvidenceInterpretationService',
)
