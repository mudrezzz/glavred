"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import re
from typing import Any

from backend.app.drafting.application.validation.draft_attribution_markers import DraftAttributionMarkerMatcher


class AttributionRequirementResolver:
    def __init__(self, marker_matcher: DraftAttributionMarkerMatcher | None = None) -> None:
        self._marker_matcher = marker_matcher or DraftAttributionMarkerMatcher()

    def normalize(self, requirements: list[Any], claims: list[dict[str, Any]]) -> dict[str, Any]:
        claims_by_id = {str(claim.get("id")): claim for claim in claims if claim.get("id")}
        claim_markers = {
            claim_id: self._marker_matcher.markers_for_claim(claim)
            for claim_id, claim in claims_by_id.items()
        }
        resolved: list[str] = []
        unresolved: list[dict[str, Any]] = []
        matches: list[dict[str, Any]] = []

        for requirement in requirements:
            explicit_claim_id = _explicit_claim_id(requirement)
            if explicit_claim_id:
                if explicit_claim_id in claims_by_id:
                    resolved.append(explicit_claim_id)
                    matches.append({"requirement": _requirement_text(requirement), "claimIds": [explicit_claim_id], "reason": "explicit-claim-id"})
                else:
                    unresolved.append({"requirement": _requirement_text(requirement), "claimId": explicit_claim_id, "reason": "claim-not-found"})
                continue

            text = _requirement_text(requirement)
            if not text:
                continue
            matched_ids = _match_claims_by_marker(text, claim_markers)
            if matched_ids:
                resolved.extend(matched_ids)
                matches.append({"requirement": text, "claimIds": matched_ids, "reason": "matched-source-marker"})
            else:
                unresolved.append({
                    "requirement": text,
                    "expectedMarkers": _extract_requirement_markers(text),
                    "reason": "unresolved-free-text-requirement",
                })

        return {
            "resolvedClaimIds": _unique(resolved),
            "requirementMatches": matches,
            "unresolvedAttributionRequirements": unresolved,
        }


def _explicit_claim_id(requirement: Any) -> str | None:
    row = requirement if isinstance(requirement, dict) else {}
    value = row.get("claimId") or row.get("claim_id") or row.get("id")
    return str(value) if value else None


def _requirement_text(requirement: Any) -> str:
    if isinstance(requirement, str):
        return requirement.strip()
    if isinstance(requirement, dict):
        return str(requirement.get("requirement") or requirement.get("text") or requirement.get("summary") or "").strip()
    return ""


def _match_claims_by_marker(text: str, claim_markers: dict[str, list[str]]) -> list[str]:
    text_lower = text.lower()
    text_compact = _compact(text)
    matched: list[str] = []
    for claim_id, markers in claim_markers.items():
        if any(_marker_in_text(marker, text_lower, text_compact) for marker in markers):
            matched.append(claim_id)
    return matched


def _marker_in_text(marker: str, text_lower: str, text_compact: str) -> bool:
    marker_lower = marker.lower()
    marker_compact = _compact(marker)
    if _has_word_boundary_marker(marker_lower, text_lower):
        return True
    return len(marker_compact) >= 8 and marker_compact in text_compact


def _extract_requirement_markers(text: str) -> list[str]:
    markers: list[str] = []
    for pattern in (
        r"(?i)(?:attribute(?:d)? to|source:|from|by)\s+([^,;.;\n]+)",
        r"(?i)(?:по данным|источник|из отч[её]та)\s+([^,;.;\n]+)",
    ):
        for match in re.finditer(pattern, text):
            marker = match.group(1).strip(" -–—:()[]")
            if marker and len(marker) >= 4:
                markers.append(marker)
    return _unique(markers)


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def _compact(value: str) -> str:
    return re.sub(r"[^a-z0-9а-яё]+", "", value.lower())


def _has_word_boundary_marker(marker: str, text: str) -> bool:
    if not marker.strip():
        return False
    if re.fullmatch(r"[a-z0-9а-яё.-]+", marker):
        return re.search(rf"(?<![a-z0-9а-яё]){re.escape(marker)}(?![a-z0-9а-яё])", text) is not None
    return marker in text
