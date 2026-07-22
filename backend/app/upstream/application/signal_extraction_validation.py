"""Owner: upstream.application

Used by: SignalExtractionService to map, ground, and deduplicate provider output.
Does not own: provider transport, prompt construction, project utility, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import hashlib
from typing import Any

from backend.app.upstream.application.signal_extraction_dossier import SignalExtractionDossier
from backend.app.upstream.application.signal_editorial_language import SignalEditorialLanguagePolicy
from backend.app.upstream.application.signal_extraction_fields import SignalExtractionFieldParser
from backend.app.upstream.application.signal_grounding import SignalGroundingPolicy
from backend.app.upstream.application.signal_localization import SignalLocalizationPolicy
from backend.app.upstream.domain.signal_extraction_contracts import (
    ExtractedSourceSignal,
    MaterialDecisionRecord,
    MaterialExtractionDecision,
    SignalEvidenceRef,
    SignalType,
)


class SignalExtractionPayloadError(ValueError):
    def __init__(self, errors: list[str], grounding_violations: list[dict[str, Any]] | None = None) -> None:
        self.errors = tuple(errors)
        self.grounding_violations = tuple(grounding_violations or [])
        super().__init__("; ".join(errors))


class SignalExtractionPayloadMapper:
    _FORBIDDEN_FIELDS = {"suggestedTopicId", "suggestedFabulaId", "audience", "value", "goal", "platform", "channel"}

    def __init__(
        self,
        grounding: SignalGroundingPolicy | None = None,
        editorial_language: SignalEditorialLanguagePolicy | None = None,
        localization: SignalLocalizationPolicy | None = None,
        fields: SignalExtractionFieldParser | None = None,
    ) -> None:
        self._grounding = grounding or SignalGroundingPolicy()
        self._editorial_language = editorial_language or SignalEditorialLanguagePolicy()
        self._localization = localization or SignalLocalizationPolicy()
        self._fields = fields or SignalExtractionFieldParser()

    def map(
        self,
        *,
        payload: dict[str, Any],
        dossier: SignalExtractionDossier,
        radar_id: str,
        run_id: str,
    ) -> tuple[list[ExtractedSourceSignal], list[MaterialDecisionRecord], list[dict[str, Any]]]:
        errors: list[str] = []
        raw_signals = payload.get("signals")
        raw_decisions = payload.get("materialDecisions")
        if not isinstance(raw_signals, list):
            errors.append("signals-must-be-list")
        if not isinstance(raw_decisions, list):
            errors.append("materialDecisions-must-be-list")
        if errors:
            raise SignalExtractionPayloadError(errors)

        signals: list[ExtractedSourceSignal] = []
        violations: list[dict[str, Any]] = []
        for index, item in enumerate(raw_signals):
            if not isinstance(item, dict):
                errors.append(f"signal-{index}-must-be-object")
                continue
            forbidden = sorted(self._FORBIDDEN_FIELDS.intersection(item))
            if forbidden:
                errors.append(f"signal-{index}-forbidden-fields:{','.join(forbidden)}")
                continue
            try:
                signal = self._signal(item, dossier=dossier, radar_id=radar_id, run_id=run_id)
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"signal-{index}-invalid:{exc}")
                continue
            language_errors = self._editorial_language.validate(signal)
            if language_errors:
                errors.extend(f"signal-{index}-{item}" for item in language_errors)
                continue
            grounded, signal_violations = self._grounding.validate(signal=signal, dossier=dossier)
            violations.extend(signal_violations)
            if grounded:
                signals.append(grounded)

        decisions = self._decisions(raw_decisions, dossier=dossier, errors=errors)
        counts_by_material: dict[str, int] = {}
        for signal in signals:
            for material_id in dict.fromkeys(ref.material_id for ref in signal.evidence_refs):
                counts_by_material[material_id] = counts_by_material.get(material_id, 0) + 1
        for material_id, count in counts_by_material.items():
            if count > 3:
                errors.append(f"too-many-signals-for-material:{material_id}:{count}/3")
        if violations:
            errors.extend(f"grounding:{item['reasonCode']}:{item['detail']}" for item in violations)
        if errors:
            raise SignalExtractionPayloadError(errors, violations)
        return signals, decisions, violations

    def _signal(
        self,
        item: dict[str, Any],
        *,
        dossier: SignalExtractionDossier,
        radar_id: str,
        run_id: str,
    ) -> ExtractedSourceSignal:
        signal_type = SignalType(str(item["type"]))
        title = self._fields.required_text(item, "title", 300)
        summary = self._fields.required_text(item, "summary", 1200)
        confidence = self._fields.confidence(item.get("confidence"))
        refs = item.get("evidenceRefs")
        if not isinstance(refs, list) or not refs:
            raise ValueError("missing-evidenceRefs")
        evidence_refs = tuple(
            SignalEvidenceRef(
                material_id=self._fields.required_text(ref, "materialId", 200),
                fragment_id=self._fields.required_text(ref, "fragmentId", 240),
                quote=self._fields.required_text(ref, "quote", 1000),
            )
            for ref in refs
            if isinstance(ref, dict)
        )
        if not evidence_refs:
            raise ValueError("empty-evidenceRefs")
        stable_source = "|".join(
            [radar_id, signal_type.value, self._fields.canonical(title), *(f"{ref.material_id}:{ref.fragment_id}" for ref in evidence_refs)]
        )
        signal_id = f"signal-{hashlib.sha256(stable_source.encode('utf-8')).hexdigest()[:20]}"
        editorial_language = str(
            (((dossier.provider_input.get("context") or {}).get("languageContext") or {}).get("editorialLanguage"))
            or "ru"
        )
        source_language, localization_status, localization_reasons = self._localization.classify(
            evidence_refs=evidence_refs,
            dossier=dossier,
            editorial_language=editorial_language,
        )
        return ExtractedSourceSignal(
            id=signal_id,
            radar_id=radar_id,
            run_id=run_id,
            signal_type=signal_type,
            title=title,
            summary=summary,
            confidence=confidence,
            uncertainty=str(item.get("uncertainty") or "")[:800],
            evidence_refs=evidence_refs,
            mechanism=str(item.get("mechanism") or "")[:1000],
            actors=self._fields.string_list(item.get("actors"), item_limit=200, max_items=12),
            outcome=str(item.get("outcome") or "")[:1000],
            limitations=self._fields.string_list(item.get("limitations"), item_limit=500, max_items=12),
            reason_codes=self._fields.string_list(item.get("reasonCodes"), item_limit=120, max_items=20),
            editorial_language=editorial_language,
            source_language=source_language,
            localization_status=localization_status,
            localization_reason_codes=localization_reasons,
        )

    def _decisions(
        self,
        raw_decisions: list[Any],
        *,
        dossier: SignalExtractionDossier,
        errors: list[str],
    ) -> list[MaterialDecisionRecord]:
        decisions: list[MaterialDecisionRecord] = []
        seen: set[str] = set()
        expected = set(dossier.eligible_material_ids)
        for index, item in enumerate(raw_decisions):
            if not isinstance(item, dict):
                errors.append(f"decision-{index}-must-be-object")
                continue
            material_id = str(item.get("materialId") or "")
            if material_id not in expected or material_id in seen:
                errors.append(f"decision-{index}-unknown-or-duplicate-material")
                continue
            seen.add(material_id)
            try:
                decision = MaterialExtractionDecision(str(item.get("decision") or ""))
            except ValueError:
                errors.append(f"decision-{index}-unknown-decision")
                continue
            decisions.append(
                MaterialDecisionRecord(
                    material_id=material_id,
                    decision=decision,
                    reason_codes=self._fields.string_list(item.get("reasonCodes"), item_limit=120, max_items=20),
                )
            )
        for missing in sorted(expected - seen):
            errors.append(f"missing-material-decision:{missing}")
        return decisions


__all__ = (
    "SignalExtractionPayloadError",
    "SignalExtractionPayloadMapper",
)
