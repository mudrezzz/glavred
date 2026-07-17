"""Owner: upstream.application

Used by: signal extraction payload mapping before accepting a candidate signal.
Does not own: provider transport, JSON schema mapping, deduplication, or scoring.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

from backend.app.upstream.application.signal_extraction_dossier import SignalExtractionDossier
from backend.app.upstream.domain.signal_extraction_contracts import ExtractedSourceSignal


class SignalGroundingPolicy:
    _NUMBER_OR_DATE = re.compile(r"\b\d[\d\s.,:/-]*\b")

    def validate(
        self, *, signal: ExtractedSourceSignal, dossier: SignalExtractionDossier,
    ) -> tuple[ExtractedSourceSignal | None, list[dict[str, Any]]]:
        violations: list[dict[str, Any]] = []
        legacy_evidence = False
        for ref in signal.evidence_refs:
            fragment = dossier.fragment_index.get((ref.material_id, ref.fragment_id))
            if fragment is None:
                violations.append(self._violation(signal.id, "unknown-evidence-handle", ref.fragment_id))
                continue
            fragment_text = self._normalize(str(fragment.get("text") or ""))
            quote = self._normalize(ref.quote)
            if not quote or quote not in fragment_text:
                violations.append(self._violation(signal.id, "quote-not-in-fragment", ref.fragment_id))
            if ref.material_id in dossier.legacy_material_ids:
                legacy_evidence = True

        evidence_text = " ".join(ref.quote for ref in signal.evidence_refs)
        claim_text = " ".join(
            [signal.title, signal.summary, signal.mechanism, signal.outcome, *signal.actors, *signal.limitations]
        )
        evidence_numbers = {self._normalize_number(item) for item in self._NUMBER_OR_DATE.findall(evidence_text)}
        for number in self._NUMBER_OR_DATE.findall(claim_text):
            if self._normalize_number(number) not in evidence_numbers:
                violations.append(self._violation(signal.id, "number-or-date-not-grounded", number.strip()))

        if violations:
            return None, violations
        if legacy_evidence and signal.confidence == "high":
            signal = replace(
                signal,
                confidence="medium",
                reason_codes=tuple(dict.fromkeys((*signal.reason_codes, "legacy-summary-confidence-capped"))),
            )
        return signal, []

    def _violation(self, signal_id: str, reason: str, detail: str) -> dict[str, Any]:
        return {"signalId": signal_id, "reasonCode": reason, "detail": detail[:180]}

    def _normalize(self, value: str) -> str:
        return " ".join(value.split()).casefold()

    def _normalize_number(self, value: str) -> str:
        return re.sub(r"\s+", "", value).strip(".,")


__all__ = ("SignalGroundingPolicy",)
