"""Owner: upstream.application

Used by: RadarRun search triage to form stable duplicate groups and representatives.
Does not own: provider search, score calculation, read execution, persistence, or UI rendering.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256

from backend.app.upstream.domain.search_triage_contracts import (
    SearchDuplicateGroup,
    SearchResultCandidate,
    SearchResultDimensionScores,
)


class SearchDuplicateGroupingPolicy:
    def group(
        self,
        candidates: list[SearchResultCandidate],
        scores: dict[str, SearchResultDimensionScores],
    ) -> list[SearchDuplicateGroup]:
        valid = sorted((item for item in candidates if item.valid), key=self._candidate_key)
        parent = {item.id: item.id for item in valid}
        by_url: dict[str, list[str]] = defaultdict(list)
        by_fingerprint: dict[str, list[str]] = defaultdict(list)
        by_id = {item.id: item for item in valid}

        for candidate in valid:
            by_url[candidate.canonical_url].append(candidate.id)
            if candidate.fingerprint:
                by_fingerprint[candidate.fingerprint].append(candidate.id)
        for bucket in (*by_url.values(), *by_fingerprint.values()):
            if len(bucket) < 2:
                continue
            first = bucket[0]
            for candidate_id in bucket[1:]:
                self._union(parent, first, candidate_id)

        grouped: dict[str, list[SearchResultCandidate]] = defaultdict(list)
        for candidate in valid:
            grouped[self._find(parent, candidate.id)].append(candidate)

        result: list[SearchDuplicateGroup] = []
        for members in grouped.values():
            ordered = sorted(members, key=self._candidate_key)
            representative = min(
                ordered,
                key=lambda item: (-scores[item.id].total, self._candidate_key(item)),
            )
            urls = {item.canonical_url for item in ordered}
            fingerprints = {item.fingerprint for item in ordered if item.fingerprint}
            reasons: list[str] = []
            if len(ordered) > 1 and len(urls) < len(ordered):
                reasons.append("canonical-url")
            if len(ordered) > 1 and len(fingerprints) < len(ordered):
                reasons.append("content-fingerprint")
            group_seed = "|".join(sorted(item.canonical_url or item.fingerprint for item in ordered))
            result.append(
                SearchDuplicateGroup(
                    id=f"duplicate-group-{sha256(group_seed.encode('utf-8')).hexdigest()[:16]}",
                    representative_candidate_id=representative.id,
                    candidate_ids=tuple(item.id for item in ordered),
                    raw_result_ids=tuple(item.raw_result_id for item in ordered),
                    query_ids=self._unique(item.query_id for item in ordered),
                    intent_ids=self._unique(item.intent_id for item in ordered),
                    families=self._unique(item.family for item in ordered),
                    evidence_types=self._unique(item.evidence_type for item in ordered),
                    domains=self._unique(item.domain for item in ordered),
                    match_reasons=tuple(reasons or ["unique-result"]),
                )
            )
        return sorted(result, key=lambda item: item.id)

    def _candidate_key(self, candidate: SearchResultCandidate) -> tuple[str, str, str, str]:
        return (
            candidate.canonical_url,
            candidate.title.casefold(),
            candidate.query_id,
            candidate.raw_result_id,
        )

    def _unique(self, values) -> tuple[str, ...]:
        return tuple(sorted({str(value) for value in values if value}))

    def _find(self, parent: dict[str, str], item: str) -> str:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def _union(self, parent: dict[str, str], left: str, right: str) -> None:
        left_root = self._find(parent, left)
        right_root = self._find(parent, right)
        if left_root == right_root:
            return
        first, second = sorted((left_root, right_root))
        parent[second] = first


__all__ = ("SearchDuplicateGroupingPolicy",)
