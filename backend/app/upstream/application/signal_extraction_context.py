"""Owner: upstream.application

Used by: SignalExtractionService before any provider attempt.
Does not own: provider transport, grounding validation, project utility scoring, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfile
from backend.app.upstream.application.signal_extraction_compaction import SignalExtractionDossierCompactor
from backend.app.upstream.application.signal_extraction_fragments import FoundMaterialFragmentPolicy


@dataclass(frozen=True)
class SignalExtractionDossier:
    provider_input: dict[str, Any]
    fragment_index: dict[tuple[str, str], dict[str, Any]]
    eligible_material_ids: tuple[str, ...]
    deferred_material_ids: tuple[str, ...]
    legacy_material_ids: tuple[str, ...]
    readiness: str
    suppressed_fields: tuple[str, ...]
    trimmed_fragment_count: int = 0
    trimmed_context_count: int = 0

    def trace_payload(self) -> dict[str, Any]:
        return {
            "profileId": "upstream-signal-extraction-dossier-v1",
            "readiness": self.readiness,
            "eligibleMaterialIds": list(self.eligible_material_ids),
            "deferredMaterialIds": list(self.deferred_material_ids),
            "legacyMaterialIds": list(self.legacy_material_ids),
            "fragmentCount": len(self.fragment_index),
            "trimmedFragmentCount": self.trimmed_fragment_count,
            "trimmedContextCount": self.trimmed_context_count,
            "suppressedFields": list(self.suppressed_fields),
            "neverSendToProvider": list(self.suppressed_fields),
            "runtimeMigrated": True,
        }


class SignalExtractionContextFactory:
    def build(self, *, workspace: dict[str, Any], radar: dict[str, Any]) -> dict[str, Any]:
        return {
            "projectId": str(workspace.get("projectId") or workspace.get("id") or ""),
            "radarId": str(radar.get("id") or ""),
            "scope": str(radar.get("scope") or "")[:600],
            "rules": [
                {"id": str(item.get("id") or ""), "statement": str(item.get("statement") or "")[:240]}
                for item in radar.get("rules", [])
                if isinstance(item, dict) and item.get("status", "active") != "archived"
            ][:8],
            "filters": [
                {
                    "id": str(item.get("id") or ""),
                    "dimension": str(item.get("dimension") or ""),
                    "mode": str(item.get("mode") or ""),
                    "instruction": str(item.get("instruction") or "")[:240],
                }
                for item in radar.get("filters", [])
                if isinstance(item, dict) and item.get("enabled", True)
            ][:8],
        }


class SignalExtractionDossierFactory:
    NEVER_SEND = (
        "workspace",
        "topics",
        "fabulas",
        "contentPlan",
        "publicationHistory",
        "rawResults",
        "searchTriage",
        "operations",
        "operationEnvelope",
        "payloadBudget",
    )

    def __init__(self, fragment_policy: FoundMaterialFragmentPolicy | None = None) -> None:
        self._fragments = fragment_policy or FoundMaterialFragmentPolicy()
        self._compactor = SignalExtractionDossierCompactor()

    def build(
        self,
        *,
        context: dict[str, Any],
        materials: list[dict[str, Any]],
        profile: UpstreamProviderBudgetProfile,
    ) -> SignalExtractionDossier:
        eligible: list[dict[str, Any]] = []
        deferred: list[str] = []
        legacy: list[str] = []
        fragment_index: dict[tuple[str, str], dict[str, Any]] = {}

        readable = [item for item in materials if item.get("status") not in {"metadataOnly", "skipped", "duplicate"}]
        for material in readable:
            material_id = str(material.get("id") or "")
            if len(eligible) >= profile.max_materials:
                deferred.append(material_id)
                continue
            fragments = material.get("contentFragments") if isinstance(material.get("contentFragments"), list) else []
            is_legacy = not fragments
            if is_legacy:
                fragments = self._fragments.legacy_summary(material)
                legacy.append(material_id)
            selected_fragments = []
            for fragment in fragments[: profile.max_fragments_per_material]:
                if not isinstance(fragment, dict):
                    continue
                bounded = {
                    "id": str(fragment.get("id") or ""),
                    "text": str(fragment.get("text") or "")[: profile.max_fragment_chars],
                    "kind": str(fragment.get("kind") or "text"),
                    "hash": str(fragment.get("hash") or ""),
                }
                if not bounded["id"] or not bounded["text"]:
                    continue
                fragment_index[(material_id, bounded["id"])] = bounded
                selected_fragments.append(bounded)
            if not selected_fragments:
                deferred.append(material_id)
                continue
            eligible.append(
                {
                    "id": material_id,
                    "title": str(material.get("title") or "")[:300],
                    "locator": str(material.get("locator") or "")[:2048],
                    "provenance": str(material.get("provenanceLabel") or "")[:300],
                    "legacySummaryOnly": is_legacy,
                    "fragments": selected_fragments,
                    "discovery": {
                        "families": list((material.get("discoveryTrace") or {}).get("families") or []),
                        "evidenceTypes": list((material.get("discoveryTrace") or {}).get("evidenceTypes") or []),
                    },
                }
            )

        readiness = "BLOCKED" if not eligible else ("DEGRADED" if legacy or deferred else "READY")
        provider_input = {
            "operationId": "signalExtraction",
            "context": context,
            "materials": eligible,
            "extractionContract": {
                "signalTypes": [
                    "eventFact", "change", "audienceQuestion", "tensionCounterargument", "case",
                    "dataPoint", "practice", "problemFailureMode", "personalObservation", "recurringPattern",
                ],
                "materialDecisions": [
                    "signalProducing", "insufficient", "duplicate", "corroborating",
                    "contradiction", "noise", "extractionFailed",
                ],
                "requiredSignalFields": [
                    "type", "title", "summary", "confidence", "uncertainty", "evidenceRefs",
                    "mechanism", "actors", "outcome", "limitations", "reasonCodes",
                ],
                "confidenceValues": ["low", "medium", "high"],
                "maxSignalsPerMaterial": 3,
                "preferZeroSignalsOverWeakClaims": True,
                "fieldCharLimits": {
                    "title": 180,
                    "summary": 500,
                    "uncertainty": 300,
                    "mechanism": 500,
                    "outcome": 500,
                    "evidenceQuote": 500,
                },
                "requiredDecisionFields": ["materialId", "decision", "reasonCodes"],
                "evidenceRefFields": ["materialId", "fragmentId", "quote"],
                "forbiddenOwnership": ["suggestedTopicId", "suggestedFabulaId", "audience", "value", "goal", "platform", "channel"],
            },
        }
        compacted = self._compactor.compact(provider_input, max_chars=profile.max_provider_input_chars)
        provider_input = compacted.provider_input
        fragment_index = {
            (str(material["id"]), str(fragment["id"])): fragment
            for material in provider_input["materials"]
            for fragment in material["fragments"]
        }
        compacted_context = compacted.trimmed_fragment_count > 0 or compacted.trimmed_context_count > 0
        return SignalExtractionDossier(
            provider_input=provider_input,
            fragment_index=fragment_index,
            eligible_material_ids=tuple(item["id"] for item in eligible),
            deferred_material_ids=tuple(deferred),
            legacy_material_ids=tuple(legacy),
            readiness="DEGRADED" if readiness == "READY" and compacted_context else readiness,
            suppressed_fields=self.NEVER_SEND,
            trimmed_fragment_count=compacted.trimmed_fragment_count,
            trimmed_context_count=compacted.trimmed_context_count,
        )


__all__ = ("SignalExtractionContextFactory", "SignalExtractionDossier", "SignalExtractionDossierFactory")
