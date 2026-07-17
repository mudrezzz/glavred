"""Owner: upstream.application

Used by: signal extraction payload mapping after evidence references are parsed.
Does not own: language validation, provider retries, grounding, or UI rendering.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from backend.app.upstream.application.signal_extraction_dossier import SignalExtractionDossier
from backend.app.upstream.domain.signal_extraction_contracts import SignalEvidenceRef


class SignalLocalizationPolicy:
    """Classifies whether editorial fields are original, localized, or unverified."""

    def classify(
        self,
        *,
        evidence_refs: tuple[SignalEvidenceRef, ...],
        dossier: SignalExtractionDossier,
        editorial_language: str,
    ) -> tuple[str, str, tuple[str, ...]]:
        evidence_material_ids = {ref.material_id for ref in evidence_refs}
        material_languages = {
            str((item.get("sourceLanguage") or {}).get("language") or "unknown")
            for item in dossier.provider_input.get("materials", [])
            if str(item.get("id") or "") in evidence_material_ids
        }
        if not material_languages or material_languages.intersection({"unknown", "mixed"}):
            return "unknown", "unverified", ("source-language-unverified",)
        if len(material_languages) > 1:
            return "mixed", "localized", ("multiple-source-languages",)
        source_language = next(iter(material_languages))
        if source_language == editorial_language:
            return source_language, "original", ("source-matches-editorial-language",)
        return source_language, "localized", ("editorial-fields-localized",)


__all__ = ("SignalLocalizationPolicy",)
