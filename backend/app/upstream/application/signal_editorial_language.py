"""Owner: upstream.application

Used by: signal extraction payload validation before a provider result is accepted.
Does not own: provider retries, evidence grounding, project scoring, or UI localization.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from backend.app.upstream.domain.radar_language import SourceLanguageInspector
from backend.app.upstream.domain.signal_extraction_contracts import ExtractedSourceSignal


class SignalEditorialLanguagePolicy:
    def __init__(self, inspector: SourceLanguageInspector | None = None) -> None:
        self._inspector = inspector or SourceLanguageInspector()

    def validate(self, signal: ExtractedSourceSignal) -> list[str]:
        fields = {
            "title": signal.title,
            "summary": signal.summary,
            "uncertainty": signal.uncertainty,
            "mechanism": signal.mechanism,
            "outcome": signal.outcome,
        }
        fields.update({f"limitations[{index}]": value for index, value in enumerate(signal.limitations)})
        return [
            f"editorial-language-not-satisfied:{name}:{signal.editorial_language}"
            for name, value in fields.items()
            if value and not self._inspector.supports_editorial_language(value, signal.editorial_language)
        ]


__all__ = ("SignalEditorialLanguagePolicy",)
