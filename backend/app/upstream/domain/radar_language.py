"""Owner: upstream.domain

Used by: RadarRun planning, triage, material creation, and signal localization.
Does not own: portfolio lookup, provider calls, API routing, persistence, or UI rendering.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


SOURCE_LANGUAGE_POLICIES = ("editorialOnly", "editorialAndEnglish", "any")


@dataclass(frozen=True)
class SourceLanguageAssessment:
    language: str
    confidence: str
    mixed: bool
    reason_codes: tuple[str, ...]
    cyrillic_share: float = 0.0
    latin_share: float = 0.0

    def to_payload(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "confidence": self.confidence,
            "mixed": self.mixed,
            "reasonCodes": list(self.reason_codes),
        }


@dataclass(frozen=True)
class RadarLanguageContext:
    project_id: str
    editorial_language: str
    source_language_policy: str
    query_languages: tuple[str, ...]
    allowed_source_languages: tuple[str, ...]
    allow_unknown_source_language: bool
    fallback_reason: str | None = None

    def query_language_for(self, family: str) -> str:
        if self.editorial_language == "en" or self.source_language_policy == "editorialOnly":
            return self.editorial_language
        if family in {"caseExample", "benchmarkPaper", "ossTooling"}:
            return "en"
        return self.editorial_language

    def allows(self, assessment: SourceLanguageAssessment) -> tuple[bool, str | None]:
        if self.source_language_policy == "any":
            return True, None
        if assessment.language in {"unknown", "mixed"} or assessment.mixed or assessment.confidence != "high":
            return True, "source-language-unverified"
        if assessment.language in self.allowed_source_languages:
            return True, None
        return False, "source-language-not-allowed"

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "projectId": self.project_id,
            "editorialLanguage": self.editorial_language,
            "sourceLanguagePolicy": self.source_language_policy,
            "queryLanguages": list(self.query_languages),
            "allowedSourceLanguages": list(self.allowed_source_languages),
            "allowUnknownSourceLanguage": self.allow_unknown_source_language,
        }
        if self.fallback_reason:
            payload["fallbackReason"] = self.fallback_reason
        return payload


class SourceLanguageInspector:
    _URL_OR_IDENTIFIER = re.compile(
        r"https?://\S+|\b[\w.-]+@[\w.-]+\b|\b[a-z]+(?:[-_/][a-z0-9]+){1,}\b",
        flags=re.IGNORECASE,
    )

    def inspect(self, *values: str) -> SourceLanguageAssessment:
        text = self._URL_OR_IDENTIFIER.sub(" ", " ".join(str(value or "") for value in values))
        letters = [char for char in text if char.isalpha()]
        if len(letters) < 12:
            return SourceLanguageAssessment("unknown", "low", False, ("too-little-language-text",))
        cyrillic = sum(self._is_cyrillic(char) for char in letters)
        latin = sum(self._is_latin(char) for char in letters)
        other = max(0, len(letters) - cyrillic - latin)
        cyrillic_share = cyrillic / len(letters)
        latin_share = latin / len(letters)
        other_share = other / len(letters)
        mixed = sum(share >= 0.2 for share in (cyrillic_share, latin_share, other_share)) > 1
        ranked = sorted(((cyrillic_share, "ru"), (latin_share, "en"), (other_share, "other")), reverse=True)
        top_share, language = ranked[0]
        if mixed:
            return SourceLanguageAssessment(
                "mixed",
                "medium",
                True,
                ("multiple-writing-systems",),
                cyrillic_share,
                latin_share,
            )
        confidence = "high" if top_share >= 0.8 else ("medium" if top_share >= 0.6 else "low")
        if confidence == "low":
            language = "unknown"
        return SourceLanguageAssessment(
            language,
            confidence,
            False,
            (f"dominant-language-{language}",),
            cyrillic_share,
            latin_share,
        )

    def supports_editorial_language(self, text: str, editorial_language: str) -> bool:
        cleaned = self._URL_OR_IDENTIFIER.sub(" ", str(text or ""))
        letters = [char for char in cleaned if char.isalpha()]
        if len(letters) < 12:
            return True
        expected = (
            sum(self._is_cyrillic(char) for char in letters)
            if editorial_language == "ru"
            else sum(self._is_latin(char) for char in letters)
        )
        return expected >= 3 and expected / len(letters) >= 0.3

    def _is_cyrillic(self, char: str) -> bool:
        return "\u0400" <= char <= "\u052f"

    def _is_latin(self, char: str) -> bool:
        lowered = char.casefold()
        return "a" <= lowered <= "z"


__all__ = (
    "RadarLanguageContext",
    "SOURCE_LANGUAGE_POLICIES",
    "SourceLanguageAssessment",
    "SourceLanguageInspector",
)
