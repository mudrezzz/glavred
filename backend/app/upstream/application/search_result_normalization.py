"""Owner: upstream.application

Used by: deterministic RadarRun search-result triage and raw-result payload construction.
Does not own: provider execution, result scoring, read allocation, persistence, or UI rendering.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from hashlib import sha256
import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from backend.app.upstream.domain.search_triage_contracts import SearchResultCandidate
from backend.app.upstream.domain.radar_language import SourceLanguageInspector


class SearchResultNormalizer:
    URL_LIMIT = 2048
    TITLE_LIMIT = 300
    SNIPPET_LIMIT = 1200
    DIAGNOSTIC_LIMIT = 320
    _TRACKING_KEYS = {"gclid", "fbclid", "ref"}
    _LATIN_MOJIBAKE = ("Ã", "Â", "Ð", "Ñ", "â€", "ï¿½")
    _CYRILLIC_MOJIBAKE = (
        "Рђ", "Р‘", "Р’", "Р“", "Р”", "Р•", "Р–", "Р—", "Р", "Р™",
        "Рљ", "Р›", "Рњ", "Рќ", "Рћ", "Рџ", "Р ", "РЎ", "Рў", "РЈ",
        "Р¤", "РҐ", "Р¦", "Р§", "РЁ", "Р©", "Р­", "Р®", "РЇ", "СЃ",
        "С‚", "СЂ", "Сѓ", "С„", "С…", "С†", "С‡", "С€", "С‰", "СЊ",
        "С‹", "СЌ", "СЋ", "СЏ", "В«", "В»", "вЂ",
    )

    def __init__(self, language_inspector: SourceLanguageInspector | None = None) -> None:
        self._languages = language_inspector or SourceLanguageInspector()

    def normalize(self, raw_result: dict[str, Any], *, query: dict[str, Any] | None = None) -> SearchResultCandidate:
        original_url = str(raw_result.get("url") or "").strip()
        raw_url = self.bounded_text(original_url, self.URL_LIMIT)
        canonical_url, invalid_reason = self.canonical_url(original_url)
        invalid_reason = str(raw_result.get("invalidReason") or invalid_reason or "") or None
        title = self.bounded_text(str(raw_result.get("title") or canonical_url or raw_url), self.TITLE_LIMIT)
        snippet = self.bounded_text(str(raw_result.get("snippet") or ""), self.SNIPPET_LIMIT)
        title, snippet, integrity_issues = self._sanitize_provider_text(title=title, snippet=snippet)
        if integrity_issues:
            invalid_reason = invalid_reason or "provider-result-text-integrity-failed"
        title = title or canonical_url or raw_url
        source_language = self._languages.inspect(title, snippet)
        query_payload = query or {}
        query_id = str(raw_result.get("queryId") or query_payload.get("id") or "")
        candidate_seed = "|".join(
            (canonical_url, title, snippet, query_id, str(raw_result.get("id") or ""))
        )
        candidate_id = f"search-candidate-{sha256(candidate_seed.encode('utf-8')).hexdigest()[:16]}"
        return SearchResultCandidate(
            id=candidate_id,
            raw_result_id=str(raw_result.get("id") or candidate_id),
            source_handle_id=str(raw_result.get("sourceHandleId") or query_payload.get("sourceHandleId") or ""),
            query_id=query_id,
            intent_id=str(raw_result.get("intentId") or query_payload.get("intentId") or ""),
            family=str(raw_result.get("family") or query_payload.get("family") or "unknown"),
            evidence_type=str(raw_result.get("evidenceType") or query_payload.get("evidenceType") or "unknown"),
            title=title,
            url=raw_url,
            canonical_url=canonical_url,
            snippet=snippet,
            domain=urlsplit(canonical_url).netloc if canonical_url else "",
            query=self.bounded_text(str(raw_result.get("query") or query_payload.get("query") or ""), 1000),
            provider=str(raw_result.get("provider") or "unknown"),
            fingerprint=self.content_fingerprint(title=title, snippet=snippet),
            valid=invalid_reason is None,
            invalid_reason=invalid_reason,
            source_language=source_language.language,
            source_language_confidence=source_language.confidence,
            source_language_mixed=source_language.mixed,
            source_language_reason_codes=source_language.reason_codes,
            requirement_ids=tuple(
                str(item) for item in (raw_result.get("requirementIds") or query_payload.get("requirementIds") or []) if item
            ),
            text_integrity_issues=integrity_issues,
        )

    def canonical_url(self, value: str) -> tuple[str, str | None]:
        raw = value.strip()
        if not raw:
            return "", "missing-url"
        if len(raw) > self.URL_LIMIT:
            return raw[: self.URL_LIMIT], "url-too-long"
        try:
            parsed = urlsplit(raw if "://" in raw else f"https://{raw}")
        except ValueError:
            return raw, "invalid-url"
        scheme = parsed.scheme.lower()
        hostname = (parsed.hostname or "").lower().removeprefix("www.")
        if scheme not in {"http", "https"} or not hostname:
            return raw, "invalid-url"
        try:
            port = f":{parsed.port}" if parsed.port else ""
        except ValueError:
            return raw[: self.URL_LIMIT], "invalid-url"
        path = parsed.path or "/"
        if path != "/":
            path = path.rstrip("/")
        query = urlencode(
            sorted(
                (key, item)
                for key, item in parse_qsl(parsed.query, keep_blank_values=True)
                if not self._is_tracking_key(key)
            ),
            doseq=True,
        )
        return urlunsplit((scheme, f"{hostname}{port}", path, query, "")), None

    def content_fingerprint(self, *, title: str, snippet: str) -> str:
        title_key = self._fingerprint_text(title)
        snippet_key = self._fingerprint_text(snippet)[:360]
        seed = f"{title_key}|{snippet_key}"
        return sha256(seed.encode("utf-8")).hexdigest()[:20] if seed.strip("|") else ""

    def bounded_text(self, value: str, limit: int) -> str:
        return " ".join(value.split())[:limit].rstrip()

    def _is_tracking_key(self, key: str) -> bool:
        lowered = key.lower()
        return lowered.startswith("utm_") or lowered in self._TRACKING_KEYS

    def _fingerprint_text(self, value: str) -> str:
        lowered = value.casefold()
        return " ".join(re.findall(r"[\w]+", lowered, flags=re.UNICODE))

    def _sanitize_provider_text(
        self, *, title: str, snippet: str,
    ) -> tuple[str, str, tuple[dict[str, Any], ...]]:
        issues: list[dict[str, Any]] = []
        safe_values: dict[str, str] = {"title": title, "snippet": snippet}
        for field, value in tuple(safe_values.items()):
            reason = self._text_integrity_reason(value)
            if reason is None:
                continue
            issues.append(
                {
                    "field": field,
                    "reasonCode": reason,
                    "charCount": len(value),
                    "valueHash": sha256(value.encode("utf-8")).hexdigest()[:20],
                }
            )
            safe_values[field] = ""
        return safe_values["title"], safe_values["snippet"], tuple(issues)

    def _text_integrity_reason(self, value: str) -> str | None:
        if "\ufffd" in value:
            return "unicode-replacement-character"
        if re.search(r"\?{4,}", value):
            return "question-mark-replacement-text"
        if any(marker in value for marker in self._LATIN_MOJIBAKE):
            return "probable-mojibake"
        marker_count = sum(value.count(marker) for marker in self._CYRILLIC_MOJIBAKE)
        return "probable-mojibake" if marker_count >= 3 else None


__all__ = ("SearchResultNormalizer",)
