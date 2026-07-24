"""Owner: upstream.application

Used by: signal quality checks and source-credibility consistency decisions.
Does not own: provider scoring, signal extraction, persistence, or UI rendering.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from backend.app.upstream.domain.signal_utility_types import (
    SignalClaimSupport,
    SignalSourcePosture,
)
from backend.app.upstream.domain.source_posture import SourcePostureAssessment


class SourcePosturePolicy:
    """Classifies ownership independently from cross-source claim support."""

    _INDEPENDENT_DOMAINS = {
        "acm.org", "arxiv.org", "doi.org", "ieee.org", "nature.com",
        "reuters.com", "sciencedirect.com", "springer.com",
    }
    _VENDOR_MARKERS = {
        "our platform", "our solution", "customer story", "request a demo",
        "наша платформа", "наше решение", "история клиента",
    }
    _GENERIC_OWNER_KEYS = {
        "www", "com", "org", "net", "io", "ai", "app", "cloud", "group",
        "systems", "solutions", "technology", "technologies",
    }

    def assess(self, signal: dict[str, Any]) -> SourcePostureAssessment:
        evidence = [
            item for item in signal.get("evidence", [])
            if isinstance(item, dict) and item.get("sourceUrl")
        ]
        domains = tuple(
            dict.fromkeys(
                domain for domain in (self._domain(str(item.get("sourceUrl") or "")) for item in evidence)
                if domain
            )
        )
        owner_keys = tuple(
            dict.fromkeys(
                owner_key
                for item in evidence
                if (
                    owner_key := self._normalized_owner(
                        str(item.get("publisherOwner") or item.get("ownerKey") or "")
                    )
                    or self._owner_key(self._domain(str(item.get("sourceUrl") or "")))
                )
            )
        )
        codes = {str(item).casefold() for item in signal.get("reasonCodes") or []}
        ownership, ownership_reason = self._ownership(signal, evidence, domains, owner_keys, codes)
        support, support_reason = self._claim_support(codes, owner_keys)
        return SourcePostureAssessment(
            ownership=ownership,
            claim_support=support,
            reason_codes=(ownership_reason, support_reason),
            source_domains=domains,
            owner_keys=owner_keys,
        )

    def _ownership(
        self,
        signal: dict[str, Any],
        evidence: list[dict[str, Any]],
        domains: tuple[str, ...],
        owner_keys: tuple[str, ...],
        codes: set[str],
    ) -> tuple[SignalSourcePosture, str]:
        if "source-vendor" in codes or "vendor-only" in codes:
            return SignalSourcePosture.VENDOR, "explicit-vendor-provenance"
        if "source-first-party" in codes:
            return SignalSourcePosture.FIRST_PARTY, "explicit-first-party-provenance"
        if domains and all(self._is_independent_domain(domain) for domain in domains):
            return SignalSourcePosture.INDEPENDENT, "independent-publisher-domain"

        source_text = " ".join(
            [
                str(signal.get("source") or ""),
                str(signal.get("title") or ""),
                *(str(item) for item in signal.get("actors") or []),
                *(str(item.get("sourceTitle") or "") for item in evidence),
            ]
        ).casefold()
        publisher_match = any(
            owner and re.search(rf"\b{re.escape(owner)}\b", source_text)
            for owner in owner_keys
        )
        if publisher_match:
            evidence_text = " ".join(
                f"{item.get('sourceTitle', '')} {item.get('quote', '')}"
                for item in evidence
            ).casefold()
            if any(marker in evidence_text for marker in self._VENDOR_MARKERS):
                return SignalSourcePosture.VENDOR, "publisher-product-promotional-relation"
            return SignalSourcePosture.FIRST_PARTY, "publisher-subject-identity-match"
        return SignalSourcePosture.UNKNOWN, "source-owner-not-resolved"

    def _claim_support(
        self,
        codes: set[str],
        owner_keys: tuple[str, ...],
    ) -> tuple[SignalClaimSupport, str]:
        if {"source-contradicted", "contradiction"} & codes:
            return SignalClaimSupport.CONTRADICTED, "contradicting-evidence-recorded"
        if len(set(owner_keys)) >= 2:
            return SignalClaimSupport.CORROBORATED, "multiple-independent-owner-keys"
        if owner_keys:
            return SignalClaimSupport.SINGLE_SOURCE, "single-source-owner"
        return SignalClaimSupport.NOT_CHECKED, "no-resolvable-source-owner"

    def _domain(self, value: str) -> str:
        hostname = (urlparse(value).hostname or "").casefold().removeprefix("www.")
        return hostname

    def _owner_key(self, domain: str) -> str:
        labels = [item for item in domain.split(".") if item]
        for label in reversed(labels[:-1] or labels):
            normalized = re.sub(r"[^a-z0-9]+", "", label.casefold())
            if normalized and normalized not in self._GENERIC_OWNER_KEYS:
                return normalized
        return labels[0] if labels else ""

    def _normalized_owner(self, value: str) -> str:
        return re.sub(r"[^a-z0-9а-яё]+", "", value.casefold())

    def _is_independent_domain(self, domain: str) -> bool:
        return (
            domain.endswith(".gov")
            or domain.endswith(".edu")
            or any(domain == item or domain.endswith(f".{item}") for item in self._INDEPENDENT_DOMAINS)
        )


__all__ = ("SourcePosturePolicy",)
