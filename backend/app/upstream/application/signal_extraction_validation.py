"""Owner: upstream.application

Used by: SignalExtractionService to map, ground, and deduplicate provider output.
Does not own: provider transport, prompt construction, project utility, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from backend.app.upstream.application.signal_extraction_context import SignalExtractionDossier
from backend.app.upstream.application.signal_grounding import SignalGroundingPolicy
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

    def __init__(self, grounding: SignalGroundingPolicy | None = None) -> None:
        self._grounding = grounding or SignalGroundingPolicy()

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
                signal = self._signal(item, radar_id=radar_id, run_id=run_id)
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"signal-{index}-invalid:{exc}")
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

    def _signal(self, item: dict[str, Any], *, radar_id: str, run_id: str) -> ExtractedSourceSignal:
        signal_type = SignalType(str(item["type"]))
        title = self._required_text(item, "title", 300)
        summary = self._required_text(item, "summary", 1200)
        confidence = self._confidence(item.get("confidence"))
        refs = item.get("evidenceRefs")
        if not isinstance(refs, list) or not refs:
            raise ValueError("missing-evidenceRefs")
        evidence_refs = tuple(
            SignalEvidenceRef(
                material_id=self._required_text(ref, "materialId", 200),
                fragment_id=self._required_text(ref, "fragmentId", 240),
                quote=self._required_text(ref, "quote", 1000),
            )
            for ref in refs
            if isinstance(ref, dict)
        )
        if not evidence_refs:
            raise ValueError("empty-evidenceRefs")
        stable_source = "|".join(
            [radar_id, signal_type.value, self._canonical(title), *(f"{ref.material_id}:{ref.fragment_id}" for ref in evidence_refs)]
        )
        signal_id = f"signal-{hashlib.sha256(stable_source.encode('utf-8')).hexdigest()[:20]}"
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
            actors=self._string_list(item.get("actors"), item_limit=200, max_items=12),
            outcome=str(item.get("outcome") or "")[:1000],
            limitations=self._string_list(item.get("limitations"), item_limit=500, max_items=12),
            reason_codes=self._string_list(item.get("reasonCodes"), item_limit=120, max_items=20),
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
                    reason_codes=self._string_list(item.get("reasonCodes"), item_limit=120, max_items=20),
                )
            )
        for missing in sorted(expected - seen):
            errors.append(f"missing-material-decision:{missing}")
        return decisions

    def _required_text(self, value: dict[str, Any], key: str, limit: int) -> str:
        result = " ".join(str(value.get(key) or "").split())[:limit]
        if not result:
            raise ValueError(f"missing-{key}")
        return result

    def _confidence(self, value: Any) -> str:
        normalized = str(value or "low").strip().casefold()
        if normalized in {"low", "medium", "high"}:
            return normalized
        try:
            numeric = float(normalized.replace(",", "."))
        except ValueError as exc:
            raise ValueError(f"unknown-confidence:{normalized[:40]}") from exc
        if not 0 <= numeric <= 1:
            raise ValueError(f"unknown-confidence:{normalized[:40]}")
        return "high" if numeric >= 0.8 else ("medium" if numeric >= 0.5 else "low")

    def _string_list(self, value: Any, *, item_limit: int, max_items: int) -> tuple[str, ...]:
        values = [value] if isinstance(value, str) else (value if isinstance(value, (list, tuple)) else [])
        return tuple(
            normalized
            for item in values[:max_items]
            if (normalized := " ".join(str(item or "").split())[:item_limit])
        )

    def _canonical(self, value: str) -> str:
        return re.sub(r"[^a-zа-я0-9]+", " ", value.casefold()).strip()


__all__ = (
    "SignalExtractionPayloadError",
    "SignalExtractionPayloadMapper",
)
