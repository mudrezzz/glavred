from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PublicationSizeContract:
    profile_id: str
    title: str
    platform: str
    publication_kind: str
    min_chars: int
    target_chars: int
    max_chars: int
    hard_max_chars: int
    paragraph_range: dict[str, int]
    section_range: dict[str, int]
    density: str
    fabula_size_intent: str
    source: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "profileId": self.profile_id,
            "title": self.title,
            "platform": self.platform,
            "publicationKind": self.publication_kind,
            "minChars": self.min_chars,
            "targetChars": self.target_chars,
            "maxChars": self.max_chars,
            "hardMaxChars": self.hard_max_chars,
            "paragraphRange": self.paragraph_range,
            "sectionRange": self.section_range,
            "density": self.density,
            "fabulaSizeIntent": self.fabula_size_intent,
            "source": self.source,
        }
