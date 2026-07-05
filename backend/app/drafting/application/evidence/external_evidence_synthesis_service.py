"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.drafting.application.evidence.deterministic_external_evidence_synthesis import (
    DeterministicExternalEvidenceSynthesisService,
)
from backend.app.drafting.application.operations.json_step_adapter import OpenRouterJsonStepAdapter
from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.drafting.application.operations.draft_model_role_resolver import select_model_for_role, unconfigured_model_selection
from backend.app.drafting.application.evidence.external_evidence_synthesis_prompts import (
    build_external_evidence_synthesis_messages,
)
from backend.app.domain.ai_run import AiRunCapability, AiRunProvider
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.domain.draft_evidence_synthesis import (
    EvidenceSynthesis,
    ExternalEvidenceClaim,
    ExternalEvidenceWarning,
)
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.settings import BackendSettings
from backend.app.drafting.application.operations.json_step_adapter import DraftingJsonOperationClient

SYNTHESIS_KEYS = {"externalClaims", "warnings", "decisions"}
SYNTHESIS_TEMPERATURE = 0.1


class ExternalEvidenceSynthesisService:
    def __init__(
        self,
        *,
        settings: BackendSettings,
        ai_run_service: AiRunService,
        openrouter_validator: OpenRouterConfigValidator,
        openrouter_adapter: OpenRouterJsonStepAdapter,
        deterministic_service: DeterministicExternalEvidenceSynthesisService | None = None,
    ) -> None:
        self._settings = settings
        self._ai_run_service = ai_run_service
        self._openrouter_validator = openrouter_validator
        self._openrouter_adapter = openrouter_adapter
        self._deterministic_service = deterministic_service or DeterministicExternalEvidenceSynthesisService()

    def synthesize(self, *, context_artifact: dict[str, Any], public_evidence: dict[str, Any]) -> DraftPlanningStepResult:
        messages = build_external_evidence_synthesis_messages(context_artifact=context_artifact, public_evidence=public_evidence)
        status = self._openrouter_validator.evaluate(self._settings)
        provider = AiRunProvider.OPENROUTER if status.configured else AiRunProvider.DETERMINISTIC
        selection = select_model_for_role(self._settings, DraftModelRole.RESEARCH) if status.configured else unconfigured_model_selection(DraftModelRole.RESEARCH)
        model = selection.model
        request_payload = {
            "draftRunStep": "externalEvidenceSynthesis",
            "provider": provider.value,
            "model": model,
            "promptMessages": messages,
            "publicEvidenceItemCount": len(_items(public_evidence)),
            **selection.to_payload(),
        }
        if not status.configured:
            return self._fallback(public_evidence, request_payload, provider, model, "OpenRouter is not configured")
        try:
            result = DraftingJsonOperationClient(self._openrouter_adapter).complete(
                settings=self._settings,
                messages=messages,
                expected_keys=SYNTHESIS_KEYS,
                temperature=SYNTHESIS_TEMPERATURE,
                model=model,
            )
            synthesis = _synthesis_from_payload(result.payload, public_evidence, source="openrouter")
            payload = synthesis.to_payload()
            run = self._ai_run_service.create_completed_run(
                capability=AiRunCapability.DRAFT_GENERATION,
                provider=AiRunProvider.OPENROUTER,
                model=model,
                request_payload=request_payload,
                result_payload={
                    "draftRunStep": "externalEvidenceSynthesis",
                    "evidenceSynthesis": payload,
                    "providerResponse": result.raw_response,
                },
                fallback_used=False,
            )
            return DraftPlanningStepResult(artifact_payload={"evidenceSynthesis": payload, "aiRunId": run.id, "fallbackUsed": False, **selection.to_payload()}, ai_run_id=run.id)
        except Exception as exc:
            return self._fallback(public_evidence, request_payload, AiRunProvider.OPENROUTER, model, self._safe_error(exc))

    def _fallback(
        self,
        public_evidence: dict[str, Any],
        request_payload: dict[str, Any],
        provider: AiRunProvider,
        model: str | None,
        error: str,
    ) -> DraftPlanningStepResult:
        payload = self._deterministic_service.synthesize(public_evidence).to_payload()
        run = self._ai_run_service.create_completed_run(
            capability=AiRunCapability.DRAFT_GENERATION,
            provider=provider,
            model=model,
            request_payload=request_payload,
            result_payload={
                "draftRunStep": "externalEvidenceSynthesis",
                "evidenceSynthesis": payload,
                "fallback": "deterministic",
            },
            fallback_used=True,
            error=error,
        )
        return DraftPlanningStepResult(
            artifact_payload={"evidenceSynthesis": payload, "aiRunId": run.id, "fallbackUsed": True, "error": error, **{key: request_payload[key] for key in ("modelRole", "selectedModel", "modelSelectionSource") if key in request_payload}},
            ai_run_id=run.id,
        )

    def _safe_error(self, error: Exception) -> str:
        message = str(error)
        if self._settings.openrouter_api_key:
            token = self._settings.openrouter_api_key.get_secret_value()
            if token:
                message = message.replace(token, "[redacted]")
        return f"{error.__class__.__name__}: {message[:180]}"


def _synthesis_from_payload(payload: dict[str, Any], public_evidence: dict[str, Any], *, source: str) -> EvidenceSynthesis:
    item_ids = {str(item.get("id")) for item in _items(public_evidence) if item.get("id")}
    claims = []
    for item in payload.get("externalClaims") or []:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("publicEvidenceItemId") or "")
        if item_id not in item_ids:
            continue
        claims.append(ExternalEvidenceClaim(
            public_evidence_item_id=item_id,
            statement=str(item.get("statement") or "")[:800],
            allowed_use=_allowed_use(str(item.get("allowedUse") or "needsQualification")),
            confidence=_confidence(str(item.get("confidence") or "medium")),
            decision=str(item.get("decision") or "mergeQualifiedClaim"),
            rationale=str(item.get("rationale") or "Synthesized from accepted public evidence.")[:500],
            risk_flags=[str(flag) for flag in item.get("riskFlags") or [] if flag],
        ))
    warnings = [
        ExternalEvidenceWarning(
            code=str(item.get("code") or "synthesis-warning"),
            message=str(item.get("message") or "")[:500],
            public_evidence_item_id=str(item.get("publicEvidenceItemId")) if item.get("publicEvidenceItemId") else None,
        )
        for item in payload.get("warnings") or []
        if isinstance(item, dict)
    ]
    return EvidenceSynthesis(
        source=source,
        external_claims=claims,
        warnings=warnings,
        decisions=[item for item in payload.get("decisions") or [] if isinstance(item, dict)],
        metadata={"version": "evidence-synthesis-v1", "itemCount": len(item_ids)},
    )


def _items(public_evidence: dict[str, Any]) -> list[dict[str, Any]]:
    items = public_evidence.get("items")
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []


def _allowed_use(value: str) -> str:
    return value if value in {"canState", "needsQualification", "canUseAsFraming", "doNotState"} else "needsQualification"


def _confidence(value: str) -> str:
    return value if value in {"high", "medium", "low", "unknown"} else "medium"


__all__ = (
    'SYNTHESIS_KEYS',
    'SYNTHESIS_TEMPERATURE',
    'ExternalEvidenceSynthesisService',
)
