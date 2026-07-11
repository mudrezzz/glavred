"""Owner: drafting.application.generation

Used by: DraftRun generation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.generation.deterministic_draft_candidate_service import DeterministicDraftCandidateService
from backend.app.drafting.application.generation.draft_candidate_audit import build_candidate_result_trace
from backend.app.drafting.application.generation.draft_candidate_prompts import CANDIDATE_KEYS
from backend.app.drafting.application.generation.draft_generation_params import GenerationParamProfile, generation_params_for_attempt, generation_params_for_profile
from backend.app.drafting.application.generation.draft_writer_dossier_attempt import WriterDossierAttemptBuilder
from backend.app.drafting.application.generation.draft_candidate_attempt_records import CandidateAttemptRecordComponent
from backend.app.drafting.application.operations.draft_provider_error_utils import DraftProviderErrorUtilsComponent
from backend.app.drafting.application.operations.json_step_adapter import OpenRouterJsonStepAdapter
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, selection_for_attempt, unconfigured_model_selection
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_candidates import DraftCandidate, DraftCandidateDirection, candidate_from_payload
from backend.app.domain.draft_generation import DraftGenerationRequest
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings
from backend.app.drafting.domain.provider_dossier import DossierReadinessStatus, ProviderDossier


class DraftCandidateProviderService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: OpenRouterJsonStepAdapter,
        deterministic_candidate_service: DeterministicDraftCandidateService,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._deterministic_candidate_service = deterministic_candidate_service
        self._attempt_builder = WriterDossierAttemptBuilder()

    def create_one(
        self,
        *,
        request: DraftGenerationRequest,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        direction: DraftCandidateDirection,
        provider_dossier: ProviderDossier,
        context_pack: dict[str, Any] | None,
    ) -> tuple[dict[str, Any], list[str]]:
        status = self._openrouter_validator.evaluate(self._settings)
        provider = AiRunProvider.OPENROUTER if status.configured else AiRunProvider.DETERMINISTIC
        primary_selection = select_model_for_role(self._settings, DraftModelRole.WRITER) if status.configured else unconfigured_model_selection(DraftModelRole.WRITER)
        if provider_dossier.readiness_status is DossierReadinessStatus.BLOCKED:
            request_payload = self._request_payload(provider, primary_selection.model, context_summary, direction, provider_dossier, primary_selection.to_payload())
            request_payload["dossierBlocked"] = True
            payload, ai_run_id = self._fallback(request, direction, rule_pack, material_plan, request_payload, provider, primary_selection.model, "writer-dossier-blocked")
            return payload, [ai_run_id] if ai_run_id else []
        if not status.configured:
            request_payload = self._request_payload(provider, primary_selection.model, context_summary, direction, provider_dossier, primary_selection.to_payload())
            payload, ai_run_id = self._fallback(request, direction, rule_pack, material_plan, request_payload, provider, primary_selection.model, "OpenRouter is not configured")
            return payload, [ai_run_id] if ai_run_id else []

        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        for attempt in build_json_step_attempts(primary_model=primary_selection.model or self._settings.openrouter_default_model, backup_model=self._settings.openrouter_backup_model_or_none):
            result = self._try_attempt(
                attempt=attempt,
                primary_selection=primary_selection,
                request=request,
                context_summary=context_summary,
                rule_pack=rule_pack,
                material_plan=material_plan,
                draft_strategy=draft_strategy,
                direction=direction,
                provider_dossier=provider_dossier,
                repair_context=repair_context,
            )
            attempts.append(result["attempt"])
            if result["accepted"]:
                return result["candidate"], CandidateAttemptRecordComponent.ai_run_ids(attempts)
            repair_context = {"previousAttempt": result["attempt"], "requiredShape": "title, body, rationale, usedEvidence, ruleCoverage, risks, weaknesses"}

        request_payload = self._request_payload(AiRunProvider.OPENROUTER, primary_selection.model, context_summary, direction, provider_dossier, primary_selection.to_payload())
        payload, ai_run_id = self._fallback(request, direction, rule_pack, material_plan, {**request_payload, "attempts": attempts}, AiRunProvider.OPENROUTER, primary_selection.model, CandidateAttemptRecordComponent.last_error(attempts) or "Draft candidate JSON generation failed after all attempts")
        return payload, [*CandidateAttemptRecordComponent.ai_run_ids(attempts), *([ai_run_id] if ai_run_id else [])]

    def _try_attempt(
        self,
        *,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        request: DraftGenerationRequest,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
        direction: DraftCandidateDirection,
        provider_dossier: ProviderDossier,
        repair_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(role=DraftModelRole.WRITER, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        generation_params = generation_params_for_attempt(self._settings, primary_profile=GenerationParamProfile.WRITER, attempt=attempt)
        prepared = self._attempt_builder.prepare(
            operation_id="draftCandidate",
            draft_run_step="draftCandidate",
            dossier=provider_dossier,
            context_summary=context_summary,
            direction=direction,
            provider=AiRunProvider.OPENROUTER,
            model=attempt.model,
            model_role=DraftModelRole.WRITER.value,
            model_selection=selection.to_payload(),
            attempt={"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup},
            generation_params=generation_params.to_payload(),
            execution_mode=self._settings.draft_run_execution_mode,
            repair_context=repair_context if attempt.repair else None,
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
            candidate = candidate_from_payload(f"candidate-{direction.id}-{request.brief.id}", direction, result.payload)
            if not candidate.body.strip():
                raise ValueError("OpenRouter draft candidate body is empty")
            payload, ai_run_id = self._complete_candidate(candidate, "openrouter", request_payload, result.raw_response, attempt.model, False, None, model_selection=selection.to_payload())
            return {"accepted": True, "candidate": payload, "attempt": CandidateAttemptRecordComponent.record(attempt, ai_run_id, "accepted", selection.to_payload())}
        except Exception as exc:
            return self._attempt_error(attempt, request_payload, DraftProviderErrorUtilsComponent.safe_provider_error(self._settings, exc), DraftProviderErrorUtilsComponent.raw_response_excerpt(exc))

    def _request_payload(self, provider: AiRunProvider, model: str | None, context_summary: dict[str, Any], direction: DraftCandidateDirection, provider_dossier: ProviderDossier, model_selection: dict[str, Any]) -> dict[str, Any]:
        prepared = self._attempt_builder.prepare(
            operation_id="draftCandidate",
            draft_run_step="draftCandidate",
            dossier=provider_dossier,
            context_summary=context_summary,
            direction=direction,
            provider=provider,
            model=model,
            model_role=DraftModelRole.WRITER.value,
            model_selection=model_selection,
            attempt=None,
            generation_params=generation_params_for_profile(self._settings, GenerationParamProfile.WRITER).to_payload(),
            execution_mode=self._settings.draft_run_execution_mode,
            repair_context=None,
        )
        return prepared.request_payload

    def _attempt_error(self, attempt: JsonStepAttempt, request_payload: dict[str, Any], error: str, raw_response_excerpt: str | None = None) -> dict[str, Any]:
        result_payload = build_candidate_result_trace(candidate_payload={}, provider_response=None, fallback=None)
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
        return {"accepted": False, "candidate": None, "attempt": CandidateAttemptRecordComponent.record(attempt, run.id, "error", selection, error)}

    def _fallback(self, request: DraftGenerationRequest, direction: DraftCandidateDirection, rule_pack: dict[str, Any], material_plan: dict[str, Any], request_payload: dict[str, Any], provider: AiRunProvider, model: str | None, error: str) -> tuple[dict[str, Any], str | None]:
        candidate = self._deterministic_candidate_service.create_candidate(request=request, direction=direction, rule_pack=rule_pack, material_plan=material_plan)
        model_selection = {key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}
        return self._complete_candidate(candidate, "deterministicFallback", request_payload, None, model, True, error, provider=provider, model_selection=model_selection)

    def _complete_candidate(
        self,
        candidate: DraftCandidate,
        source: str,
        request_payload: dict[str, Any],
        provider_response: dict[str, Any] | None,
        model: str | None,
        fallback_used: bool,
        error: str | None,
        *,
        provider: AiRunProvider = AiRunProvider.OPENROUTER,
        model_selection: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], str]:
        payload = candidate.to_payload(source=source, ai_run_id=None, fallback_used=fallback_used)
        if model_selection:
            payload.update(model_selection)
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=provider,
            model=model,
            request_payload=request_payload,
            result_payload=build_candidate_result_trace(candidate_payload=payload, provider_response=provider_response, fallback="deterministic" if fallback_used else None),
            fallback_used=fallback_used,
            error=error,
        )
        final_payload = candidate.to_payload(source=source, ai_run_id=run.id, fallback_used=fallback_used)
        if model_selection:
            final_payload.update(model_selection)
        return final_payload, run.id
