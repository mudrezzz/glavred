from dataclasses import dataclass, field
from typing import Any


ALLOWED_USES = {"canState", "canUseAsFraming", "needsQualification", "doNotState"}
CONFIDENCE_LEVELS = {"high", "medium", "low", "unknown"}


@dataclass(frozen=True)
class EvidenceInterpretationItem:
    id: str
    title: str
    summary: str
    source_ids: tuple[str, ...] = ()
    public_evidence_item_ids: tuple[str, ...] = ()
    claim_ids: tuple[str, ...] = ()
    rule_ids: tuple[str, ...] = ()
    contract_obligation_ids: tuple[str, ...] = ()
    confidence: str = "unknown"
    allowed_use: str = "needsQualification"
    reason: str = ""

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "sourceIds": list(self.source_ids),
            "publicEvidenceItemIds": list(self.public_evidence_item_ids),
            "claimIds": list(self.claim_ids),
            "ruleIds": list(self.rule_ids),
            "contractObligationIds": list(self.contract_obligation_ids),
            "confidence": _confidence(self.confidence),
            "allowedUse": _allowed_use(self.allowed_use),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class EvidenceInterpretation:
    implications: tuple[EvidenceInterpretationItem, ...] = ()
    tensions: tuple[EvidenceInterpretationItem, ...] = ()
    usable_examples: tuple[EvidenceInterpretationItem, ...] = ()
    limits: tuple[EvidenceInterpretationItem, ...] = ()
    forbidden_overclaims: tuple[EvidenceInterpretationItem, ...] = ()
    author_position_links: tuple[EvidenceInterpretationItem, ...] = ()
    reader_value_hooks: tuple[EvidenceInterpretationItem, ...] = ()
    recommended_use_by_plan: tuple[EvidenceInterpretationItem, ...] = ()
    rejected_evidence_uses: tuple[EvidenceInterpretationItem, ...] = ()
    warnings: tuple[dict[str, Any], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "version": "evidence-interpretation-v1",
            "implications": [item.to_payload() for item in self.implications],
            "tensions": [item.to_payload() for item in self.tensions],
            "usableExamples": [item.to_payload() for item in self.usable_examples],
            "limits": [item.to_payload() for item in self.limits],
            "forbiddenOverclaims": [item.to_payload() for item in self.forbidden_overclaims],
            "authorPositionLinks": [item.to_payload() for item in self.author_position_links],
            "readerValueHooks": [item.to_payload() for item in self.reader_value_hooks],
            "recommendedUseByPlan": [item.to_payload() for item in self.recommended_use_by_plan],
            "rejectedEvidenceUses": [item.to_payload() for item in self.rejected_evidence_uses],
            "warnings": list(self.warnings),
            "metadata": {
                "implicationCount": len(self.implications),
                "tensionCount": len(self.tensions),
                "usableExampleCount": len(self.usable_examples),
                "limitCount": len(self.limits),
                "forbiddenOverclaimCount": len(self.forbidden_overclaims),
                "warningCount": len(self.warnings),
                **self.metadata,
            },
        }


def evidence_interpretation_from_payload(payload: dict[str, Any]) -> EvidenceInterpretation:
    return EvidenceInterpretation(
        implications=_items(payload.get("implications")),
        tensions=_items(payload.get("tensions")),
        usable_examples=_items(payload.get("usableExamples")),
        limits=_items(payload.get("limits")),
        forbidden_overclaims=_items(payload.get("forbiddenOverclaims")),
        author_position_links=_items(payload.get("authorPositionLinks")),
        reader_value_hooks=_items(payload.get("readerValueHooks")),
        recommended_use_by_plan=_items(payload.get("recommendedUseByPlan")),
        rejected_evidence_uses=_items(payload.get("rejectedEvidenceUses")),
        warnings=tuple(item for item in _records(payload.get("warnings"))),
        metadata=_record(payload.get("metadata")),
    )


def _items(value: Any) -> tuple[EvidenceInterpretationItem, ...]:
    result: list[EvidenceInterpretationItem] = []
    for index, item in enumerate(_records(value), start=1):
        result.append(
            EvidenceInterpretationItem(
                id=_text(item.get("id"), f"interpretation-{index}"),
                title=_text(item.get("title"), "Evidence interpretation"),
                summary=_text(item.get("summary") or item.get("description"), ""),
                source_ids=_strings(item.get("sourceIds")),
                public_evidence_item_ids=_strings(item.get("publicEvidenceItemIds")),
                claim_ids=_strings(item.get("claimIds")),
                rule_ids=_strings(item.get("ruleIds")),
                contract_obligation_ids=_strings(item.get("contractObligationIds")),
                confidence=_confidence(_text(item.get("confidence"), "unknown")),
                allowed_use=_allowed_use(_text(item.get("allowedUse"), "needsQualification")),
                reason=_text(item.get("reason"), ""),
            )
        )
    return tuple(result)


def _records(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _strings(value: Any) -> tuple[str, ...]:
    return tuple(str(item).strip() for item in value if str(item).strip()) if isinstance(value, list) else ()


def _text(value: Any, fallback: str) -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _allowed_use(value: str) -> str:
    return value if value in ALLOWED_USES else "needsQualification"


def _confidence(value: str) -> str:
    return value if value in CONFIDENCE_LEVELS else "unknown"
