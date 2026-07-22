"""Owner: upstream.application

Used by: signal utility attempts to validate provider semantic comparisons.
Does not own: provider transport, retry order, recommendation policy, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.upstream.domain.signal_utility import (
    SignalUtilityDimension,
    SignalUtilityDimensionResult,
    SignalUtilityDossier,
    SignalUtilityImportance,
    SignalUtilityStatus,
)
from backend.app.upstream.application.signal_relationship_payload import SignalRelationshipPayloadMapper
from backend.app.upstream.application.signal_utility_compact_payload import SignalUtilityCompactCriteriaMapper


class SignalUtilityPayloadError(ValueError):
    def __init__(self, errors: list[str]) -> None:
        super().__init__(";".join(errors))
        self.errors = tuple(errors)


@dataclass(frozen=True)
class SignalUtilityMappedPayload:
    evaluations: dict[str, tuple[SignalUtilityDimensionResult, ...]]
    relationships: dict[str, dict[str, str]]


class SignalUtilityPayloadMapper:
    def __init__(self) -> None:
        self._relationships = SignalRelationshipPayloadMapper()
        self._compact = SignalUtilityCompactCriteriaMapper()

    def map(
        self,
        *,
        payload: dict[str, Any],
        dossier: SignalUtilityDossier,
        setting_modes: dict[str, str],
    ) -> SignalUtilityMappedPayload:
        raw_evaluations = payload.get("signalEvaluations")
        if isinstance(raw_evaluations, dict):
            raw_evaluations = [
                {"signalId": signal_id, **value}
                for signal_id, value in raw_evaluations.items()
                if isinstance(value, dict)
            ]
        if not isinstance(raw_evaluations, list):
            raise SignalUtilityPayloadError(["signalEvaluations-must-be-list"])
        errors: list[str] = []
        mapped: dict[str, tuple[SignalUtilityDimensionResult, ...]] = {}
        expected = set(dossier.signal_ids)
        signal_aliases = self._compact.signal_aliases(dossier)
        for raw in raw_evaluations:
            if not isinstance(raw, dict):
                errors.append("signal-evaluation-must-be-object")
                continue
            signal_id = str(raw.get("signalId") or signal_aliases.get(str(raw.get("signalKey") or "")) or "")
            if signal_id not in expected:
                errors.append(f"unknown-signal:{signal_id or '<blank>'}")
                continue
            if signal_id in mapped:
                errors.append(f"duplicate-signal-evaluation:{signal_id}")
                continue
            dimensions = (
                self._compact.map(
                    raw.get("criteria"),
                    dossier=dossier,
                    setting_modes=setting_modes,
                    signal_id=signal_id,
                    errors=errors,
                )
                if isinstance(raw.get("criteria"), list)
                else self._dimensions(
                    raw.get("dimensions"),
                    dossier=dossier,
                    setting_modes=setting_modes,
                    signal_id=signal_id,
                    errors=errors,
                )
            )
            if not dimensions:
                errors.append(f"missing-dimensions:{signal_id}")
            self._validate_required_filter_dimensions(
                dimensions,
                dossier=dossier,
                signal_id=signal_id,
                errors=errors,
            )
            mapped[signal_id] = tuple(dimensions)
        for missing in sorted(expected - set(mapped)):
            errors.append(f"missing-signal-evaluation:{missing}")
        if errors:
            raise SignalUtilityPayloadError(errors)
        relationships = self._relationships.map(payload.get("relationships"), dossier, errors)
        if errors:
            raise SignalUtilityPayloadError(errors)
        return SignalUtilityMappedPayload(mapped, relationships)

    def _dimensions(
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
        result: list[SignalUtilityDimensionResult] = []
        seen: set[tuple[SignalUtilityDimension, tuple[str, ...]]] = set()
        for raw in value:
            if not isinstance(raw, dict):
                errors.append(f"dimension-must-be-object:{signal_id}")
                continue
            try:
                dimension = SignalUtilityDimension(str(raw.get("dimension") or ""))
                status = SignalUtilityStatus(str(raw.get("status") or ""))
            except ValueError:
                errors.append(f"unknown-dimension-or-status:{signal_id}")
                continue
            setting_refs = tuple(dict.fromkeys(str(item) for item in raw.get("settingRefs", []) if item))
            identity = (dimension, tuple(sorted(setting_refs)))
            if identity in seen:
                errors.append(f"duplicate-dimension-setting:{signal_id}:{dimension.value}")
                continue
            seen.add(identity)
            unknown_settings = sorted(set(setting_refs) - dossier.setting_ids)
            if unknown_settings:
                errors.append(f"unresolved-setting:{signal_id}:{','.join(unknown_settings)}")
            evidence_refs = self._evidence_refs(raw.get("evidenceRefs"), dossier, signal_id, errors)
            summary = " ".join(str(raw.get("summary") or "").split())
            if not summary:
                errors.append(f"missing-dimension-summary:{signal_id}:{dimension.value}")
            importance = self._importance(setting_refs, setting_modes)
            result.append(
                SignalUtilityDimensionResult(
                    dimension=dimension,
                    status=status,
                    importance=importance,
                    summary=summary[:500],
                    reason_codes=tuple(str(item) for item in raw.get("reasonCodes", []) if item) or ("provider-semantic-evaluation",),
                    setting_refs=setting_refs,
                    evidence_refs=tuple(evidence_refs),
                    uncertainty=" ".join(str(raw.get("uncertainty") or "").split())[:320],
                )
            )
        return result

    def _validate_required_filter_dimensions(
        self,
        dimensions: list[SignalUtilityDimensionResult],
        *,
        dossier: SignalUtilityDossier,
        signal_id: str,
        errors: list[str],
    ) -> None:
        contract = dossier.provider_input.get("evaluationContract", {})
        requirements = (
            contract.get("criteria", contract.get("requiredSettingDimensions", []))
            if isinstance(contract, dict)
            else []
        )
        for requirement in requirements if isinstance(requirements, list) else []:
            if not isinstance(requirement, dict):
                continue
            dimension = str(requirement.get("dimension") or "")
            setting_id = str(requirement.get("settingId") or "")
            result = next(
                (
                    item for item in dimensions
                    if item.dimension.value == dimension and setting_id in item.setting_refs
                ),
                None,
            )
            if result is None:
                errors.append(f"missing-required-filter-dimension:{signal_id}:{setting_id}:{dimension}")

    def _evidence_refs(
        self,
        value: Any,
        dossier: SignalUtilityDossier,
        signal_id: str,
        errors: list[str],
    ) -> list[dict[str, str]]:
        if not isinstance(value, list):
            return []
        result: list[dict[str, str]] = []
        for raw in value:
            if not isinstance(raw, dict):
                continue
            material_id = str(raw.get("materialId") or "")
            fragment_id = str(raw.get("fragmentId") or "")
            key = f"{material_id}:{fragment_id}"
            if key not in dossier.evidence_keys:
                errors.append(f"unresolved-evidence:{signal_id}:{key}")
                continue
            result.append({"materialId": material_id, "fragmentId": fragment_id})
        return result

    def _importance(self, setting_refs: tuple[str, ...], setting_modes: dict[str, str]) -> SignalUtilityImportance:
        modes = {setting_modes.get(item, "shouldMatch") for item in setting_refs}
        if modes & {"mustMatch", "mustNotMatch"}:
            return SignalUtilityImportance.BLOCKING
        if "seekTension" in modes:
            return SignalUtilityImportance.DIAGNOSTIC
        return SignalUtilityImportance.WEIGHTED


__all__ = ("SignalUtilityMappedPayload", "SignalUtilityPayloadError", "SignalUtilityPayloadMapper")
