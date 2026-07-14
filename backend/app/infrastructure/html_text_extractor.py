"""Owner: infrastructure

Used by: public URL reader to extract bounded text from HTML responses.
Does not own: HTTP transport, content-type policy, search triage, or persistence.
Architecture doc: docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from html.parser import HTMLParser


class HtmlTextExtractor(HTMLParser):
    def __init__(self, *, max_chars: int) -> None:
        super().__init__()
        self._max_chars = max_chars
        self._skip_depth = 0
        self._capture_title = False
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        if tag == "title":
            self._capture_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._capture_title = False

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if not value:
            return
        if self._capture_title:
            self.title_parts.append(value)
        if self._skip_depth == 0 and self.text_length < self._max_chars:
            self.text_parts.append(value)

    @property
    def text_length(self) -> int:
        return sum(len(part) for part in self.text_parts)


__all__ = ("HtmlTextExtractor",)
