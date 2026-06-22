from typing import Any

from backend.app.domain.draft_generation import DraftGenerationRequest
from backend.app.domain.draft_source_ledger import (
    ForbiddenInference,
    SourceLedgerAllowedUse,
    SourceLedgerClaim,
    SourceLedgerClaimType,
    SourceLedgerConfidence,
    SourceLedgerRisk,
    SourceLedgerWarning,
)


def brief_claims(brief: dict[str, Any], request: DraftGenerationRequest | None) -> list[SourceLedgerClaim]:
    fields = [
        ("brief-title", "title"),
        ("brief-thesis", "thesis"),
        ("brief-conflict", "conflict"),
        ("brief-author-position", "authorPosition"),
        ("brief-cta", "cta"),
    ]
    claims = [
        claim(item_id, SourceLedgerClaimType.BRIEF_INTENT, brief.get(field), "brief", SourceLedgerAllowedUse.CAN_USE_AS_FRAMING)
        for item_id, field in fields
    ]
    if request is not None:
        claims.extend(
            claim(
                f"brief-evidence-{index + 1}",
                SourceLedgerClaimType.BRIEF_INTENT,
                item,
                "brief.evidence",
                SourceLedgerAllowedUse.NEEDS_QUALIFICATION,
                SourceLedgerConfidence.MEDIUM,
            )
            for index, item in enumerate(request.brief.evidence)
        )
        claims.extend(
            claim(
                f"brief-source-{index + 1}",
                SourceLedgerClaimType.BRIEF_INTENT,
                item,
                "brief.sources",
                SourceLedgerAllowedUse.CAN_USE_AS_FRAMING,
                SourceLedgerConfidence.UNKNOWN,
            )
            for index, item in enumerate(request.brief.sources)
        )
    return [item for item in claims if item.statement]


def candidate_claims(candidate: dict[str, Any]) -> list[SourceLedgerClaim]:
    confidence = confidence_from_candidate(candidate.get("confidence"))
    fields = [
        ("candidate-thesis", "thesis", SourceLedgerAllowedUse.CAN_USE_AS_FRAMING),
        ("candidate-value", "value", SourceLedgerAllowedUse.CAN_USE_AS_FRAMING),
        ("candidate-goal", "goal", SourceLedgerAllowedUse.CAN_USE_AS_FRAMING),
        ("candidate-evidence-summary", "evidenceSummary", SourceLedgerAllowedUse.NEEDS_QUALIFICATION),
    ]
    return [
        claim(item_id, SourceLedgerClaimType.CANDIDATE_CLAIM, candidate.get(field), "candidate", allowed, confidence)
        for item_id, field, allowed in fields
        if candidate.get(field)
    ]


def signal_claims(signal: dict[str, Any]) -> list[SourceLedgerClaim]:
    claims = [
        claim("signal-summary", SourceLedgerClaimType.SOURCE_CLAIM, signal.get("summary"), "sourceSignal", SourceLedgerAllowedUse.CAN_STATE),
        claim("signal-raw-note", SourceLedgerClaimType.SOURCE_CLAIM, signal.get("rawNote"), "sourceSignal.rawNote", SourceLedgerAllowedUse.NEEDS_QUALIFICATION),
        claim(
            "signal-author-correction",
            SourceLedgerClaimType.SOURCE_CLAIM,
            signal.get("authorCorrection"),
            "sourceSignal.authorCorrection",
            SourceLedgerAllowedUse.CAN_USE_AS_FRAMING,
            SourceLedgerConfidence.MEDIUM,
            ["author-correction-not-external-proof"],
        ),
    ]
    claims.extend(
        claim(
            f"signal-evidence-{index + 1}",
            SourceLedgerClaimType.SOURCE_CLAIM,
            item.get("summary") if isinstance(item, dict) else item,
            "sourceSignal.evidence",
            SourceLedgerAllowedUse.CAN_STATE,
            SourceLedgerConfidence.MEDIUM,
        )
        for index, item in enumerate(as_list(signal.get("evidence")))
    )
    return [item for item in claims if item.statement]


def topic_fabula_claims(topic: dict[str, Any], fabula: dict[str, Any]) -> list[SourceLedgerClaim]:
    claims: list[SourceLedgerClaim] = []
    claims.extend(constraint_claim(f"topic-rule-{index + 1}", item, "topic.rules") for index, item in enumerate(as_list(topic.get("rules"))))
    claims.extend(
        constraint_claim(f"fabula-proof-{index + 1}", item, "fabula.proofRequirements")
        for index, item in enumerate(as_list(fabula.get("proofRequirements")))
    )
    claims.extend(constraint_claim(f"fabula-rule-{index + 1}", item, "fabula.rules") for index, item in enumerate(as_list(fabula.get("rules"))))
    return [item for item in claims if item.statement]


def author_position_claims(author_evidence: dict[str, Any]) -> list[SourceLedgerClaim]:
    claims: list[SourceLedgerClaim] = []
    for index, item in enumerate(as_list(author_evidence.get("items"))):
        if isinstance(item, dict):
            claims.append(
                claim(
                    str(item.get("id") or f"author-position-{index + 1}"),
                    SourceLedgerClaimType.AUTHOR_POSITION_EVIDENCE,
                    item.get("statement") or item.get("title"),
                    "authorPositionEvidence",
                    SourceLedgerAllowedUse.CAN_USE_AS_FRAMING,
                    confidence_from_author_evidence(item.get("confidence")),
                    ["author-position-not-source-fact"],
                )
            )
    return [item for item in claims if item.statement]


