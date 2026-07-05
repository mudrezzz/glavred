from html.parser import HTMLParser

import httpx

from backend.app.drafting.application.evidence.public_evidence_ports import PublicUrlReadResult


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


class HttpxPublicUrlReader:
    def __init__(self, *, timeout_seconds: float = 12.0, max_bytes: int = 600_000, max_text_chars: int = 12_000) -> None:
        self._timeout_seconds = timeout_seconds
        self._max_bytes = max_bytes
        self._max_text_chars = max_text_chars

    def read(self, url: str) -> PublicUrlReadResult:
        response = httpx.get(
            url,
            timeout=self._timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "GlavredPublicEvidenceBot/0.1"},
        )
        response.raise_for_status()
        content = response.content[: self._max_bytes]
        text = content.decode(response.encoding or "utf-8", errors="replace")
        extractor = HtmlTextExtractor(max_chars=self._max_text_chars)
        extractor.feed(text)
        title = " ".join(extractor.title_parts).strip()
        body = " ".join(extractor.text_parts).strip()
        return PublicUrlReadResult(
            url=url,
            final_url=str(response.url),
            title=title or str(response.url),
            text=body or text[: self._max_text_chars],
        )
