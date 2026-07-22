"""Owner: infrastructure

Used by: DraftRun public evidence retrieval and RadarRun selective URL reading.
Does not own: PDF extraction, search-result triage, provider search, or material scoring.
Architecture doc: docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md
"""

import httpx

from backend.app.drafting.application.evidence.public_evidence_ports import PublicUrlReadResult
from backend.app.infrastructure.html_text_extractor import HtmlTextExtractor
from backend.app.infrastructure.public_url_content_policy import PublicUrlContentPolicy


class HttpxPublicUrlReader:
    def __init__(
        self,
        *,
        timeout_seconds: float = 12.0,
        max_bytes: int = 600_000,
        max_text_chars: int = 12_000,
        content_policy: PublicUrlContentPolicy | None = None,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._max_bytes = max_bytes
        self._max_text_chars = max_text_chars
        self._content_policy = content_policy or PublicUrlContentPolicy()

    def read(self, url: str) -> PublicUrlReadResult:
        response = httpx.get(
            url,
            timeout=self._timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "GlavredPublicEvidenceBot/0.1"},
        )
        response.raise_for_status()
        content = response.content[: self._max_bytes]
        self._content_policy.ensure_readable(
            content_type=response.headers.get("content-type", ""),
            content=content,
        )
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
