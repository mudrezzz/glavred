"""Owner: drafting.application.operations

Used by: Payload budget compactors for shared counters and value helpers.
Does not own: Operation-specific compaction policy or provider messages.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

import json
from typing import Any, Mapping


class PayloadBudgetCounters:
    @staticmethod
    def sent_counts(payload: Mapping[str, Any]) -> dict[str, int]:
        blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return {
            "rules": blob.count('"validatorType"') + blob.count('"ruleIds"'),
            "claims": blob.count('"statement"') + blob.count('"claimIds"'),
            "evidenceItems": blob.count('"sourceUrl"') + blob.count('"sourceTitle"'),
            "candidates": blob.count('"body"') + blob.count('"candidateId"'),
            "sourceSnippets": blob.count('"snippet"'),
            "priorDrafts": blob.count('"baseCandidateId"'),
        }


class CountAccumulator:
    @staticmethod
    def merge(target: dict[str, int], source: Mapping[str, int]) -> None:
        for key, value in source.items():
            target[key] = target.get(key, 0) + int(value)

    @staticmethod
    def trimmed(target: dict[str, int], key: str, original_count: int, sent_count: int) -> None:
        target[key] = target.get(key, 0) + max(0, original_count - sent_count)


def _drop_empty(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value not in (None, "", [], {})}


def _pick(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys if key in payload and payload[key] not in (None, "", [], {})}


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
