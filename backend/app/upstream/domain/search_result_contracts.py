"""Owner: upstream.domain

Used by: deterministic RadarRun result normalization, scoring, duplicate grouping, and trace.
Does not own: provider transport, URL reading, read allocation, persistence, or signals.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SearchResultCandidate:
    id: str
    raw_result_id: str
    source_handle_id: str
    query_id: str
    intent_id: str
    family: str
    evidence_type: str
    title: str
    url: str
    canonical_url: str
    snippet: str
    domain: str
    query: str
    provider: str
    fingerprint: str
    valid: bool = True
    invalid_reason: str | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.id,
            "rawResultId": self.raw_result_id,
            "sourceHandleId": self.source_handle_id,
            "queryId": self.query_id,
            "intentId": self.intent_id,
            "family": self.family,
            "evidenceType": self.evidence_type,
            "title": self.title,
            "url": self.url,
            "canonicalUrl": self.canonical_url,
            "snippet": self.snippet,
            "domain": self.domain,
            "provider": self.provider,
            "fingerprint": self.fingerprint,
            "valid": self.valid,
        }
        if self.invalid_reason:
            payload["invalidReason"] = self.invalid_reason
        return payload


@dataclass(frozen=True)
class SearchResultDimensionScores:
    relevance: int
    evidence_fit: int
    project_fit: int
    source_quality: int
    novelty: int
    noise_risk: int
    total: int
    reason_codes: tuple[str, ...] = ()
    explanation: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "relevance": self.relevance,
            "evidenceFit": self.evidence_fit,
            "projectFit": self.project_fit,
            "sourceQuality": self.source_quality,
            "novelty": self.novelty,
            "noiseRisk": self.noise_risk,
            "total": self.total,
            "reasonCodes": list(self.reason_codes),
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class SearchDuplicateGroup:
    id: str
    representative_candidate_id: str
    candidate_ids: tuple[str, ...]
    raw_result_ids: tuple[str, ...]
    query_ids: tuple[str, ...]
    intent_ids: tuple[str, ...]
    families: tuple[str, ...]
    evidence_types: tuple[str, ...]
    domains: tuple[str, ...]
    match_reasons: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "representativeCandidateId": self.representative_candidate_id,
            "candidateIds": list(self.candidate_ids),
            "rawResultIds": list(self.raw_result_ids),
            "queryIds": list(self.query_ids),
            "intentIds": list(self.intent_ids),
            "families": list(self.families),
            "evidenceTypes": list(self.evidence_types),
            "domains": list(self.domains),
            "matchReasons": list(self.match_reasons),
        }


__all__ = ("SearchDuplicateGroup", "SearchResultCandidate", "SearchResultDimensionScores")
