from __future__ import annotations

import httpx
import pytest

from backend.app.infrastructure.public_url_content_policy import UnsupportedPublicUrlContentError
from backend.app.infrastructure.public_url_reader import HttpxPublicUrlReader


def test_public_url_reader_rejects_pdf_content_type(monkeypatch: pytest.MonkeyPatch) -> None:
    response = httpx.Response(
        200,
        headers={"content-type": "application/pdf"},
        content=b"%PDF-1.4 binary",
        request=httpx.Request("GET", "https://example.com/report.pdf"),
    )
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: response)

    with pytest.raises(UnsupportedPublicUrlContentError, match="unsupported-content-type:application/pdf"):
        HttpxPublicUrlReader().read("https://example.com/report.pdf")


def test_public_url_reader_rejects_pdf_signature_without_content_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = httpx.Response(
        200,
        content=b"  %PDF-1.7 binary",
        request=httpx.Request("GET", "https://example.com/download"),
    )
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: response)

    with pytest.raises(UnsupportedPublicUrlContentError, match="unsupported-content-signature:pdf"):
        HttpxPublicUrlReader().read("https://example.com/download")
