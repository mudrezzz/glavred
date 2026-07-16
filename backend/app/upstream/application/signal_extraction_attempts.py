"""Owner: upstream.application

Used by: SignalExtractionService for one budgeted primary, repair, or backup attempt.
Does not own: retry order, material terminal coverage, project scoring, or RadarRun orchestration.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfile
from backend.app.upstream.application.signal_extraction_attempt_request import SignalExtractionAttemptRequestBuilder
from backend.app.upstream.application.signal_extraction_context import SignalExtractionDossier
from backend.app.upstream.application.signal_deduplication import SignalDeduplicationPolicy
from backend.app.upstream.application.signal_extraction_provider import SignalExtractionProvider
from backend.app.upstream.application.signal_extraction_validation import SignalExtractionPayloadError, SignalExtractionPayloadMapper
from backend.app.upstream.domain.signal_extraction_contracts import ExtractedSourceSignal, MaterialDecisionRecord


@dataclass(frozen=True)
class SignalExtractionAttemptResult:
    accepted: bool
    attempt: dict[str, Any]
    signals: tuple[ExtractedSourceSignal, ...] = ()
    decisions: tuple[MaterialDecisionRecord, ...] = ()
    grounding_violations: tuple[dict[str, Any], ...] = ()
    errors: tuple[str, ...] = ()


class SignalExtractionAttemptRunner:
    def __init__(
        self,
        *,
        provider: SignalExtractionProvider,
        ai_run_service: AiRunService,
        mapper: SignalExtractionPayloadMapper | None = None,
        dedupe: SignalDeduplicationPolicy | None = None,
    ) -> None:
        self._provider = provider
        self._ai_runs = ai_run_service
        self._mapper = mapper or SignalExtractionPayloadMapper()
        self._dedupe = dedupe or SignalDeduplicationPolicy()
        self._requests = SignalExtractionAttemptRequestBuilder()

    def run(
        self,
        *,
        dossier: SignalExtractionDossier,
        profile: UpstreamProviderBudgetProfile,
        label: str,
        model: str,
        radar_id: str,
        run_id: str,
        repair_errors: list[str],
    ) -> SignalExtractionAttemptResult:
        request = self._requests.build(
            dossier=dossier,
            profile=profile,
            label=label,
            model=model,
            repair_errors=repair_errors,
        )
        if request.blocked_reason:
            ai_run = self._ai_runs.create_failed_run(
                capability=AiRunCapability.SIGNAL_EXTRACTION,
                provider=AiRunProvider.OPENROUTER,
                model=model,
                request_payload=request.fields,
                error=request.blocked_reason,
            )
            return SignalExtractionAttemptResult(
                accepted=False,
                attempt=self._trace(label, model, ai_run.id, "blocked", request.fields, error=request.blocked_reason),
                errors=(request.blocked_reason,),
            )
        provider_result = None
        try:
            provider_result = self._provider.complete(
                messages=request.messages,
                model=model,
                max_output_tokens=profile.max_output_tokens,
            )
            signals, decisions, violations = self._mapper.map(
                payload=provider_result.payload,
                dossier=dossier,
                radar_id=radar_id,
                run_id=run_id,
            )
            signals = self._dedupe.apply(signals)
            result_payload = {
                "accepted": True,
                "signalCount": len(signals),
                "materialDecisionCount": len(decisions),
                "providerUsage": provider_result.usage,
                "providerUsageStatus": "available" if provider_result.usage is not None else "unavailable",
                "providerRequestId": provider_result.request_id,
            }
            ai_run = self._ai_runs.create_completed_run(
                capability=AiRunCapability.SIGNAL_EXTRACTION,
                provider=AiRunProvider.OPENROUTER,
                model=provider_result.model or model,
                request_payload=request.fields,
                result_payload=result_payload,
                fallback_used=label == "backup",
            )
            attempt = self._trace(label, model, ai_run.id, "accepted", request.fields)
            attempt.update(
                {
                    "providerUsage": provider_result.usage,
                    "providerUsageStatus": result_payload["providerUsageStatus"],
                    "providerRequestId": provider_result.request_id,
                }
            )
            return SignalExtractionAttemptResult(
                accepted=True,
                attempt=attempt,
                signals=tuple(signals),
                decisions=tuple(decisions),
                grounding_violations=tuple(violations),
            )
        except SignalExtractionPayloadError as exc:
            errors = list(exc.errors)
            violations = list(exc.grounding_violations)
            error = f"schema-or-grounding-failure:{';'.join(errors)[:800]}"
        except Exception as exc:
            errors = [f"{exc.__class__.__name__}:{str(exc)[:500]}"]
            violations = []
            error = f"provider-failure:{errors[0]}"
        failure_payload = {
            "validationErrors": errors,
            "providerUsage": provider_result.usage if provider_result else None,
            "providerUsageStatus": "available" if provider_result and provider_result.usage is not None else "unavailable",
            "providerRequestId": provider_result.request_id if provider_result else None,
        }
        ai_run = self._ai_runs.create_failed_run(
            capability=AiRunCapability.SIGNAL_EXTRACTION,
            provider=AiRunProvider.OPENROUTER,
            model=model,
            request_payload=request.fields,
            error=error,
            result_payload=failure_payload,
        )
        attempt_trace = self._trace(label, model, ai_run.id, "failed", request.fields, error=error)
        attempt_trace.update(
            {
                "providerUsage": failure_payload["providerUsage"],
                "providerUsageStatus": failure_payload["providerUsageStatus"],
                "providerRequestId": failure_payload["providerRequestId"],
            }
        )
        return SignalExtractionAttemptResult(
            accepted=False,
            attempt=attempt_trace,
            grounding_violations=tuple(violations),
            errors=tuple(errors),
        )

    def _trace(
        self,
        label: str,
        model: str,
        ai_run_id: str,
        status: str,
        fields: dict[str, Any],
        *,
        error: str | None = None,
    ) -> dict[str, Any]:
        return {
            "attemptLabel": label,
            "model": model,
            "status": status,
            "aiRunId": ai_run_id,
            "payloadBudget": fields.get("payloadBudget"),
            "messageCharCount": fields.get("messageCharCount"),
            "repairContextCharCount": fields.get("repairContextCharCount", 0),
            **({"error": error} if error else {}),
        }


__all__ = ("SignalExtractionAttemptResult", "SignalExtractionAttemptRunner")
