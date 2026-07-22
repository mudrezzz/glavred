"""Owner: upstream.application

Used by: project editorial opportunity profile construction.
Does not own: workspace traversal, history selection, provider calls, or scoring.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.domain.signal_utility import ProjectEditorialSetting


class ProjectEditorialSettingProjector:
    FILTER_DIMENSIONS = {
        "author": ("authorFit", "Соответствие автору"),
        "audience": ("audienceValue", "Ценность для аудитории"),
        "positioning": ("positioningContribution", "Вклад в позиционирование"),
        "goals": ("projectGoalContribution", "Вклад в цели проекта"),
        "forbiddenTopics": ("prohibitedContent", "Запрещенный контент"),
        "topics": ("topicAffinity", "Соответствие темам"),
        "evidenceStrength": ("evidenceStrength", "Сила доказательств"),
        "factualSpecificity": ("factualSpecificity", "Фактическая конкретность"),
        "sourceCredibility": ("sourceCredibility", "Надежность источника"),
        "mechanism": ("mechanism", "Механизм"),
        "observableOutcome": ("observableOutcome", "Наблюдаемый результат"),
        "actionability": ("actionability", "Практическая применимость"),
        "novelty": ("novelty", "Новизна"),
        "productiveTension": ("productiveTension", "Продуктивное противоречие"),
        "freshness": ("freshness", "Свежесть"),
        "duplicationRisk": ("duplicationRisk", "Риск дубля"),
        "promotionalNoise": ("promotionalNoise", "Рекламность и общий AI-шум"),
    }
    PROJECT_DIMENSIONS = {
        "author": "authorFit",
        "audience": "audienceValue",
        "positioning": "positioningContribution",
        "goal": "projectGoalContribution",
        "forbidden": "prohibitedContent",
    }

    def radar_filter(self, item: dict[str, Any]) -> ProjectEditorialSetting:
        legacy_dimension = str(item.get("dimension") or "unknown")
        dimension, title = self.FILTER_DIMENSIONS.get(legacy_dimension, (legacy_dimension, "Фильтр радара"))
        return ProjectEditorialSetting(
            id=str(item.get("id") or ""),
            kind=f"radarFilter:{dimension}",
            title=title,
            statement=self._cap(str(item.get("instruction") or ""), 420),
            mode=str(item.get("mode") or "shouldMatch"),
            dimension=dimension,
            origin="radar",
        )

    def editorial_model(self, workspace: dict[str, Any]) -> list[ProjectEditorialSetting]:
        model = workspace.get("editorialModel") if isinstance(workspace.get("editorialModel"), dict) else {}
        result = [
            self._model("author", "Авторская роль", model.get("author")),
            self._model("audience", "Целевая аудитория", model.get("audience")),
            self._model("positioning", "Позиционирование", model.get("positioning")),
        ]
        result.extend(self._model(f"goal-{index + 1}", "Цель проекта", goal) for index, goal in enumerate(model.get("goals") or []))
        result.extend(
            self._model(f"forbidden-{index + 1}", "Запрещенная тема", topic, mode="mustNotMatch")
            for index, topic in enumerate(model.get("forbiddenTopics") or [])
        )
        return [item for item in result if item.statement]

    def rule(self, item: dict[str, Any]) -> ProjectEditorialSetting:
        return ProjectEditorialSetting(
            id=str(item.get("id") or ""),
            kind=f"editorialRule:{item.get('group') or 'unknown'}",
            title=self._cap(str(item.get("title") or ""), 120),
            statement=self._cap(str(item.get("statement") or ""), 360),
            dimension=None,
            origin="project",
        )

    def assertion(self, item: dict[str, Any]) -> ProjectEditorialSetting:
        return ProjectEditorialSetting(
            id=str(item.get("id") or ""),
            kind=f"authorPosition:{item.get('type') or 'unknown'}",
            title=self._cap(str(item.get("title") or ""), 120),
            statement=self._cap(str(item.get("statement") or ""), 320),
            dimension="positioningContribution",
            origin="project",
        )

    def topic(self, item: dict[str, Any]) -> ProjectEditorialSetting:
        statement = " ".join(str(item.get(key) or "") for key in ("description", "purpose", "audienceValue", "authorStance"))
        return ProjectEditorialSetting(
            id=str(item.get("id") or ""),
            kind="topic",
            title=self._cap(str(item.get("title") or ""), 120),
            statement=self._cap(statement, 420),
            dimension="topicAffinity",
            origin="project",
        )

    def _model(self, suffix: str, title: str, statement: Any, *, mode: str = "shouldMatch") -> ProjectEditorialSetting:
        return ProjectEditorialSetting(
            id=f"project-model-{suffix}",
            kind=f"projectModel:{suffix.split('-', 1)[0]}",
            title=title,
            statement=self._cap(str(statement or ""), 420),
            mode=mode,
            dimension=self.PROJECT_DIMENSIONS.get(suffix.split("-", 1)[0]),
            origin="project",
        )

    def _cap(self, value: str, limit: int) -> str:
        clean = " ".join(value.split())
        return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


__all__ = ("ProjectEditorialSettingProjector",)
