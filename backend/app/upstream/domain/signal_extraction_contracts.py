"""Owner: upstream.domain

Used by: upstream signal extraction application services and API serializers.
Does not own: provider transport, project utility scoring, candidate assembly, or UI.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import hashlib
from typing import Any


class SignalType(StrEnum):
    EVENT_FACT = "eventFact"
    CHANGE = "change"
    AUDIENCE_QUESTION = "audienceQuestion"
    TENSION_COUNTERARGUMENT = "tensionCounterargument"
    CASE = "case"
    DATA_POINT = "dataPoint"
    PRACTICE = "practice"
    PROBLEM_FAILURE_MODE = "problemFailureMode"
    PERSONAL_OBSERVATION = "personalObservation"
    RECURRING_PATTERN = "recurringPattern"


class MaterialExtractionDecision(StrEnum):
    SIGNAL_PRODUCING = "signalProducing"
    INSUFFICIENT = "insufficient"
    DUPLICATE = "duplicate"
    CORROBORATING = "corroborating"
    CONTRADICTION = "contradiction"
    NOISE = "noise"
    EXTRACTION_FAILED = "extractionFailed"


@dataclass(frozen=True)
class SignalEvidenceRef:
    material_id: str
    fragment_id: str
    quote: str

    def to_payload(self) -> dict[str, Any]:
        return {"materialId": self.material_id, "fragmentId": self.fragment_id, "quote": self.quote}


@dataclass(frozen=True)
class ExtractedSourceSignal:
    id: str
    radar_id: str
    run_id: str
    signal_type: SignalType
    title: str
    summary: str
    confidence: str
    uncertainty: str
    evidence_refs: tuple[SignalEvidenceRef, ...]
    mechanism: str = ""
    actors: tuple[str, ...] = ()
    outcome: str = ""
    limitations: tuple[str, ...] = ()
    reason_codes: tuple[str, ...] = ()
    editorial_language: str = "ru"
    source_language: str = "unknown"
    localization_status: str = "unverified"
    localization_reason_codes: tuple[str, ...] = ()

    def to_payload(self, materials_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
        evidence = []
        for ref in self.evidence_refs:
            material = materials_by_id.get(ref.material_id, {})
            evidence_seed = f"{self.id}|{ref.material_id}|{ref.fragment_id}|{ref.quote}"
            evidence_id = hashlib.sha256(evidence_seed.encode("utf-8")).hexdigest()[:20]
            evidence.append(
                {
                    "id": f"evidence-{evidence_id}",
                    "materialId": ref.material_id,
                    "fragmentId": ref.fragment_id,
                    "sourceTitle": str(material.get("title") or ref.material_id),
                    "sourceUrl": str(material.get("locator") or ""),
                    "quote": ref.quote,
                    "summary": self.summary,
                }
            )
        evidence_materials = [materials_by_id.get(ref.material_id, {}) for ref in self.evidence_refs]
        return {
            "id": self.id,
            "type": self.signal_type.value,
            "title": self.title,
            "source": ", ".join(dict.fromkeys(item["sourceTitle"] for item in evidence)),
            "capturedAt": max((str(item.get("capturedAt") or "") for item in evidence_materials), default=""),
            "summary": self.summary,
            "rawNote": self.mechanism or self.outcome or self.summary,
            "evidence": evidence,
            "evidenceRefs": [item.to_payload() for item in self.evidence_refs],
            "radarId": self.radar_id,
            "radarRunId": self.run_id,
            "reviewStatus": "candidate",
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "mechanism": self.mechanism,
            "actors": list(self.actors),
            "outcome": self.outcome,
            "limitations": list(self.limitations),
            "provenance": {"materialIds": list(dict.fromkeys(ref.material_id for ref in self.evidence_refs))},
            "reasonCodes": list(self.reason_codes),
            "editorialLanguage": self.editorial_language,
            "sourceLanguage": self.source_language,
            "localizationStatus": self.localization_status,
            "localizationReasonCodes": list(self.localization_reason_codes),
        }


@dataclass(frozen=True)
class MaterialDecisionRecord:
    material_id: str
    decision: MaterialExtractionDecision
    reason_codes: tuple[str, ...]
    signal_ids: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        return {
            "materialId": self.material_id,
            "decision": self.decision.value,
            "reasonCodes": list(self.reason_codes),
            "signalIds": list(self.signal_ids),
        }


@dataclass(frozen=True)
class SignalExtractionOutcome:
    status: str
    signals: tuple[ExtractedSourceSignal, ...]
    decisions: tuple[MaterialDecisionRecord, ...]
    attempts: tuple[dict[str, Any], ...]
    grounding_violations: tuple[dict[str, Any], ...] = ()
    warnings: tuple[str, ...] = ()
    revision: int = 1
    prior_revisions: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    def report_payload(self) -> dict[str, Any]:
        decision_counts = {value.value: 0 for value in MaterialExtractionDecision}
        for decision in self.decisions:
            decision_counts[decision.decision.value] += 1
        return {
            "status": self.status,
            "revision": self.revision,
            "revisions": [*self.prior_revisions, {"revision": self.revision, "status": self.status}],
            "materialDecisions": [item.to_payload() for item in self.decisions],
            "decisionCounts": decision_counts,
            "signalIds": [item.id for item in self.signals],
            "signalCount": len(self.signals),
            "providerAttempts": list(self.attempts),
            "groundingViolations": list(self.grounding_violations),
            "warnings": list(self.warnings),
            "decisionCoverageComplete": len({item.material_id for item in self.decisions}) == len(self.decisions),
        }


__all__ = (
    "ExtractedSourceSignal",
    "MaterialDecisionRecord",
    "MaterialExtractionDecision",
    "SignalEvidenceRef",
    "SignalExtractionOutcome",
    "SignalType",
)
