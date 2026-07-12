"""Owner: drafting.application.final_quality

Used by: DraftRun final_quality package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.final_quality.draft_final_quality_review_parser import FinalQualityReviewParser
from backend.app.drafting.application.final_quality.draft_final_quality_review_prompts import (
    FINAL_QUALITY_REVIEW_KEYS,
    FINAL_QUALITY_REVIEW_TEMPERATURE,
    FinalQualityReviewPromptBuilder,
)
from backend.app.drafting.application.final_quality.draft_final_quality_dossier_attempt import FinalQualityDossierAttemptBuilder
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_final_gate, selection_for_attempt
from backend.app.drafting.application.operations.draft_provider_error_utils import raw_response_excerpt, safe_provider_error
from backend.app.application.json_step_retry_policy import JsonStepAttempt, build_json_step_attempts
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings
from backend.app.drafting.domain.provider_dossier import DossierReadinessStatus, ProviderDossier
from backend.app.drafting.application.dossiers.provider_dossier_context_snapshot import ProviderDossierContextSnapshotFactory
from backend.app.drafting.application.dossiers.provider_dossier_factories import FinalQualityDossierFactory


class DraftFinalQualityReviewService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: Any,
        parser: FinalQualityReviewParser | None = None,
        prompt_builder: FinalQualityReviewPromptBuilder | None = None,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._parser = parser or FinalQualityReviewParser()
        self._prompt_builder = prompt_builder or FinalQualityReviewPromptBuilder()
        self._attempt_builder = FinalQualityDossierAttemptBuilder(prompt_builder=self._prompt_builder)

    def review(
        self,
        *,
        candidate: dict[str, Any],
        contract: dict[str, Any],
        deterministic_gate: dict[str, Any],
        validation_report: dict[str, Any],
        provider_dossier: ProviderDossier | None = None,
        repair_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        status = self._openrouter_validator.evaluate(self._settings)
        primary_selection = select_model_for_final_gate(self._settings)
        independence = _model_independence(self._settings, primary_selection.model)
        if provider_dossier is None:
            access = ProviderDossierContextSnapshotFactory().access(
                draft_artifact={"candidates": [candidate]},
                validation_report=validation_report,
                context_artifact={"postContract": contract.get("postContract") or contract},
                review_context={
                    "currentCandidate": candidate,
                    "validationReport": validation_report,
                    "finalQualityContract": contract,
                    "deterministicGate": deterministic_gate,
                },
            )
            provider_dossier = FinalQualityDossierFactory(access).build(candidate_id=str(candidate.get("id") or ""))
        if provider_dossier is None or provider_dossier.readiness_status is DossierReadinessStatus.BLOCKED:
            return {
                "status": "not-run",
                "reason": "dossier-context-unavailable" if provider_dossier is None else "final-quality-dossier-blocked",
                "attempts": [],
                "aiRunIds": [],
                "dossierBlocked": True,
                "providerDossier": provider_dossier.to_payload() if provider_dossier else None,
                "modelIndependence": independence,
                **primary_selection.to_payload(),
            }
        if not status.configured or not primary_selection.model:
            return {
                "status": "not-run",
                "reason": "provider-unconfigured",
                "attempts": [],
                "aiRunIds": [],
                "modelIndependence": independence,
                **primary_selection.to_payload(),
            }
        attempts: list[dict[str, Any]] = []
        repair_attempt_context: dict[str, Any] | None = None
        for attempt in build_json_step_attempts(
            primary_model=primary_selection.model,
            backup_model=self._settings.openrouter_backup_model_or_none,
        ):
            result = self._try_attempt(
                attempt=attempt,
                primary_selection=primary_selection,
                candidate=candidate,
                contract=contract,
                deterministic_gate=deterministic_gate,
                validation_report=validation_report,
                provider_dossier=provider_dossier,
                repair_context=repair_context,
                repair_attempt_context=repair_attempt_context,
                independence=independence,
            )
            attempts.append(result["attempt"])
            if result["accepted"]:
                review = self._parser.normalize(result["payload"], candidate_id=str(candidate.get("id") or "final"))
                return {
                    **review,
                    "attempts": attempts,
                    "aiRunIds": _ai_run_ids(attempts),
                    "modelIndependence": independence,
                    **result["selection"],
                }
            repair_attempt_context = {"previousAttempt": result["attempt"], "requiredShape": "final quality review JSON object"}
        return {
            "status": "not-run",
            "reason": "final-gate-provider-failed",
            "attempts": attempts,
            "aiRunIds": _ai_run_ids(attempts),
            "modelIndependence": independence,
            **primary_selection.to_payload(),
        }

    def _try_attempt(
        self,
        *,
        attempt: JsonStepAttempt,
        primary_selection: Any,
        candidate: dict[str, Any],
        contract: dict[str, Any],
        deterministic_gate: dict[str, Any],
        validation_report: dict[str, Any],
        provider_dossier: ProviderDossier,
        repair_context: dict[str, Any] | None,
        repair_attempt_context: dict[str, Any] | None,
        independence: str,
    ) -> dict[str, Any]:
        selection = selection_for_attempt(role=DraftModelRole.FINAL_GATE, model=attempt.model, backup=attempt.backup, primary_selection=primary_selection)
        attempt_payload = {"label": attempt.label, "model": attempt.model, "repair": attempt.repair, "backup": attempt.backup, **selection.to_payload()}
        prepared = self._attempt_builder.prepare(
            dossier=provider_dossier,
            model=attempt.model,
            attempt=attempt_payload,
            model_selection=selection.to_payload(),
            execution_mode=self._settings.draft_run_execution_mode,
            model_independence=independence,
            repair_context=repair_attempt_context or repair_context if attempt.repair else repair_context,
        )
        messages = prepared.messages
        request_payload = {**prepared.request_payload, "finalQualityContract": contract}
        try:
            result = DraftingJsonOperationClient(self._openrouter_adapter).complete(
                settings=self._settings,
                messages=messages,
                expected_keys=FINAL_QUALITY_REVIEW_KEYS,
                temperature=FINAL_QUALITY_REVIEW_TEMPERATURE,
                model=attempt.model,
            )
            if not isinstance(result.payload.get("findings"), list) or not isinstance(result.payload.get("observations"), list):
                raise ValueError("Final quality review findings/observations are not lists")
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload={"draftRunStep": "finalQualityGateReview", "attempt": attempt_payload, "result": result.payload, "providerResponse": result.raw_response},
                fallback_used=False,
            )
            return {"accepted": True, "payload": result.payload, "selection": selection.to_payload(), "attempt": _attempt_record(attempt, run.id, "accepted", selection.to_payload())}
        except Exception as exc:
            error = safe_provider_error(self._settings, exc)
            result_payload: dict[str, Any] = {"draftRunStep": "finalQualityGateReview", "attempt": attempt_payload, "result": {}}
            excerpt = raw_response_excerpt(exc)
            if excerpt:
                result_payload["rawResponseExcerpt"] = excerpt
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=attempt.model,
                request_payload=request_payload,
                result_payload=result_payload,
                fallback_used=False,
                error=error,
            )
            return {"accepted": False, "payload": {}, "selection": selection.to_payload(), "attempt": _attempt_record(attempt, run.id, "error", selection.to_payload(), error)}


def _model_independence(settings: BackendSettings, gate_model: str | None) -> str:
    writer = settings.draft_writer_model.strip()
    if not gate_model:
        return "unknown"
    return "weak" if writer and writer == gate_model else "independent"


def _attempt_record(attempt: JsonStepAttempt, ai_run_id: str, status: str, model_selection: dict[str, Any], validation: str | None = None) -> dict[str, Any]:
    record = {"label": attempt.label, "model": attempt.model, "status": status, "aiRunId": ai_run_id, "backup": attempt.backup, **model_selection}
    if validation:
        record["validation"] = validation
    return record


def _ai_run_ids(attempts: list[dict[str, Any]]) -> list[str]:
    return [str(attempt["aiRunId"]) for attempt in attempts if attempt.get("aiRunId")]
