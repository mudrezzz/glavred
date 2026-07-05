"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.draft_article_memory import DossierCard, DossierCardType


class EvidenceInterpretationContextCardsComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def evidence_interpretation_cards(payload: dict[str, Any]) -> list[DossierCard]:
        cards: list[DossierCard] = []
        for item in _records(payload.get("implications"))[:8]:
            cards.append(_card(item, DossierCardType.CLAIM, "evidence-implication", "Evidence implication"))
        for item in _records(payload.get("tensions"))[:6]:
            cards.append(_card(item, DossierCardType.TENSION, "evidence-tension", "Evidence tension"))
        for item in _records(payload.get("usableExamples"))[:6]:
            cards.append(_card(item, DossierCardType.EVIDENCE, "evidence-example", "Usable source example"))
        for item in _records(payload.get("limits"))[:6]:
            cards.append(_card(item, DossierCardType.RISK, "evidence-limit", "Evidence limit"))
        for item in _records(payload.get("forbiddenOverclaims"))[:6]:
            cards.append(_card(item, DossierCardType.REJECTED_MOVE, "evidence-overclaim", "Forbidden overclaim"))
        for item in _records(payload.get("readerValueHooks"))[:6]:
            cards.append(_card(item, DossierCardType.VOICE_NOTE, "evidence-reader-value", "Reader value hook"))
        for item in _records(payload.get("rejectedEvidenceUses"))[:6]:
            cards.append(_card(item, DossierCardType.REJECTED_MOVE, "evidence-rejected-use", "Rejected evidence use"))
        for warning in _records(payload.get("warnings"))[:6]:
            warning_id = str(warning.get("id") or len(cards) + 1)
            cards.append(DossierCard(
                id=f"evidence-interpretation-warning-{warning_id}",
                type=DossierCardType.RISK,
                title="Evidence interpretation warning",
                summary=str(warning.get("message") or warning.get("detail") or warning),
                source="evidenceInterpretation",
                priority="high",
            ))
        return cards

    @staticmethod
    def _card(item: dict[str, Any], card_type: DossierCardType, prefix: str, fallback_title: str) -> DossierCard:
        item_id = str(item.get("id") or len(str(item)))
        priority = "high" if item.get("allowedUse") in {"canState", "needsQualification", "doNotState"} else "medium"
        return DossierCard(
            id=f"{prefix}-{item_id}",
            type=card_type,
            title=str(item.get("title") or fallback_title),
            summary=str(item.get("summary") or item.get("reason") or ""),
            source="evidenceInterpretation",
            related_ids=tuple(_strings(item.get("claimIds")) + _strings(item.get("publicEvidenceItemIds")) + _strings(item.get("ruleIds"))),
            priority=priority,
            metadata={
                "allowedUse": item.get("allowedUse"),
                "confidence": item.get("confidence"),
                "sourceIds": _strings(item.get("sourceIds")),
            },
        )

    @staticmethod
    def _records(value: Any) -> list[dict[str, Any]]:
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

    @staticmethod
    def _strings(value: Any) -> list[str]:
        return [str(item) for item in value if str(item).strip()] if isinstance(value, list) else []

evidence_interpretation_cards = EvidenceInterpretationContextCardsComponent.evidence_interpretation_cards
_card = EvidenceInterpretationContextCardsComponent._card
_records = EvidenceInterpretationContextCardsComponent._records
_strings = EvidenceInterpretationContextCardsComponent._strings


__all__ = (
    'evidence_interpretation_cards',
    'EvidenceInterpretationContextCardsComponent',
)
