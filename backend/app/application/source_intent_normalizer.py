import re

from backend.app.domain.draft_generation import DraftGenerationRequest
from backend.app.domain.draft_source_intent import SourceIntent, SourceIntentItem, SourceIntentItemKind

URL_RE = re.compile(r"^https?://\S+$", re.IGNORECASE)
PREFIXES = {
    "url:": SourceIntentItemKind.URL,
    "источник:": SourceIntentItemKind.NAMED_SOURCE,
    "source:": SourceIntentItemKind.NAMED_SOURCE,
    "найти:": SourceIntentItemKind.RESEARCH_REQUEST,
    "search:": SourceIntentItemKind.RESEARCH_REQUEST,
    "проверить:": SourceIntentItemKind.PROOF_NEED,
    "verify:": SourceIntentItemKind.PROOF_NEED,
    "контекст:": SourceIntentItemKind.FRAMING_HINT,
    "framing:": SourceIntentItemKind.FRAMING_HINT,
    "не использовать:": SourceIntentItemKind.EXCLUSION,
    "exclude:": SourceIntentItemKind.EXCLUSION,
}
REQUEST_MARKERS = ("найти", "мнение", "лидер", "эксперт", "кто пишет", "что говорят", "обзор")
PROOF_MARKERS = ("проверить", "статист", "цифр", "данн", "исследован", "benchmark", "доказ")
EXCLUSION_MARKERS = ("не использовать", "избегать", "без vendor", "без вендор", "exclude")
FRAMING_MARKERS = ("как контекст", "для рамки", "framing", "позиция")


class SourceIntentNormalizer:
    def normalize(self, request: DraftGenerationRequest) -> SourceIntent:
        items = [
            self._item(index + 1, raw)
            for index, raw in enumerate(request.brief.sources)
            if raw.strip()
        ]
        warnings = [] if items else ["Approved brief has no source intent lines."]
        return SourceIntent(
            items=items,
            warnings=warnings,
            metadata={"version": "source-intent-v1", "sourceCount": len(items)},
        )

    def _item(self, index: int, raw: str) -> SourceIntentItem:
        cleaned = raw.strip()
        kind, instruction, notes = self._classify(cleaned)
        return SourceIntentItem(
            id=f"source-intent-{index}",
            raw=cleaned,
            kind=kind,
            instruction=instruction,
            confidence="high" if kind in {SourceIntentItemKind.URL, SourceIntentItemKind.EXCLUSION} else "medium",
            notes=notes,
        )

    def _classify(self, value: str) -> tuple[SourceIntentItemKind, str, list[str]]:
        lowered = value.lower()
        for prefix, kind in PREFIXES.items():
            if lowered.startswith(prefix):
                instruction = value[len(prefix):].strip()
                return kind, instruction or value, [f"explicit prefix {prefix}"]
        if URL_RE.match(value):
            return SourceIntentItemKind.URL, value, ["detected URL"]
        if any(marker in lowered for marker in EXCLUSION_MARKERS):
            return SourceIntentItemKind.EXCLUSION, value, ["detected exclusion"]
        if any(marker in lowered for marker in PROOF_MARKERS):
            return SourceIntentItemKind.PROOF_NEED, value, ["detected proof need"]
        if any(marker in lowered for marker in REQUEST_MARKERS):
            return SourceIntentItemKind.RESEARCH_REQUEST, value, ["detected research request"]
        if any(marker in lowered for marker in FRAMING_MARKERS):
            return SourceIntentItemKind.FRAMING_HINT, value, ["detected framing hint"]
        if len(value.split()) <= 5:
            return SourceIntentItemKind.NAMED_SOURCE, value, ["short line treated as named source"]
        return SourceIntentItemKind.RESEARCH_REQUEST, value, ["plain language research request"]
