from typing import Any

from backend.app.domain.draft_article_memory import ArticleDossier, ContextPack, ContextPackItem, DossierCard, DossierCardType
from backend.app.domain.draft_model_roles import DraftModelRole

MAX_CONTEXT_PACK_ITEMS = 12

ROLE_CARD_TYPES: dict[DraftModelRole, tuple[DossierCardType, ...]] = {
    DraftModelRole.RESEARCH: (DossierCardType.EVIDENCE, DossierCardType.CLAIM, DossierCardType.OPEN_QUESTION, DossierCardType.RISK),
    DraftModelRole.STRATEGY: (DossierCardType.CLAIM, DossierCardType.TENSION, DossierCardType.DECISION, DossierCardType.RISK, DossierCardType.OPEN_QUESTION),
    DraftModelRole.WRITER: (DossierCardType.CLAIM, DossierCardType.EVIDENCE, DossierCardType.ANGLE, DossierCardType.DECISION, DossierCardType.VOICE_NOTE, DossierCardType.RISK),
    DraftModelRole.REVIEW: (DossierCardType.CLAIM, DossierCardType.EVIDENCE, DossierCardType.DECISION, DossierCardType.RISK, DossierCardType.REJECTED_MOVE),
    DraftModelRole.CRITIC: (DossierCardType.TENSION, DossierCardType.RISK, DossierCardType.REJECTED_MOVE, DossierCardType.CLAIM, DossierCardType.OPEN_QUESTION),
    DraftModelRole.FINAL_GATE: (DossierCardType.CLAIM, DossierCardType.EVIDENCE, DossierCardType.DECISION, DossierCardType.RISK, DossierCardType.REJECTED_MOVE, DossierCardType.VOICE_NOTE),
    DraftModelRole.ANOTHER_ANGLE: (DossierCardType.TENSION, DossierCardType.ANGLE, DossierCardType.REJECTED_MOVE, DossierCardType.OPEN_QUESTION, DossierCardType.DECISION),
}

ROLE_REASONS: dict[DossierCardType, str] = {
    DossierCardType.EVIDENCE: "Ground the step in accepted evidence.",
    DossierCardType.CLAIM: "Keep usable claims explicit.",
    DossierCardType.TENSION: "Preserve the editorial tension.",
    DossierCardType.ANGLE: "Reuse or challenge an existing route.",
    DossierCardType.DECISION: "Respect locked post decisions.",
    DossierCardType.RISK: "Avoid known quality or provenance risks.",
    DossierCardType.REJECTED_MOVE: "Do not repeat rejected moves.",
    DossierCardType.VOICE_NOTE: "Preserve author/editor voice notes.",
    DossierCardType.OPEN_QUESTION: "Keep unresolved research questions visible.",
}


class ContextPackBuilder:
    def build_all(self, dossier: ArticleDossier) -> dict[str, dict[str, Any]]:
        return {role.value: self.build(dossier, role).to_payload() for role in DraftModelRole}

    def build(self, dossier: ArticleDossier, role: DraftModelRole) -> ContextPack:
        wanted = ROLE_CARD_TYPES[role]
        cards = sorted(dossier.cards, key=_card_sort_key)
        items = [
            ContextPackItem(
                card_id=card.id,
                title=card.title,
                summary=card.summary[:700],
                reason=ROLE_REASONS[card.type],
                source=card.source,
                priority=card.priority,
                metadata={"type": card.type.value, "relatedIds": list(card.related_ids)},
            )
            for card in cards
            if card.type in wanted
        ][:MAX_CONTEXT_PACK_ITEMS]
        return ContextPack(role.value, tuple(items), metadata={"cardTypes": [card_type.value for card_type in wanted]})


def context_pack_for_role(payload: dict[str, Any] | None, role: DraftModelRole) -> dict[str, Any] | None:
    packs = payload.get("contextPacks") if isinstance(payload, dict) else None
    pack = packs.get(role.value) if isinstance(packs, dict) else None
    return pack if isinstance(pack, dict) else None


def _card_sort_key(card: DossierCard) -> tuple[int, str, str]:
    priority_rank = {"high": 0, "medium": 1, "low": 2}.get(card.priority, 1)
    return (priority_rank, card.type.value, card.id)
