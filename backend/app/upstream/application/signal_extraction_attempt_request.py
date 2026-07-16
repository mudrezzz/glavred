"""Owner: upstream.application

Used by: SignalExtractionAttemptRunner before every provider attempt.
Does not own: provider transport, retry order, payload parsing, or material decisions.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from backend.app.shared.llm_operations.provider_message_budget_guard import ProviderMessageBudgetGuard
from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfile
from backend.app.upstream.application.provider_input_budget_gate import UpstreamProviderInputBudgetGate
from backend.app.upstream.application.signal_extraction_context import SignalExtractionDossier


@dataclass(frozen=True)
class SignalExtractionAttemptRequest:
    fields: dict[str, Any]
    messages: list[dict[str, str]]
    blocked_reason: str | None


class SignalExtractionAttemptRequestBuilder:
    def __init__(self) -> None:
        self._input_gate = UpstreamProviderInputBudgetGate()
        self._message_guard = ProviderMessageBudgetGuard()

    def build(
        self,
        *,
        dossier: SignalExtractionDossier,
        profile: UpstreamProviderBudgetProfile,
        label: str,
        model: str,
        repair_errors: list[str],
    ) -> SignalExtractionAttemptRequest:
        repair_context = self._repair_context(repair_errors) if label == "repair" else ""
        provider_input = dict(dossier.provider_input)
        if repair_context:
            provider_input["repairContext"] = repair_context
        budget = self._input_gate.evaluate(provider_input=provider_input, profile=profile, run_budget={})
        messages = self._messages(provider_input)
        guarded = self._message_guard.evaluate(
            messages=messages,
            request_fields=budget.request_fields,
            repair_context_char_count=len(repair_context),
        )
        fields = {
            **guarded.request_fields,
            "draftRunStep": None,
            "operationId": "signalExtraction",
            "attemptLabel": label,
            "selectedModel": model,
            "maxOutputTokens": profile.max_output_tokens,
            "providerDossier": dossier.trace_payload(),
        }
        fields["payloadStats"] = {
            **dict(fields.get("payloadStats") or {}),
            "retainedMaterialCount": len(dossier.eligible_material_ids),
            "retainedFragmentCount": len(dossier.fragment_index),
            "trimmedMaterialCount": len(dossier.deferred_material_ids),
            "trimmedFragmentCount": dossier.trimmed_fragment_count,
            "trimmedContextCount": dossier.trimmed_context_count,
            "suppressedFields": list(dossier.suppressed_fields),
        }
        return SignalExtractionAttemptRequest(
            fields=fields,
            messages=messages,
            blocked_reason=budget.blocked_reason or guarded.blocked_reason,
        )

    def _messages(self, provider_input: dict[str, Any]) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "Извлеки только доказательные сигналы из переданных фрагментов. "
                    "Не оценивай полезность для темы или канала. Не придумывай факты. "
                    "Верни JSON object с массивами signals и materialDecisions. "
                    "Каждый signal обязан иметь evidenceRefs с materialId, fragmentId и точной quote из fragment text. "
                    "Поле confidence допускает только строки low, medium или high. "
                    "Выбери не более трёх сильнейших сигналов на материал; слабый материал должен дать ноль сигналов. "
                    "Соблюдай fieldCharLimits из extractionContract. "
                    "Для каждого переданного material верни ровно одно materialDecision с materialId, decision и reasonCodes."
                ),
            },
            {"role": "user", "content": json.dumps(provider_input, ensure_ascii=False, sort_keys=True)},
        ]

    def _repair_context(self, errors: list[str]) -> str:
        return json.dumps(
            {"errorType": "schema-or-grounding", "validationErrors": errors[:12]},
            ensure_ascii=False,
            sort_keys=True,
        )[:1200]


__all__ = ("SignalExtractionAttemptRequest", "SignalExtractionAttemptRequestBuilder")
