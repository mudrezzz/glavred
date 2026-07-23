"""Owner: upstream.application

Used by: signal extraction dossier construction.
Does not own: provider calls, material selection, grounding, or project utility scoring.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any


class SignalExtractionContractFactory:
    """Builds the provider-visible extraction and localization contract."""

    def build(self, *, editorial_language: str) -> dict[str, Any]:
        return {
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
            "editorialLanguage": editorial_language,
            "editorialLanguageFields": ["title", "summary", "uncertainty", "mechanism", "outcome", "limitations"],
            "preserveOriginalFields": ["sourceTitle", "evidenceRefs.quote"],
            "groundingRules": {
                "evidenceQuote": "exact-contiguous-fragment-substring",
                "editorialNumbersAndDates": "must-occur-in-signal-evidence-quotes",
                "invalidSignal": "omit-instead-of-relaxing-contract",
            },
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
            "forbiddenOwnership": [
                "suggestedTopicId", "suggestedFabulaId", "audience", "value", "goal", "platform", "channel",
            ],
        }


__all__ = ("SignalExtractionContractFactory",)
