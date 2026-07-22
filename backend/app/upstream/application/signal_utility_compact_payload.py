"""Owner: upstream.application.

Used by: SignalUtilityPayloadMapper for compact provider criteria.
Does not own: signal batch completeness, legacy payloads, relationships, or policy.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.domain.signal_utility import (
    SignalUtilityDimension,
    SignalUtilityDimensionResult,
    SignalUtilityDossier,
    SignalUtilityImportance,
    SignalUtilityStatus,
)


class SignalUtilityCompactCriteriaMapper:
    def map(
        self,
        value: Any,
        *,
        dossier: SignalUtilityDossier,
        setting_modes: dict[str, str],
        signal_id: str,
        errors: list[str],
    ) -> list[SignalUtilityDimensionResult]:
        if not isinstance(value, list):
            return []
        contract = self._criterion_contract(dossier)
        evidence_aliases = self._evidence_aliases(dossier, signal_id)
        result: list[SignalUtilityDimensionResult] = []
        seen: set[str] = set()
        for raw in value:
            if not isinstance(raw, dict):
                errors.append(f"criterion-must-be-object:{signal_id}")
                continue
            criterion_key = str(raw.get("criterionKey") or "")
            requirement = contract.get(criterion_key)
            if requirement is None:
                errors.append(f"unknown-criterion:{signal_id}:{criterion_key or '<blank>'}")
                continue
            if criterion_key in seen:
                errors.append(f"duplicate-criterion:{signal_id}:{criterion_key}")
                continue
            seen.add(criterion_key)
            try:
                dimension = SignalUtilityDimension(str(requirement.get("dimension") or ""))
                status = SignalUtilityStatus(str(raw.get("status") or ""))
            except ValueError:
                errors.append(f"unknown-dimension-or-status:{signal_id}:{criterion_key}")
                continue
            setting_id = str(requirement.get("settingId") or "")
            setting_refs = (setting_id,) if setting_id else ()
            evidence_refs = self._resolve_evidence(
                raw.get("evidenceKeys"),
                evidence_aliases=evidence_aliases,
                signal_id=signal_id,
                errors=errors,
            )
            summary = " ".join(str(raw.get("summary") or "").split())
            if not summary:
                errors.append(f"missing-dimension-summary:{signal_id}:{dimension.value}")
            result.append(
                SignalUtilityDimensionResult(
                    dimension=dimension,
                    status=status,
                    importance=self._importance(setting_refs, setting_modes),
                    summary=summary[:240],
                    reason_codes=tuple(str(item) for item in raw.get("reasonCodes", []) if item)[:1]
                    or ("provider-semantic-evaluation",),
                    setting_refs=setting_refs,
                    evidence_refs=tuple(evidence_refs),
                    uncertainty=" ".join(str(raw.get("uncertainty") or "").split())[:120],
                )
            )
        return result

    def signal_aliases(self, dossier: SignalUtilityDossier) -> dict[str, str]:
        return {
            str(item.get("key") or ""): str(item.get("id") or "")
            for item in dossier.provider_input.get("signals", [])
            if isinstance(item, dict) and item.get("key") and item.get("id")
        }

    def _criterion_contract(self, dossier: SignalUtilityDossier) -> dict[str, dict[str, Any]]:
        contract = dossier.provider_input.get("evaluationContract", {})
        criteria = contract.get("criteria", []) if isinstance(contract, dict) else []
        return {
            str(item.get("key") or ""): item
            for item in criteria
            if isinstance(item, dict) and item.get("key")
        }

    def _evidence_aliases(self, dossier: SignalUtilityDossier, signal_id: str) -> dict[str, dict[str, str]]:
        signal = next(
            (
                item
                for item in dossier.provider_input.get("signals", [])
                if isinstance(item, dict) and str(item.get("id") or "") == signal_id
            ),
            {},
        )
        return {
            str(item.get("key") or ""): {
                "materialId": str(item.get("materialId") or ""),
                "fragmentId": str(item.get("fragmentId") or ""),
            }
            for item in signal.get("evidenceRefs", [])
            if isinstance(signal, dict) and isinstance(item, dict) and item.get("key")
        }

    def _resolve_evidence(
        self,
        value: Any,
        *,
        evidence_aliases: dict[str, dict[str, str]],
        signal_id: str,
        errors: list[str],
    ) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for evidence_key in dict.fromkeys(str(item) for item in value if item) if isinstance(value, list) else ():
            evidence = evidence_aliases.get(evidence_key)
            if evidence is None:
                errors.append(f"unresolved-evidence-alias:{signal_id}:{evidence_key}")
                continue
            result.append(evidence)
        return result

    def _importance(
        self,
        setting_refs: tuple[str, ...],
        setting_modes: dict[str, str],
    ) -> SignalUtilityImportance:
        modes = {setting_modes.get(item, "shouldMatch") for item in setting_refs}
        if modes & {"mustMatch", "mustNotMatch"}:
            return SignalUtilityImportance.BLOCKING
        if "seekTension" in modes:
            return SignalUtilityImportance.DIAGNOSTIC
        return SignalUtilityImportance.WEIGHTED


__all__ = ("SignalUtilityCompactCriteriaMapper",)
