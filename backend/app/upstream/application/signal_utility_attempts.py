"""Owner: upstream.application

Used by: SignalUtilityScoringService for one budgeted provider attempt.
Does not own: retry order, recommendation policy, project persistence, or review status.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfile
from backend.app.upstream.application.signal_utility_attempt_request import SignalUtilityAttemptRequestBuilder
from backend.app.upstream.application.signal_utility_payload import SignalUtilityPayloadError, SignalUtilityPayloadMapper
from backend.app.upstream.application.signal_utility_provider import SignalUtilityProvider
from backend.app.upstream.domain.signal_utility import SignalUtilityDimensionResult, SignalUtilityDossier


@dataclass(frozen=True)
class SignalUtilityAttemptResult:
    accepted: bool
    attempt: dict[str, Any]
    evaluations: dict[str, tuple[SignalUtilityDimensionResult, ...]]
    relationships: dict[str, dict[str, str]]
    errors: tuple[str, ...] = ()


class SignalUtilityAttemptRunner:
    def __init__(self, *, provider: SignalUtilityProvider, ai_run_service: AiRunService) -> None:
        self._provider = provider
        self._ai_runs = ai_run_service
        self._requests = SignalUtilityAttemptRequestBuilder()
        self._mapper = SignalUtilityPayloadMapper()

    def run(
        self,
        *,
        dossier: SignalUtilityDossier,
        profile: UpstreamProviderBudgetProfile,
        label: str,
        model: str,
        repair_errors: list[str],
        setting_modes: dict[str, str],
    ) -> SignalUtilityAttemptResult:
        request = self._requests.build(
            dossier=dossier,
            profile=profile,
            label=label,
            model=model,
            repair_errors=repair_errors,
        )
        if request.blocked_reason:
            run = self._ai_runs.create_failed_run(
                capability=AiRunCapability.SIGNAL_SCORING,
                provider=AiRunProvider.OPENROUTER,
                model=model,
                request_payload=request.fields,
                error=request.blocked_reason,
            )
            return SignalUtilityAttemptResult(False, self._trace(label, model, run.id, "blocked", request.fields), {}, {}, (request.blocked_reason,))
        provider_result = None
        try:
            provider_result = self._provider.complete(
                messages=request.messages,
                model=model,
                max_output_tokens=profile.max_output_tokens,
            )
            mapped = self._mapper.map(
                payload=provider_result.payload,
                dossier=dossier,
                setting_modes=setting_modes,
            )
            result_payload = {
                "accepted": True,
                "evaluatedSignalCount": len(mapped.evaluations),
                "relationshipCount": len(mapped.relationships),
                "providerUsage": provider_result.usage,
                "providerUsageStatus": "available" if provider_result.usage is not None else "unavailable",
                "providerRequestId": provider_result.request_id,
            }
            run = self._ai_runs.create_completed_run(
                capability=AiRunCapability.SIGNAL_SCORING,
                provider=AiRunProvider.OPENROUTER,
                model=provider_result.model or model,
                request_payload=request.fields,
                result_payload=result_payload,
                fallback_used=label == "backup",
            )
            trace = self._trace(label, model, run.id, "accepted", request.fields)
            trace.update({"providerUsage": provider_result.usage, "providerUsageStatus": result_payload["providerUsageStatus"]})
            return SignalUtilityAttemptResult(True, trace, mapped.evaluations, mapped.relationships)
        except SignalUtilityPayloadError as exc:
            errors = list(exc.errors)
            error = f"schema-failure:{';'.join(errors)[:800]}"
        except Exception as exc:
            errors = [f"{exc.__class__.__name__}:{str(exc)[:500]}"]
            error = f"provider-failure:{errors[0]}"
        result_payload = {
            "validationErrors": errors,
            "providerUsage": provider_result.usage if provider_result else None,
            "providerUsageStatus": "available" if provider_result and provider_result.usage is not None else "unavailable",
        }
        run = self._ai_runs.create_failed_run(
            capability=AiRunCapability.SIGNAL_SCORING,
            provider=AiRunProvider.OPENROUTER,
            model=model,
            request_payload=request.fields,
            result_payload=result_payload,
            error=error,
        )
        trace = self._trace(label, model, run.id, "failed", request.fields, error=error)
        trace.update({"providerUsage": result_payload["providerUsage"], "providerUsageStatus": result_payload["providerUsageStatus"]})
        return SignalUtilityAttemptResult(False, trace, {}, {}, tuple(errors))

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
            "aiRunId": ai_run_id,
            "status": status,
            "payloadBudget": fields.get("payloadBudget"),
            "messageCharCount": fields.get("messageCharCount"),
            "repairContextCharCount": fields.get("repairContextCharCount", 0),
            **({"error": error} if error else {}),
        }


__all__ = ("SignalUtilityAttemptResult", "SignalUtilityAttemptRunner")
