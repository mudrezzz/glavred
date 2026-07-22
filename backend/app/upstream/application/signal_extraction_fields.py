"""Owner: upstream.application

Used by: signal extraction payload mapping for bounded scalar and list fields.
Does not own: provider retries, evidence grounding, localization, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

import re
from typing import Any


class SignalExtractionFieldParser:
    def required_text(self, value: dict[str, Any], key: str, limit: int) -> str:
        result = " ".join(str(value.get(key) or "").split())[:limit]
        if not result:
            raise ValueError(f"missing-{key}")
        return result

    def confidence(self, value: Any) -> str:
        normalized = str(value or "low").strip().casefold()
        if normalized in {"low", "medium", "high"}:
            return normalized
        try:
            numeric = float(normalized.replace(",", "."))
        except ValueError as exc:
            raise ValueError(f"unknown-confidence:{normalized[:40]}") from exc
        if not 0 <= numeric <= 1:
            raise ValueError(f"unknown-confidence:{normalized[:40]}")
        return "high" if numeric >= 0.8 else ("medium" if numeric >= 0.5 else "low")

    def string_list(self, value: Any, *, item_limit: int, max_items: int) -> tuple[str, ...]:
        values = [value] if isinstance(value, str) else (value if isinstance(value, (list, tuple)) else [])
        return tuple(
            normalized
            for item in values[:max_items]
            if (normalized := " ".join(str(item or "").split())[:item_limit])
        )

    def canonical(self, value: str) -> str:
        return re.sub(r"[^a-zа-я0-9]+", " ", value.casefold()).strip()


__all__ = ("SignalExtractionFieldParser",)
