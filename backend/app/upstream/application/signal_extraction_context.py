"""Owner: upstream.application

Used by: SignalExtractionService before any provider attempt.
Does not own: provider transport, grounding validation, project utility scoring, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfile
from backend.app.upstream.application.radar_language_context import RadarLanguageContextFactory
from backend.app.upstream.application.signal_extraction_compaction import SignalExtractionDossierCompactor
from backend.app.upstream.application.signal_extraction_contract import SignalExtractionContractFactory
from backend.app.upstream.application.signal_extraction_dossier import SignalExtractionDossier
from backend.app.upstream.application.signal_extraction_fragments import FoundMaterialFragmentPolicy
from backend.app.upstream.domain.radar_language import RadarLanguageContext


class SignalExtractionContextFactory:
    def __init__(self, language_factory: RadarLanguageContextFactory | None = None) -> None:
        self._languages = language_factory or RadarLanguageContextFactory()

    def build(
        self,
        *,
        workspace: dict[str, Any],
        radar: dict[str, Any],
        language_context: RadarLanguageContext | None = None,
    ) -> dict[str, Any]:
        language_context = language_context or self._languages.build(
            project_context=None,
            workspace=workspace,
            radar=radar,
        )
        return {
            "projectId": language_context.project_id,
            "radarId": str(radar.get("id") or ""),
            "languageContext": language_context.to_payload(),
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
    MAX_REPAIR_CONTEXT_CHARS = 1200
    REPAIR_CONTEXT_OVERHEAD_CHARS = 64
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
        self._contract = SignalExtractionContractFactory()

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
        language_excluded: list[str] = []
        fragment_index: dict[tuple[str, str], dict[str, Any]] = {}

        readable = [item for item in materials if item.get("status") not in {"metadataOnly", "skipped", "duplicate"}]
        for material in readable:
            material_id = str(material.get("id") or "")
            if not self._source_language_allowed(material, context):
                language_excluded.append(material_id)
                continue
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
                    "sourceLanguage": material.get("sourceLanguage") or {"language": "unknown", "confidence": "low", "mixed": False},
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
            "extractionContract": self._contract.build(
                editorial_language=str((context.get("languageContext") or {}).get("editorialLanguage") or "ru"),
            ),
        }
        compacted = self._compactor.compact(
            provider_input,
            max_chars=max(
                0,
                profile.max_provider_input_chars
                - self.repair_context_reserve(profile)
                - self.REPAIR_CONTEXT_OVERHEAD_CHARS,
            ),
        )
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
            language_excluded_material_ids=tuple(language_excluded),
            readiness="DEGRADED" if readiness == "READY" and compacted_context else readiness,
            suppressed_fields=self.NEVER_SEND,
            trimmed_fragment_count=compacted.trimmed_fragment_count,
            trimmed_context_count=compacted.trimmed_context_count,
        )

    def _source_language_allowed(self, material: dict[str, Any], context: dict[str, Any]) -> bool:
        language_context = context.get("languageContext") if isinstance(context.get("languageContext"), dict) else {}
        if language_context.get("sourceLanguagePolicy") == "any":
            return True
        assessment = material.get("sourceLanguage") if isinstance(material.get("sourceLanguage"), dict) else {}
        language = str(assessment.get("language") or "unknown")
        confidence = str(assessment.get("confidence") or "low")
        mixed = bool(assessment.get("mixed"))
        if language in {"unknown", "mixed"} or mixed or confidence != "high":
            return True
        return language in set(language_context.get("allowedSourceLanguages") or [])

    @classmethod
    def repair_context_reserve(cls, profile: UpstreamProviderBudgetProfile) -> int:
        return min(cls.MAX_REPAIR_CONTEXT_CHARS, max(400, profile.max_provider_input_chars // 10))


__all__ = ("SignalExtractionContextFactory", "SignalExtractionDossierFactory")
