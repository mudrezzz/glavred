"""Owner: infrastructure

Used by: public URL readers before decoding response bytes as text.
Does not own: HTTP transport, PDF extraction, search triage, or material persistence.
Architecture doc: docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations


class UnsupportedPublicUrlContentError(ValueError):
    pass


class PublicUrlContentPolicy:
    def ensure_readable(self, *, content_type: str, content: bytes) -> None:
        media_type = content_type.split(";", 1)[0].strip().casefold()
        if media_type and not (media_type.startswith("text/") or media_type == "application/xhtml+xml"):
            raise UnsupportedPublicUrlContentError(f"unsupported-content-type:{media_type}")
        if content.lstrip().startswith(b"%PDF-"):
            raise UnsupportedPublicUrlContentError("unsupported-content-signature:pdf")


__all__ = ("PublicUrlContentPolicy", "UnsupportedPublicUrlContentError")
