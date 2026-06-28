import re
from typing import Any


GENERIC_MARKERS = set("about article blog case data demo discovery guide news post product publicevidence report research source study survey trust".split())

class DraftAttributionMarkerMatcher:
    def evaluate(self, *, body: str, claims: list[dict[str, Any]], claim_ids: list[str]) -> dict[str, Any]:
        body_lower = body.lower()
        body_compact = _compact(body)
        claims_by_id = {str(claim.get("id")): claim for claim in claims if claim.get("id")}
        expected: dict[str, list[str]] = {}
        matched: dict[str, list[str]] = {}
        missing: list[str] = []
        unresolvable: list[str] = []

        for claim_id in claim_ids:
            markers = attribution_markers_for_claim(claims_by_id.get(claim_id, {}))
            expected[claim_id] = markers
            if not markers:
                unresolvable.append(claim_id)
                continue
            matches = [marker for marker in markers if _marker_matches(marker, body_lower, body_compact)]
            if matches:
                matched[claim_id] = matches
            else:
                missing.append(claim_id)

        return {
            "expectedAttributionMarkers": expected,
            "matchedAttributionMarkers": matched,
            "matchedClaimIds": sorted(matched),
            "missingClaimIds": missing,
            "unresolvableClaimIds": unresolvable,
        }

def attribution_markers_for_claim(claim: dict[str, Any]) -> list[str]:
    provenance = _dict(claim.get("provenance"))
    raw_markers = [
        claim.get("source"),
        provenance.get("source"),
        provenance.get("sourceTitle"),
        provenance.get("sourceUrl"),
    ]
    markers: list[str] = []
    for marker in raw_markers:
        markers.extend(_source_markers(str(marker or "")))
    return _unique([marker for marker in markers if _is_useful_marker(marker)])

def _source_markers(value: str) -> list[str]:
    if not value.strip():
        return []
    markers = [value.strip()]
    if value.startswith(("http://", "https://")):
        host = _domain(value)
        markers.extend([host, host.removeprefix("www.")])
        markers.extend(host.split(".")[:1])
    markers.extend(_title_name_markers(value))
    return markers

def _title_name_markers(value: str) -> list[str]:
    tokens = re.findall(r"\b[A-Z][A-Za-z0-9&.-]{1,}\b", value)
    markers: list[str] = []
    run: list[str] = []
    for token in tokens:
        if token.lower().strip(".") in GENERIC_MARKERS:
            if len(run) >= 2:
                markers.append(" ".join(run))
            run = []
            continue
        run.append(token.strip("."))
    if len(run) >= 2:
        markers.append(" ".join(run))
    return markers

def _marker_matches(marker: str, body_lower: str, body_compact: str) -> bool:
    marker_lower = marker.lower()
    marker_compact = _compact(marker)
    if _has_word_boundary_marker(marker_lower, body_lower):
        return True
    return len(marker_compact) >= 8 and marker_compact in body_compact

def _is_useful_marker(marker: str) -> bool:
    normalized = marker.lower().strip(" /.,:;()[]")
    if len(normalized) < 4 or normalized in GENERIC_MARKERS:
        return False
    return True

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

def _domain(url: str) -> str:
    return url.replace("https://", "").replace("http://", "").split("/")[0]

def _has_word_boundary_marker(marker: str, text: str) -> bool:
    if not marker.strip():
        return False
    if re.fullmatch(r"[a-z0-9а-яё.-]+", marker):
        return re.search(rf"(?<![a-z0-9а-яё]){re.escape(marker)}(?![a-z0-9а-яё])", text) is not None
    return marker in text

def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
