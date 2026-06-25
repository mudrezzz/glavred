from dataclasses import dataclass
from enum import StrEnum


class DraftModelRole(StrEnum):
    RESEARCH = "research"
    STRATEGY = "strategy"
    WRITER = "writer"
    REVIEW = "review"
    CRITIC = "critic"
    ANOTHER_ANGLE = "anotherAngle"


class DraftModelSelectionSource(StrEnum):
    ROLE = "role"
    DEFAULT = "default"
    BACKUP = "backup"
    WEB_SEARCH = "webSearch"
    UNCONFIGURED = "unconfigured"


@dataclass(frozen=True)
class DraftModelSelection:
    role: DraftModelRole
    model: str | None
    source: DraftModelSelectionSource

    def to_payload(self) -> dict[str, str | None]:
        return {
            "modelRole": self.role.value,
            "selectedModel": self.model,
            "modelSelectionSource": self.source.value,
        }
