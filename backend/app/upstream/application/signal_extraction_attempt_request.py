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
from backend.app.upstream.application.signal_extraction_context import (
    SignalExtractionDossierFactory,
)
from backend.app.upstream.application.signal_extraction_dossier import SignalExtractionDossier


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
        base_input_chars = len(json.dumps(dossier.provider_input, ensure_ascii=False, sort_keys=True))
        repair_limit = min(
            SignalExtractionDossierFactory.MAX_REPAIR_CONTEXT_CHARS,
            max(
                0,
                profile.max_provider_input_chars
                - base_input_chars
                - SignalExtractionDossierFactory.REPAIR_CONTEXT_OVERHEAD_CHARS,
            ),
        )
        repair_context = self._repair_context(repair_errors, max_chars=repair_limit) if label in {"repair", "backup"} else ""
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
                    " Поля title, summary, uncertainty, mechanism, outcome и limitations пиши на editorialLanguage из extractionContract."
                    " Не оставляй английский заголовок или английское предложение в редакционном поле, даже если источник английский."
                    " Не переводи source metadata и evidenceRefs.quote. Каждую quote копируй как точную непрерывную подстроку fragment text:"
                    " без многоточий, исправлений, перевода и нормализации пунктуации."
                    " Каждое число и каждая дата из title, summary, uncertainty, mechanism, outcome и limitations"
                    " обязаны дословно присутствовать хотя бы в одной evidenceRefs.quote этого signal."
                    " Перед ответом проверь язык каждого редакционного поля, точность каждой quote и grounding всех чисел."
                    " Если signal нельзя вернуть без нарушения хотя бы одного правила, не возвращай этот signal;"
                    " не ослабляй правила и не выдумывай замену."
                ),
            },
            {"role": "user", "content": json.dumps(provider_input, ensure_ascii=False, sort_keys=True)},
        ]

    def _repair_context(self, errors: list[str], *, max_chars: int) -> str:
        if max_chars <= 0:
            return ""
        corrections: list[str] = [
            "В исправленной попытке верни не более одного сильнейшего сигнала на material. "
            "Каждое редакционное поле напиши как законченную фразу на editorialLanguage; "
            "латиница допустима только в неизбежных названиях и коротких технических сокращениях.",
            "Не используй числа и даты в редакционных полях, если тот же токен не скопирован "
            "дословно в evidenceRefs.quote этого сигнала; безопаснее опустить неподтвержденное число.",
        ]
        joined = " ".join(errors)
        if "editorial-language-not-satisfied" in joined:
            corrections.append(
                "Все редакционные поля перепиши целиком на editorialLanguage; английский source title в них не сохраняй. "
                "Исходные цитаты не переводи."
            )
        if "quote-not-in-fragment" in joined:
            corrections.append(
                "Каждую evidenceRefs.quote скопируй как точную непрерывную подстроку указанного fragment text "
                "без многоточий, перевода и изменения пунктуации."
            )
        if "number-or-date-not-grounded" in joined:
            corrections.append(
                "Удаляй из всех редакционных полей число или дату, которых нет дословно в evidenceRefs.quote этого signal; "
                "не пересчитывай и не меняй десятичный разделитель."
            )
        if "missing-material-decision" in joined or "provider-did-not-return-decision" in joined:
            corrections.append("Верни ровно одно materialDecision для каждого переданного materialId.")
        payload = {
            "errorType": "schema-or-grounding",
            "requiredCorrections": corrections,
            "validationErrors": errors[:12],
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)[:max_chars]


__all__ = ("SignalExtractionAttemptRequest", "SignalExtractionAttemptRequestBuilder")
