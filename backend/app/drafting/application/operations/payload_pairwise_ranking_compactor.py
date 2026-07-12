"""Owner: drafting.application.operations

Used by: pairwise-ranking payload budget compaction before prompt construction.
Does not own: candidate selection, ranking identity validation, or provider transport.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


class PairwiseRankingPayloadCompactor:
    """Keeps candidate projections symmetric and leaves room for prompt instructions."""

    TARGET_PROVIDER_INPUT_CHARS = 19_000

    def compact(self, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
        compact = dict(payload)
        trimmed: dict[str, int] = {}
        candidates = [dict(item) for item in self._list(compact.get("candidates")) if isinstance(item, Mapping)]
        compact["candidates"] = [self._candidate(item, 200) for item in candidates]
        issues = [self._issue(item) for item in self._list(compact.get("validationIssues")) if isinstance(item, Mapping)]
        compact["validationIssues"] = issues
        if self._size(compact) <= self.TARGET_PROVIDER_INPUT_CHARS:
            return compact, trimmed

        # Equal window reductions preserve comparison fairness across every candidate.
        for limit in (160, 120, 80):
            compact["candidates"] = [self._candidate(item, limit) for item in candidates]
            trimmed["pairwiseRanking.candidateWindows"] = len(candidates)
            if self._size(compact) <= self.TARGET_PROVIDER_INPUT_CHARS:
                return compact, trimmed

        # Optional evidence is removed only after all candidate windows were reduced equally.
        evidence = self._list(compact.get("evidence"))
        if evidence:
            compact["evidence"] = []
            trimmed["pairwiseRanking.evidence"] = len(evidence)
        return compact, trimmed

    def _candidate(self, candidate: Mapping[str, Any], text_limit: int) -> dict[str, Any]:
        result = {
            key: candidate.get(key)
            for key in ("id", "title", "rhetoricalPlanId", "bodyChars", "paragraphCount")
            if candidate.get(key) not in (None, "")
        }
        windows = candidate.get("bodyWindows")
        if isinstance(windows, Mapping):
            result["bodyWindows"] = {
                str(key): str(value or "")[:text_limit]
                for key, value in sorted(windows.items())
                if value
            }
        for key in ("usedEvidence", "ruleCoverage"):
            result[key] = [str(value)[:120] for value in self._list(candidate.get(key))[:8]]
        for key in ("risks", "weaknesses"):
            result[key] = [str(value)[:120] for value in self._list(candidate.get(key))[:1]]
        return {key: value for key, value in result.items() if value not in (None, "", [], {})}

    def _issue(self, issue: Mapping[str, Any]) -> dict[str, Any]:
        result = {key: issue.get(key) for key in ("candidateId", "findingCount") if issue.get(key) not in (None, "")}
        findings = [item for item in self._list(issue.get("findings")) if isinstance(item, Mapping)]
        if findings:
            finding = findings[0]
            result["findings"] = [{
                **{key: finding.get(key) for key in ("id", "candidateId", "source", "validatorId", "severity") if finding.get(key)},
                "message": str(finding.get("message") or "")[:140],
                "repairGuidance": str(finding.get("repairGuidance") or "")[:120],
                "evidenceExcerpt": str(finding.get("evidenceExcerpt") or "")[:80],
            }]
        return {key: value for key, value in result.items() if value not in (None, "", [], {})}

    def _size(self, value: Any) -> int:
        return len(json.dumps(value, ensure_ascii=False, sort_keys=True))

    def _list(self, value: Any) -> list[Any]:
        return value if isinstance(value, list) else []


__all__ = ("PairwiseRankingPayloadCompactor",)
