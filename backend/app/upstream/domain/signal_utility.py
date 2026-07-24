"""Owner: upstream.domain

Used by: signal utility profile, dossier, scoring, decision, and API presenters.
Does not own: provider transport, workspace persistence, human review, or candidate assembly.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from backend.app.upstream.domain.signal_relationship import SignalRelationship, SignalRelationshipReport
from backend.app.upstream.domain.signal_utility_explainability import SignalQualityCheck, SignalUtilityCriterionResult
from backend.app.upstream.domain.signal_utility_types import (
    SignalCriterionEffect,
    SignalCriterionOrigin,
    SignalClaimSupport,
    SignalRelationshipKind,
    SignalResultSupport,
    SignalSourcePosture,
    SignalUtilityDimension,
    SignalUtilityImportance,
    SignalUtilityRecommendation,
    SignalUtilityStatus,
)


@dataclass(frozen=True)
class ProjectEditorialSetting:
    id: str
    kind: str
    title: str
    statement: str
    mode: str = "shouldMatch"
    dimension: str | None = None
    origin: str = "project"

    def to_payload(self) -> dict[str, str]:
        return {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "statement": self.statement,
            "mode": self.mode,
            "dimension": self.dimension,
            "origin": self.origin,
        }


@dataclass(frozen=True)
class ProjectEditorialOpportunityProfile:
    project_id: str
    editorial_language: str
    project_summary: str
    settings: tuple[ProjectEditorialSetting, ...]
    history_fingerprints: tuple[dict[str, str], ...]
    retained_counts: dict[str, int]
    trimmed_counts: dict[str, int]

    def to_payload(self) -> dict[str, Any]:
        return {
            "projectId": self.project_id,
            "editorialLanguage": self.editorial_language,
            "projectSummary": self.project_summary,
            "settings": [item.to_payload() for item in self.settings],
            "historyFingerprints": list(self.history_fingerprints),
        }


@dataclass(frozen=True)
class SignalUtilityDossier:
    provider_input: dict[str, Any]
    signal_ids: tuple[str, ...]
    setting_ids: frozenset[str]
    evidence_keys: frozenset[str]
    readiness: str
    missing_inputs: tuple[str, ...] = ()
    suppressed_fields: tuple[str, ...] = ()
    retained_counts: dict[str, int] = field(default_factory=dict)
    trimmed_counts: dict[str, int] = field(default_factory=dict)
    relationship_pair_ids: frozenset[str] = frozenset()

    def trace_payload(self) -> dict[str, Any]:
        return {
            "profileId": "signal-utility-dossier-v2",
            "runtimeMigrated": True,
            "readiness": self.readiness,
            "signalIds": list(self.signal_ids),
            "settingHandleCount": len(self.setting_ids),
            "evidenceHandleCount": len(self.evidence_keys),
            "relationshipPairCount": len(self.relationship_pair_ids),
            "missingInputs": list(self.missing_inputs),
            "suppressedFields": list(self.suppressed_fields),
            "retainedCounts": self.retained_counts,
            "trimmedCounts": self.trimmed_counts,
            "qualityRisk": "high" if self.readiness == "BLOCKED" else "none",
        }


@dataclass(frozen=True)
class SignalUtilityDimensionResult:
    dimension: SignalUtilityDimension
    status: SignalUtilityStatus
    importance: SignalUtilityImportance
    summary: str
    reason_codes: tuple[str, ...]
    setting_refs: tuple[str, ...] = ()
    evidence_refs: tuple[dict[str, str], ...] = ()
    uncertainty: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension.value,
            "status": self.status.value,
            "importance": self.importance.value,
            "summary": self.summary,
            "reasonCodes": list(self.reason_codes),
            "settingRefs": list(self.setting_refs),
            "evidenceRefs": list(self.evidence_refs),
            "uncertainty": self.uncertainty,
        }


@dataclass(frozen=True)
class SignalUtilityEvaluation:
    signal_id: str
    recommendation: SignalUtilityRecommendation
    dimensions: tuple[SignalUtilityDimensionResult, ...]
    blocking_reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    radar_criteria: tuple[SignalUtilityCriterionResult, ...] = ()
    project_criteria: tuple[SignalUtilityCriterionResult, ...] = ()
    quality_checks: tuple[SignalQualityCheck, ...] = ()
    not_applicable_settings: tuple[dict[str, str], ...] = ()
    relationship_report: SignalRelationshipReport | None = None

    def to_payload(self, *, revision: int) -> dict[str, Any]:
        return {
            "version": 2,
            "revision": revision,
            "status": "complete" if self.recommendation != SignalUtilityRecommendation.INCONCLUSIVE else "inconclusive",
            "recommendation": self.recommendation.value,
            "dimensions": [item.to_payload() for item in self.dimensions],
            "blockingReasons": list(self.blocking_reasons),
            "warnings": list(self.warnings),
            "evaluationPlanVersion": 2,
            "radarCriteria": [item.to_payload() for item in self.radar_criteria],
            "projectCriteria": [item.to_payload() for item in self.project_criteria],
            "qualityChecks": [item.to_payload() for item in self.quality_checks],
            "notApplicableSettings": list(self.not_applicable_settings),
            "relationshipReport": self.relationship_report.to_payload() if self.relationship_report else None,
        }


__all__ = (
    "ProjectEditorialOpportunityProfile",
    "ProjectEditorialSetting",
    "SignalUtilityDimension",
    "SignalUtilityDimensionResult",
    "SignalUtilityDossier",
    "SignalUtilityEvaluation",
    "SignalUtilityImportance",
    "SignalUtilityRecommendation",
    "SignalUtilityStatus",
    "SignalCriterionEffect",
    "SignalCriterionOrigin",
    "SignalClaimSupport",
    "SignalQualityCheck",
    "SignalRelationship",
    "SignalRelationshipKind",
    "SignalRelationshipReport",
    "SignalResultSupport",
    "SignalSourcePosture",
    "SignalUtilityCriterionResult",
)
