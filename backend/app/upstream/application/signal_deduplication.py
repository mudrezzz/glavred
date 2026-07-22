"""Owner: upstream.application

Used by: accepted signal extraction attempts before report construction.
Does not own: provider mapping, grounding, project scoring, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from dataclasses import replace
import re

from backend.app.upstream.domain.signal_extraction_contracts import ExtractedSourceSignal


class SignalDeduplicationPolicy:
    def apply(self, signals: list[ExtractedSourceSignal]) -> list[ExtractedSourceSignal]:
        by_signature: dict[tuple[str, str], ExtractedSourceSignal] = {}
        for signal in signals:
            signature = (signal.signal_type.value, re.sub(r"\W+", " ", signal.title.casefold()).strip())
            existing = by_signature.get(signature)
            if existing is None:
                by_signature[signature] = signal
                continue
            by_signature[signature] = replace(
                existing,
                evidence_refs=tuple(dict.fromkeys((*existing.evidence_refs, *signal.evidence_refs))),
                reason_codes=tuple(dict.fromkeys((*existing.reason_codes, "multi-material-corroboration"))),
            )
        return list(by_signature.values())


__all__ = ("SignalDeduplicationPolicy",)
