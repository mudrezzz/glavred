"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.revision.draft_directed_revision_prompts import (
    DIRECTED_REVISION_KEYS,
    DirectedRevisionPromptBuilder,
)
from backend.app.drafting.application.revision.draft_revision_dossier_attempt import RevisionDossierAttemptBuilder
from backend.app.drafting.application.generation.draft_generation_params import GenerationParamProfile, generation_params_for_attempt
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, selection_for_attempt
from backend.app.drafting.application.operations.draft_provider_error_utils import raw_response_excerpt, safe_provider_error
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.drafting.application.operations.payload_budget_runtime import PayloadBudgetAttemptStatsExtractor
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.shared.llm_operations.legacy_payloads import legacy_attempt_record, legacy_not_run_result, legacy_operation_envelope
from backend.app.settings import BackendSettings
from backend.app.drafting.domain.provider_dossier import DossierReadinessStatus, ProviderDossier
from backend.app.drafting.application.dossiers.provider_dossier_context_snapshot import ProviderDossierContextSnapshotFactory
from backend.app.drafting.application.dossiers.provider_dossier_factories import RevisionDossierFactory

OPERATION_META = {"operation_id": "directedRevision", "operation_kind": "writerRevision", "owner": "backend.app.drafting.application.revision.draft_directed_revision_service", "model_role": DraftModelRole.WRITER.value}


class DraftDirectedRevisionService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: Any,
        prompt_builder: DirectedRevisionPromptBuilder | None = None,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._attempt_stats = PayloadBudgetAttemptStatsExtractor()
        self._prompt_builder = prompt_builder or DirectedRevisionPromptBuilder()
        self._attempt_builder = RevisionDossierAttemptBuilder(prompt_builder=self._prompt_builder)

    def revise(
        self,
        *,
        candidate: dict[str, Any] | None,
        instruction: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        provider_dossier: ProviderDossier | None = None,
    ) -> dict[str, Any]:
        if not candidate:
            return legacy_not_run_result("candidate-not-found", **OPERATION_META)
        if instruction.get("status") != "created":
            return legacy_not_run_result(str(instruction.get("reason") or "no-actionable-findings"), **OPERATION_META)
        status = self._openrouter_validator.evaluate(self._settings)
        if not status.configured:
            return legacy_not_run_result("provider-unconfigured", safe_error="OpenRouter is not configured", **OPERATION_META)
        if provider_dossier is None:
            access = ProviderDossierContextSnapshotFactory().access(
                draft_artifact={"candidates": [candidate]},
                context_artifact=context_artifact,
                rule_pack=rule_pack,
                material_plan=material_plan,
                review_context={
                    "currentCandidate": candidate,
                    "validationReport": {},
                    "revisionInstruction": instruction,
                },
            )
            provider_dossier = RevisionDossierFactory(access).build(candidate_id=str(candidate.get("id") or ""))
        if provider_dossier is None or provider_dossier.readiness_status is DossierReadinessStatus.BLOCKED:
            reason = "dossier-context-unavailable" if provider_dossier is None else "revision-dossier-blocked"
            result = legacy_not_run_result(reason, safe_error=reason, **OPERATION_META)
            result.update({"dossierBlocked": True, "providerDossier": provider_dossier.to_payload() if provider_dossier else None})
            return result
        attempts: list[dict[str, Any]] = []
        repair_context: dict[str, Any] | None = None
        primary_selection = select_model_for_role(self._settings, DraftModelRole.WRITER)
        for attempt in build_json_step_attempts(
            primary_model=primary_selection.model or self._settings.openrouter_default_model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(
                attempt, primary_selection, provider_dossier, repair_context
            )
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
                return {
                    "status": "succeeded",
                    "revisedCandidate": revised,
                    "attempts": attempts,
                    "aiRunIds": [str(item["aiRunId"]) for item in attempts if item.get("aiRunId")],
                    "operationEnvelope": legacy_operation_envelope(
                        "accepted",
                        attempts,
                        payload=revised,
                        input_stats=self._attempt_stats.last_input_stats(attempts),
                        payload_stats=self._attempt_stats.last_payload_stats(attempts),
                        **OPERATION_META,
                    ),
                }
            repair_context = {"previousAttempt": result["attempt"], "requiredShape": "title, body, changeLog[]"}
        last_error = next((str(item.get("validation")) for item in reversed(attempts) if item.get("validation")), None)
        return {
            "status": "failed",
            "reason": "directed-revision-provider-failed",
            "error": last_error,
            "attempts": attempts,
            "aiRunIds": [str(item["aiRunId"]) for item in attempts if item.get("aiRunId")],
            "operationEnvelope": legacy_operation_envelope(
                "failed",
                attempts,
                safe_error=last_error,
                failure_reason="directed-revision-provider-failed",
                input_stats=self._attempt_stats.last_input_stats(attempts),
                payload_stats=self._attempt_stats.last_payload_stats(attempts),
                **OPERATION_META,
            ),
        }

    def _try_attempt(self, attempt: JsonStepAttempt, primary_selection: Any, provider_dossier: ProviderDossier, repair_context: dict[str, Any] | None) -> dict[str, Any]:
        selection = selection_for_attempt(role=DraftModelRole.WRITER, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        generation_params = generation_params_for_attempt(self._settings, primary_profile=GenerationParamProfile.REVISION, attempt=attempt)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup, **selection.to_payload()}
        prepared = self._attempt_builder.prepare(
            dossier=provider_dossier,
            model=attempt.model,
            attempt=attempt_payload,
            model_selection=selection.to_payload(),
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
                expected_keys=DIRECTED_REVISION_KEYS,
                temperature=generation_params.temperature,
                top_p=generation_params.top_p,
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
            return {
                "accepted": True,
                "payload": result.payload,
                "attempt": legacy_attempt_record(
                    attempt,
                    run.id,
                    "accepted",
                    selection.to_payload(),
                    input_stats=request_payload.get("inputStats"),
                    payload_stats=request_payload.get("payloadStats"),
                    generation_params=generation_params.to_payload(),
                ),
            }
        except Exception as exc:
            return self._attempt_error(attempt, request_payload, safe_provider_error(self._settings, exc), raw_response_excerpt(exc))

    def _attempt_error(self, attempt: JsonStepAttempt, request_payload: dict[str, Any], error: str, raw_response_excerpt: str | None = None) -> dict[str, Any]:
        result_payload: dict[str, Any] = {"draftRunStep": "directedRevision", "attempt": {"label": attempt.label, "model": attempt.model}, "result": {}}
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
        return {
            "accepted": False,
            "payload": {},
            "attempt": legacy_attempt_record(
                attempt,
                run.id,
                "error",
                selection,
                error,
                input_stats=request_payload.get("inputStats"),
                payload_stats=request_payload.get("payloadStats"),
                generation_params=request_payload.get("generationParams"),
            ),
        }


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in value if str(item).strip()] if isinstance(value, list) else []
