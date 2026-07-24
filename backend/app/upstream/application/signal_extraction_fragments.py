"""Owner: upstream.application

Used by: URL-read payload construction and legacy extraction replay.
Does not own: URL transport, provider extraction, signal grounding, or scoring.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


class FoundMaterialFragmentPolicy:
    MAX_FRAGMENTS = 8
    MAX_FRAGMENT_CHARS = 1200

    def from_read_text(
        self,
        *,
        material_id: str,
        text: str,
        focus_text: str | None = None,
    ) -> list[dict[str, Any]]:
        normalized = " ".join(str(text).split())
        if not normalized:
            return []
        fragments: list[dict[str, Any]] = []
        cursor = 0
        chunks = self._chunks(normalized)
        selected_indexes = self._selected_indexes(chunks, focus_text)
        for index in selected_indexes:
            chunk = chunks[index]
            ordinal = index + 1
            start = normalized.find(chunk, cursor)
            if start < 0:
                start = normalized.find(chunk)
            if start < 0:
                start = 0
            end = start + len(chunk)
            cursor = max(cursor, end)
            digest = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
            fragments.append(
                {
                    "id": f"{material_id}-fragment-{ordinal}-{digest[:10]}",
                    "ordinal": ordinal,
                    "text": chunk,
                    "startChar": start,
                    "endChar": end,
                    "hash": digest,
                    "kind": "text",
                }
            )
        return fragments

    def _selected_indexes(
        self,
        chunks: list[str],
        focus_text: str | None,
    ) -> list[int]:
        if len(chunks) <= self.MAX_FRAGMENTS or not focus_text:
            return list(range(min(len(chunks), self.MAX_FRAGMENTS)))
        focus_terms = self._terms(focus_text)
        if not focus_terms:
            return list(range(self.MAX_FRAGMENTS))
        scored = [
            (len(focus_terms.intersection(self._terms(chunk))), index)
            for index, chunk in enumerate(chunks)
        ]
        selected = [
            index
            for score, index in sorted(scored, key=lambda item: (-item[0], item[1]))[
                : self.MAX_FRAGMENTS
            ]
            if score > 0
        ]
        if not selected:
            return list(range(self.MAX_FRAGMENTS))
        return sorted(selected)

    def _terms(self, value: str) -> set[str]:
        return {
            term
            for term in re.findall(r"[\w]+", str(value).casefold(), flags=re.UNICODE)
            if len(term) >= 4
        }

    def legacy_summary(self, material: dict[str, Any]) -> list[dict[str, Any]]:
        summary = " ".join(str(material.get("summary") or "").split())[: self.MAX_FRAGMENT_CHARS]
        if not summary:
            return []
        material_id = str(material.get("id") or "legacy-material")
        digest = hashlib.sha256(summary.encode("utf-8")).hexdigest()
        return [
            {
                "id": f"{material_id}-legacy-summary-{digest[:10]}",
                "ordinal": 1,
                "text": summary,
                "startChar": 0,
                "endChar": len(summary),
                "hash": digest,
                "kind": "legacySummary",
            }
        ]

    def _chunks(self, normalized: str) -> list[str]:
        sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", normalized) if item.strip()]
        chunks: list[str] = []
        current = ""
        for sentence in sentences or [normalized]:
            for piece in self._bounded_pieces(sentence):
                candidate = f"{current} {piece}".strip()
                if current and len(candidate) > self.MAX_FRAGMENT_CHARS:
                    chunks.append(current)
                    current = piece
                else:
                    current = candidate
        if current:
            chunks.append(current)
        return chunks

    def _bounded_pieces(self, value: str) -> list[str]:
        return [value[index : index + self.MAX_FRAGMENT_CHARS] for index in range(0, len(value), self.MAX_FRAGMENT_CHARS)]


__all__ = ("FoundMaterialFragmentPolicy",)
