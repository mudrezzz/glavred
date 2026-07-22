"""Owner: upstream.application

Used by: SignalExtractionDossierFactory to enforce the whole-dossier character cap.
Does not own: material eligibility, provider calls, grounding, or project scoring.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SignalExtractionCompactionResult:
    provider_input: dict[str, Any]
    trimmed_fragment_count: int
    trimmed_context_count: int


class SignalExtractionDossierCompactor:
    MIN_FRAGMENT_CHARS = 120
    MIN_CONTEXT_CHARS = 80

    def compact(self, provider_input: dict[str, Any], *, max_chars: int) -> SignalExtractionCompactionResult:
        payload = copy.deepcopy(provider_input)
        original_fragment_lengths = self._fragment_lengths(payload)
        original_context_lengths = self._context_lengths(payload)
        while self._size(payload) > max_chars:
            target = self._longest_fragment(payload)
            if target is None:
                target = self._longest_context(payload)
            if target is None:
                break
            owner, key, minimum = target
            value = str(owner.get(key) or "")
            owner[key] = value[: max(minimum, len(value) - max(40, len(value) // 5))].rstrip()
        return SignalExtractionCompactionResult(
            provider_input=payload,
            trimmed_fragment_count=self._changed_count(original_fragment_lengths, self._fragment_lengths(payload)),
            trimmed_context_count=self._changed_count(original_context_lengths, self._context_lengths(payload)),
        )

    def _longest_fragment(self, payload: dict[str, Any]) -> tuple[dict[str, Any], str, int] | None:
        candidates = [
            fragment
            for material in payload.get("materials", [])
            for fragment in material.get("fragments", [])
            if len(str(fragment.get("text") or "")) > self.MIN_FRAGMENT_CHARS
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda item: len(str(item.get("text") or ""))), "text", self.MIN_FRAGMENT_CHARS

    def _longest_context(self, payload: dict[str, Any]) -> tuple[dict[str, Any], str, int] | None:
        context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
        candidates: list[tuple[dict[str, Any], str, int]] = []
        if len(str(context.get("scope") or "")) > self.MIN_CONTEXT_CHARS:
            candidates.append((context, "scope", self.MIN_CONTEXT_CHARS))
        candidates.extend(
            (item, key, self.MIN_CONTEXT_CHARS)
            for collection, key in ((context.get("rules", []), "statement"), (context.get("filters", []), "instruction"))
            for item in collection
            if isinstance(item, dict) and len(str(item.get(key) or "")) > self.MIN_CONTEXT_CHARS
        )
        return max(candidates, key=lambda item: len(str(item[0].get(item[1]) or ""))) if candidates else None

    def _fragment_lengths(self, payload: dict[str, Any]) -> dict[str, int]:
        return {
            f"{material.get('id')}:{fragment.get('id')}": len(str(fragment.get("text") or ""))
            for material in payload.get("materials", [])
            for fragment in material.get("fragments", [])
        }

    def _context_lengths(self, payload: dict[str, Any]) -> dict[str, int]:
        context = payload.get("context") if isinstance(payload.get("context"), dict) else {}
        values = {"scope": len(str(context.get("scope") or ""))}
        for collection, key in ((context.get("rules", []), "statement"), (context.get("filters", []), "instruction")):
            values.update({f"{key}:{item.get('id')}": len(str(item.get(key) or "")) for item in collection if isinstance(item, dict)})
        return values

    def _changed_count(self, before: dict[str, int], after: dict[str, int]) -> int:
        return sum(1 for key, value in before.items() if after.get(key, value) < value)

    def _size(self, payload: dict[str, Any]) -> int:
        return len(json.dumps(payload, ensure_ascii=False, sort_keys=True))


__all__ = ("SignalExtractionCompactionResult", "SignalExtractionDossierCompactor")
