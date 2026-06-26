from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class DossierCardType(StrEnum):
    EVIDENCE = "evidence"
    CLAIM = "claim"
    TENSION = "tension"
    ANGLE = "angle"
    DECISION = "decision"
    RISK = "risk"
    REJECTED_MOVE = "rejectedMove"
    VOICE_NOTE = "voiceNote"
    OPEN_QUESTION = "openQuestion"


@dataclass(frozen=True)
class DossierCard:
    id: str
    type: DossierCardType
    title: str
    summary: str
    source: str
    related_ids: tuple[str, ...] = ()
    priority: str = "medium"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "summary": self.summary,
            "source": self.source,
            "relatedIds": list(self.related_ids),
            "priority": self.priority,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ArticleDossier:
    cards: tuple[DossierCard, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for card in self.cards:
            counts[card.type.value] = counts.get(card.type.value, 0) + 1
        return {
            "version": "article-dossier-v1",
            "cards": [card.to_payload() for card in self.cards],
            "metadata": {"cardCount": len(self.cards), "byType": counts, **self.metadata},
        }


@dataclass(frozen=True)
class ContextPackItem:
    card_id: str
    title: str
    summary: str
    reason: str
    source: str
    priority: str = "medium"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "cardId": self.card_id,
            "title": self.title,
            "summary": self.summary,
            "reason": self.reason,
            "source": self.source,
            "priority": self.priority,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ContextPack:
    role: str
    items: tuple[ContextPackItem, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "version": "context-pack-v1",
            "role": self.role,
            "items": [item.to_payload() for item in self.items],
            "metadata": {"itemCount": len(self.items), **self.metadata},
        }
