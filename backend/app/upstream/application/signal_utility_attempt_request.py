"""Owner: upstream.application

Used by: SignalUtilityAttemptRunner before each provider attempt.
Does not own: provider transport, retry order, payload mapping, or recommendation policy.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from backend.app.shared.llm_operations.provider_message_budget_guard import ProviderMessageBudgetGuard
from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfile
from backend.app.upstream.application.provider_input_budget_gate import UpstreamProviderInputBudgetGate
from backend.app.upstream.domain.signal_utility import SignalUtilityDossier


@dataclass(frozen=True)
class SignalUtilityAttemptRequest:
    fields: dict[str, Any]
    messages: list[dict[str, str]]
    blocked_reason: str | None


class SignalUtilityAttemptRequestBuilder:
    MAX_REPAIR_CONTEXT_CHARS = 1200

    def __init__(self) -> None:
        self._input_gate = UpstreamProviderInputBudgetGate()
        self._message_guard = ProviderMessageBudgetGuard()

    def build(
        self,
        *,
        dossier: SignalUtilityDossier,
        profile: UpstreamProviderBudgetProfile,
        label: str,
        model: str,
        repair_errors: list[str],
    ) -> SignalUtilityAttemptRequest:
        provider_input = dict(dossier.provider_input)
        repair_context = self._repair_context(repair_errors) if label in {"repair", "backup"} else ""
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
            "operationId": "signalScoring",
            "attemptLabel": label,
            "selectedModel": model,
            "maxOutputTokens": profile.max_output_tokens,
            "providerDossier": dossier.trace_payload(),
        }
        fields["payloadStats"] = {
            **dict(fields.get("payloadStats") or {}),
            "retainedSignalCount": len(dossier.signal_ids),
            "retainedSettingCount": len(dossier.setting_ids),
            "retainedEvidenceCount": len(dossier.evidence_keys),
            "suppressedFields": list(dossier.suppressed_fields),
            "trimmedCounts": dossier.trimmed_counts,
        }
        return SignalUtilityAttemptRequest(
            fields=fields,
            messages=messages,
            blocked_reason=budget.blocked_reason or guarded.blocked_reason,
        )

    def _messages(self, provider_input: dict[str, Any]) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": (
                    "Оцени редакционную полезность каждого сигнала для конкретного проекта. "
                    "Не утверждай и не отклоняй сигнал: верни только семантические dimension results. "
                    "Используй только переданные setting IDs и evidence handles. "
                    "notProven означает отсутствие доказательства и не равен conflict. "
                    "Для mustNotMatch conflict означает доказанное попадание в запрещенную область. "
                    "Для каждого evaluationContract.criteria верни отдельный criterion с указанным criterionKey. "
                    "Для каждого relationshipCandidates по возможности верни relationships с pairId, kind и summary. "
                    "Верни ровно JSON object вида {\"signalEvaluations\": [{\"signalKey\": \"s1\", "
                    "\"criteria\": [{\"criterionKey\": \"c1\", \"status\": \"matched\", \"summary\": \"...\", "
                    "\"evidenceKeys\": [\"e1\"]}]}], \"relationships\": []}. "
                    "signalEvaluations всегда массив, даже для одного сигнала. Используй только переданные короткие "
                    "signalKey, criterionKey и evidence key; не копируй полные signalId, settingId, materialId или fragmentId. "
                    "Корневой relationships всегда массив. "
                    "Ответ должен быть компактным: summary не длиннее 120 символов, uncertainty не длиннее 80 символов, "
                    "reasonCodes содержит не более одного кода, evidenceRefs содержит не более одной самой сильной ссылки. "
                    "Не повторяй в summary текст настройки, сигнала или цитаты и не добавляй поля вне контракта. "
                    "Не возвращай общий процент."
                ),
            },
            {"role": "user", "content": json.dumps(provider_input, ensure_ascii=False, sort_keys=True)},
        ]

    def _repair_context(self, errors: list[str]) -> str:
        payload = {
            "errorType": "signal-utility-contract",
            "requiredCorrections": [
                "Используй только перечисленные signalId, setting IDs и evidence handles.",
                "Верни один объект оценки на каждый requiredSignalId без дублей.",
                "Корневой объект обязан содержать массив signalEvaluations.",
                "У каждого dimension должны быть status и конкретная summary.",
                "Покрой каждый evaluationContract.criteria элементом criteria с тем же criterionKey.",
                "Используй короткие signalKey/criterionKey/evidenceKeys вместо полных технических ID.",
                "Используй только перечисленные relationship pairId и допустимые relationship kinds.",
            ],
            "validationErrors": errors[:16],
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)[: self.MAX_REPAIR_CONTEXT_CHARS]


__all__ = ("SignalUtilityAttemptRequest", "SignalUtilityAttemptRequestBuilder")
