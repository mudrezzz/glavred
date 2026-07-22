"""Owner: upstream.application
Used by: signal utility dossier construction and replay diagnostics.
Does not own: provider calls, utility decisions, workspace persistence, or candidate assembly.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.domain.signal_utility import ProjectEditorialOpportunityProfile, ProjectEditorialSetting
from backend.app.upstream.application.signal_utility_settings import ProjectEditorialSettingProjector


class ProjectEditorialOpportunityProfileFactory:
    MAX_RULES = 24
    MAX_ASSERTIONS = 16
    MAX_TOPICS = 12
    MAX_HISTORY = 20

    def __init__(self) -> None:
        self._settings = ProjectEditorialSettingProjector()

    def build(
        self,
        *,
        workspace: dict[str, Any],
        radar: dict[str, Any],
        project_context: dict[str, Any] | None,
    ) -> ProjectEditorialOpportunityProfile:
        project_id = str((project_context or {}).get("projectId") or workspace.get("projectId") or "legacy-project")
        editorial_language = str((project_context or {}).get("editorialLanguage") or "ru")
        settings: list[ProjectEditorialSetting] = []
        counts: dict[str, int] = {}
        trimmed: dict[str, int] = {}

        filters = [item for item in radar.get("filters", []) if isinstance(item, dict) and item.get("enabled")]
        settings.extend(self._settings.radar_filter(item) for item in filters)
        counts["filters"] = len(filters)

        model_settings = self._settings.editorial_model(workspace)
        settings.extend(model_settings)
        counts["projectModel"] = len(model_settings)

        rules = self._active(workspace.get("editorialRules"))
        retained_rules = rules[: self.MAX_RULES]
        settings.extend(self._settings.rule(item) for item in retained_rules)
        counts["rules"] = len(retained_rules)
        trimmed["rules"] = max(0, len(rules) - len(retained_rules))

        assertion_value = workspace.get("authorPositionAssertions")
        assertion_items = assertion_value if isinstance(assertion_value, list) else []
        assertions = [
            item
            for item in assertion_items if isinstance(item, dict)
            if item.get("status") == "confirmed" or float(item.get("confidence") or 0) >= 0.7
        ]
        retained_assertions = assertions[: self.MAX_ASSERTIONS]
        settings.extend(self._settings.assertion(item) for item in retained_assertions)
        counts["assertions"] = len(retained_assertions)
        trimmed["assertions"] = max(0, len(assertions) - len(retained_assertions))

        topics = self._active(workspace.get("topics"))
        retained_topics = topics[: self.MAX_TOPICS]
        settings.extend(self._settings.topic(item) for item in retained_topics)
        counts["topics"] = len(retained_topics)
        trimmed["topics"] = max(0, len(topics) - len(retained_topics))

        history = self._history(workspace)[: self.MAX_HISTORY]
        counts["history"] = len(history)
        unique_settings = {item.id: item for item in settings if item.id}
        return ProjectEditorialOpportunityProfile(
            project_id=project_id,
            editorial_language=editorial_language,
            project_summary=self._project_summary(workspace),
            settings=tuple(unique_settings.values()),
            history_fingerprints=tuple(history),
            retained_counts=counts,
            trimmed_counts=trimmed,
        )

    def _active(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict) and item.get("status", "active") == "active"]

    def _project_summary(self, workspace: dict[str, Any]) -> str:
        profile = workspace.get("projectProfile") if isinstance(workspace.get("projectProfile"), dict) else {}
        model = workspace.get("editorialModel") if isinstance(workspace.get("editorialModel"), dict) else {}
        return self._cap(
            " ".join(
                str(value or "")
                for value in (
                    profile.get("name"),
                    profile.get("description"),
                    model.get("author"),
                    model.get("audience"),
                    model.get("positioning"),
                )
            ),
            700,
        )

    def _history(self, workspace: dict[str, Any]) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for collection, kind in (("sourceSignals", "signal"), ("postCandidates", "candidate"), ("contentPlanItems", "plan")):
            items = workspace.get(collection)
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                result.append(
                    {
                        "id": str(item.get("id") or ""),
                        "kind": kind,
                        "fingerprint": self._cap(
                            " ".join(str(item.get(key) or "") for key in ("title", "summary", "expectedEffect")),
                            220,
                        ),
                    }
                )
        return [item for item in result if item["id"] and item["fingerprint"]]

    def _cap(self, value: str, limit: int) -> str:
        clean = " ".join(value.split())
        return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


__all__ = ("ProjectEditorialOpportunityProfileFactory",)
