"""Owner: upstream.application

Used by: external RadarRun service before planning, triage, reading, and extraction.
Does not own: portfolio persistence, language detection, provider prompts, or UI settings.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.domain.radar_language import (
    RadarLanguageContext,
    SOURCE_LANGUAGE_POLICIES,
)


class RadarLanguageContextFactory:
    DEFAULT_POLICY = "editorialAndEnglish"

    def build(
        self,
        *,
        project_context: dict[str, Any] | None,
        workspace: dict[str, Any],
        radar: dict[str, Any],
    ) -> RadarLanguageContext:
        bounded = project_context if isinstance(project_context, dict) else {}
        profile = workspace.get("projectProfile") if isinstance(workspace.get("projectProfile"), dict) else {}
        supplied_language = bounded.get("editorialLanguage")
        fallback_reason: str | None = None
        if supplied_language:
            editorial_language = self._language(supplied_language)
        else:
            editorial_language = self._language(profile.get("language") or workspace.get("language") or "ru")
            fallback_reason = "legacy-project-language-fallback"
        configured_policy = str(radar.get("sourceLanguagePolicy") or "")
        if configured_policy in SOURCE_LANGUAGE_POLICIES:
            source_policy = configured_policy
        else:
            source_policy = self.DEFAULT_POLICY
            fallback_reason = fallback_reason or "legacy-source-language-policy-fallback"
        query_languages = (editorial_language,)
        if source_policy in {"editorialAndEnglish", "any"} and editorial_language != "en":
            query_languages = (editorial_language, "en")
        if source_policy == "any":
            allowed_source_languages: tuple[str, ...] = ()
        elif source_policy == "editorialOnly":
            allowed_source_languages = (editorial_language,)
        else:
            allowed_source_languages = tuple(dict.fromkeys((editorial_language, "en")))
        return RadarLanguageContext(
            project_id=str(bounded.get("projectId") or workspace.get("projectId") or workspace.get("id") or ""),
            editorial_language=editorial_language,
            source_language_policy=source_policy,
            query_languages=query_languages,
            allowed_source_languages=allowed_source_languages,
            allow_unknown_source_language=True,
            fallback_reason=fallback_reason,
        )

    def _language(self, value: Any) -> str:
        normalized = str(value or "ru").strip().lower().replace("_", "-").split("-", 1)[0]
        return normalized if len(normalized) == 2 and normalized.isalpha() else "ru"


__all__ = ("RadarLanguageContextFactory",)