def risks(candidate: dict[str, Any], request: DraftGenerationRequest | None) -> list[SourceLedgerRisk]:
    result = [
        SourceLedgerRisk(f"candidate-risk-{index + 1}", "Candidate risk", str(item), "candidate.risks")
        for index, item in enumerate(as_list(candidate.get("risks")))
    ]
    if request is not None:
        result.extend(
            SourceLedgerRisk(f"brief-risk-{index + 1}", "Brief risk", str(item), "brief.risks")
            for index, item in enumerate(request.brief.risks)
        )
    return [item for item in result if item.detail]


def warnings(
    context_summary: dict[str, Any],
    candidate: dict[str, Any],
    signal: dict[str, Any],
    author_evidence: dict[str, Any],
    request: DraftGenerationRequest | None,
) -> list[SourceLedgerWarning]:
    result: list[SourceLedgerWarning] = []
    if not signal:
        result.append(warning("missing-source-signal", "Missing source signal", "Draft run has no linked source signal.", "sourceSignal"))
    if not candidate:
        result.append(warning("missing-candidate", "Missing candidate", "Draft run has no linked post candidate.", "candidate"))
    elif not candidate.get("evidenceSummary"):
        result.append(warning("missing-candidate-evidence", "Missing candidate evidence", "Candidate has no evidence summary.", "candidate"))
    if request is not None and request.brief.thesis and not request.brief.evidence:
        result.append(warning("brief-thesis-no-evidence", "Brief thesis has no evidence", "Approved brief has a thesis but no evidence items.", "brief"))
    if signal.get("rawNote") and not as_list(signal.get("evidence")):
        result.append(warning("signal-raw-note-no-evidence", "Signal raw note has no structured evidence", "Use raw note carefully.", "sourceSignal"))
    if not as_list(author_evidence.get("items")):
        result.append(warning("missing-author-position-evidence", "Missing author-position evidence", "No author-position assertions were attached.", "authorPositionEvidence"))
    for index, item in enumerate(as_list(context_summary.get("missingContext"))):
        if isinstance(item, dict):
            result.append(
                warning(
                    f"missing-context-{index + 1}",
                    f"Missing {item.get('entity') or 'context'}",
                    str(item.get("reason") or item.get("id") or "Linked entity is missing."),
                    "missingContext",
                )
            )
    return result


def base_forbidden_inferences() -> list[ForbiddenInference]:
    return [
        ForbiddenInference("no-invented-facts", "Do not invent facts beyond source signal or candidate evidence.", "Keep draft grounded.", "sourceLedger"),
        ForbiddenInference("risks-are-not-facts", "Do not turn candidate risks into factual claims.", "Risks describe editorial caution.", "candidate.risks"),
        ForbiddenInference("correction-is-not-proof", "Do not strengthen author correction into external evidence.", "Author correction is framing, not source proof.", "sourceSignal.authorCorrection"),
        ForbiddenInference("position-is-not-market-fact", "Do not present author-position assertions as source-backed market facts.", "Author position is internal evidence.", "authorPositionEvidence"),
    ]


def topic_forbidden_inferences(topic: dict[str, Any]) -> list[ForbiddenInference]:
    return [
        ForbiddenInference(f"topic-forbidden-{index + 1}", f"Do not use forbidden angle: {item}", "Topic marks this angle as forbidden.", "topic.forbiddenAngles")
        for index, item in enumerate(as_list(topic.get("forbiddenAngles")))
        if item
    ]


def constraint_claim(item_id: str, statement: Any, source: str) -> SourceLedgerClaim:
    return claim(
        item_id,
        SourceLedgerClaimType.TOPIC_FABULA_CONSTRAINT,
        statement,
        source,
        SourceLedgerAllowedUse.DO_NOT_STATE,
        SourceLedgerConfidence.MEDIUM,
        ["constraint-not-draft-claim"],
    )


def claim(
    item_id: str,
    claim_type: SourceLedgerClaimType,
    statement: Any,
    source: str,
    allowed_use: SourceLedgerAllowedUse,
    confidence: SourceLedgerConfidence = SourceLedgerConfidence.UNKNOWN,
    risk_flags: list[str] | None = None,
) -> SourceLedgerClaim:
    return SourceLedgerClaim(
        id=item_id,
        claim_type=claim_type,
        statement=str(statement or ""),
        source=source,
        provenance={"source": source, "path": item_id},
        confidence=confidence,
        allowed_use=allowed_use,
        risk_flags=risk_flags or [],
    )


def warning(item_id: str, title: str, detail: str, source: str) -> SourceLedgerWarning:
    return SourceLedgerWarning(id=item_id, title=title, detail=detail, source=source)


def confidence_from_candidate(value: Any) -> SourceLedgerConfidence:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return SourceLedgerConfidence.UNKNOWN
    if score >= 80:
        return SourceLedgerConfidence.HIGH
    if score >= 50:
        return SourceLedgerConfidence.MEDIUM
    return SourceLedgerConfidence.LOW


def confidence_from_author_evidence(value: Any) -> SourceLedgerConfidence:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return SourceLedgerConfidence.UNKNOWN
    if score >= 0.8:
        return SourceLedgerConfidence.HIGH
    if score >= 0.5:
        return SourceLedgerConfidence.MEDIUM
    return SourceLedgerConfidence.LOW


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
