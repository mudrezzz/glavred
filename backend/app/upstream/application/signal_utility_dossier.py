"""Owner: upstream.application

Used by: SignalUtilityScoringService before every provider scoring revision.
Does not own: provider retries, semantic scoring, final recommendation, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import json
from typing import Any

from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfile
from backend.app.upstream.domain.signal_utility import ProjectEditorialOpportunityProfile, SignalUtilityDossier
from backend.app.upstream.application.signal_relationships import SignalRelationshipPolicy


class SignalUtilityDossierFactory:
    MAX_EVIDENCE_PER_SIGNAL = 4
    REPAIR_CONTEXT_RESERVE_CHARS = 1200
    NEVER_SEND = (
        "workspace",
        "fabulas",
        "contentPlanItems",
        "publicationHistory",
        "radarRuns",
        "operations",
        "providerAttempts",
        "operationEnvelope",
    )

    def __init__(self) -> None:
        self._relationships = SignalRelationshipPolicy()

    def build(
        self,
        *,
        profile: ProjectEditorialOpportunityProfile,
        signals: list[dict[str, Any]],
        budget: UpstreamProviderBudgetProfile,
    ) -> SignalUtilityDossier:
        retained_signals = signals[: budget.max_materials]
        provider_signals = [
            self._signal_projection(item, signal_key=f"s{index + 1}")
            for index, item in enumerate(retained_signals)
        ]
        relationship_candidates = self._relationships.candidate_payload(retained_signals)
        missing = [f"signal:{item.get('id') or '?'}:evidence" for item in retained_signals if not item.get("evidenceRefs")]
        provider_input = {
            "projectProfile": profile.to_payload(),
            "signals": provider_signals,
            "evaluationContract": {
                "statuses": ["matched", "partial", "notProven", "conflict"],
                "criteria": [
                    {
                        "key": f"c{index + 1}",
                        "settingId": setting.id,
                        "dimension": setting.dimension,
                        "mode": setting.mode,
                        "origin": setting.origin,
                    }
                    for index, setting in enumerate(profile.settings)
                    if setting.dimension
                ],
                "requiredSignalKeys": [item["key"] for item in provider_signals],
                "rule": "Evaluate meaning against referenced settings. Missing proof is not a conflict.",
            },
            "relationshipCandidates": relationship_candidates,
        }
        trimmed_counts = {
            **profile.trimmed_counts,
            "signals": max(0, len(signals) - len(retained_signals)),
            "evidence": sum(max(0, len(item.get("evidenceRefs") or []) - self.MAX_EVIDENCE_PER_SIGNAL) for item in retained_signals),
        }
        suppressed = list(self.NEVER_SEND)
        readiness = "BLOCKED" if not retained_signals or missing else "READY"
        if readiness != "BLOCKED":
            dossier_limit = max(0, budget.max_provider_input_chars - self.REPAIR_CONTEXT_RESERVE_CHARS)
            provider_input, compacted = self._fit(provider_input, dossier_limit)
            if compacted:
                readiness = "DEGRADED"
                suppressed.extend(compacted)
            if self._size(provider_input) > dossier_limit:
                readiness = "BLOCKED"
                missing.append("provider-input-over-budget")

        settings = provider_input.get("projectProfile", {}).get("settings", [])
        evidence_keys = {
            self._evidence_key(ref)
            for signal in provider_input.get("signals", [])
            for ref in signal.get("evidenceRefs", [])
        }
        return SignalUtilityDossier(
            provider_input=provider_input,
            signal_ids=tuple(str(item.get("id") or "") for item in retained_signals),
            setting_ids=frozenset(str(item.get("id") or "") for item in settings),
            evidence_keys=frozenset(evidence_keys),
            readiness=readiness,
            missing_inputs=tuple(missing),
            suppressed_fields=tuple(dict.fromkeys(suppressed)),
            retained_counts={**profile.retained_counts, "signals": len(retained_signals)},
            trimmed_counts=trimmed_counts,
            relationship_pair_ids=frozenset(str(item["pairId"]) for item in relationship_candidates),
        )

    def _signal_projection(self, signal: dict[str, Any], *, signal_key: str) -> dict[str, Any]:
        return {
            "key": signal_key,
            "id": str(signal.get("id") or ""),
            "type": str(signal.get("type") or ""),
            "title": self._cap(str(signal.get("title") or ""), 220),
            "summary": self._cap(str(signal.get("summary") or ""), 420),
            "confidence": str(signal.get("confidence") or "unknown"),
            "uncertainty": self._cap(str(signal.get("uncertainty") or ""), 260),
            "mechanism": self._cap(str(signal.get("mechanism") or ""), 320),
            "outcome": self._cap(str(signal.get("outcome") or ""), 320),
            "limitations": [self._cap(str(item), 180) for item in (signal.get("limitations") or [])[:3]],
            "sourceLanguage": str(signal.get("sourceLanguage") or "unknown"),
            "evidenceRefs": [
                {
                    "key": f"e{index + 1}",
                    "materialId": str(item.get("materialId") or ""),
                    "fragmentId": str(item.get("fragmentId") or ""),
                    "quote": self._cap(str(item.get("quote") or ""), 320),
                }
                for index, item in enumerate((signal.get("evidenceRefs") or [])[: self.MAX_EVIDENCE_PER_SIGNAL])
                if isinstance(item, dict)
            ],
        }

    def _fit(self, payload: dict[str, Any], limit: int) -> tuple[dict[str, Any], list[str]]:
        compacted: list[str] = []
        project = payload["projectProfile"]
        while self._size(payload) > limit and project.get("historyFingerprints"):
            project["historyFingerprints"].pop()
            compacted.append("historyFingerprints")
        non_filters = [item for item in project.get("settings", []) if not str(item.get("kind", "")).startswith("radarFilter:")]
        while self._size(payload) > limit and len(non_filters) > 6:
            removed = non_filters.pop()
            project["settings"].remove(removed)
            contract = payload.get("evaluationContract")
            if isinstance(contract, dict) and isinstance(contract.get("criteria"), list):
                contract["criteria"] = [
                    item for item in contract["criteria"]
                    if not isinstance(item, dict) or item.get("settingId") != removed.get("id")
                ]
            compacted.append("optionalProjectSettings")
        for signal in payload["signals"]:
            while self._size(payload) > limit and len(signal.get("evidenceRefs", [])) > 2:
                signal["evidenceRefs"].pop()
                compacted.append("optionalEvidenceRefs")
        if self._size(payload) > limit:
            for signal in payload["signals"]:
                for field in ("summary", "mechanism", "outcome", "uncertainty"):
                    signal[field] = self._cap(str(signal.get(field) or ""), 180)
            compacted.append("optionalSignalDetail")
        return payload, compacted

    def _size(self, payload: dict[str, Any]) -> int:
        return len(json.dumps(payload, ensure_ascii=False, sort_keys=True))

    def _evidence_key(self, ref: dict[str, Any]) -> str:
        return f"{ref.get('materialId') or ''}:{ref.get('fragmentId') or ''}"

    def _cap(self, value: str, limit: int) -> str:
        clean = " ".join(value.split())
        return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


__all__ = ("SignalUtilityDossierFactory",)
