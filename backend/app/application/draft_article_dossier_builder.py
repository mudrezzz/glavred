from typing import Any

from backend.app.application.evidence_interpretation_context_cards import evidence_interpretation_cards
from backend.app.domain.draft_article_memory import ArticleDossier, DossierCard, DossierCardType

MAX_DOSSIER_CARDS = 48


class ArticleDossierBuilder:
    def build(
        self,
        *,
        context_artifact: dict[str, Any] | None = None,
        rule_pack: dict[str, Any] | None = None,
        material_plan: dict[str, Any] | None = None,
        draft_strategy: dict[str, Any] | None = None,
        rhetorical_plans: dict[str, Any] | None = None,
        draft_artifact: dict[str, Any] | None = None,
        validation_artifact: dict[str, Any] | None = None,
    ) -> ArticleDossier:
        cards: list[DossierCard] = []
        context = context_artifact or {}
        cards.extend(_ledger_cards(_record(context.get("enrichedSourceLedger")) or _record(context.get("sourceLedger"))))
        cards.extend(_public_evidence_cards(_record(context.get("publicEvidence")) or context))
        cards.extend(_contract_cards(_record(context.get("postContract"))))
        cards.extend(_rule_cards(rule_pack or {}))
        cards.extend(evidence_interpretation_cards(_record((rule_pack or {}).get("evidenceInterpretation")) or _record(context.get("evidenceInterpretation"))))
        cards.extend(_material_cards(material_plan or {}))
        cards.extend(_strategy_cards(draft_strategy or {}))
        cards.extend(_rhetorical_cards(rhetorical_plans or {}))
        cards.extend(_draft_cards(draft_artifact or {}))
        cards.extend(_validation_cards(validation_artifact or {}))
        unique_cards = _dedupe(cards)[:MAX_DOSSIER_CARDS]
        return ArticleDossier(tuple(unique_cards), metadata={"truncated": len(cards) > len(unique_cards)})


def _ledger_cards(ledger: dict[str, Any]) -> list[DossierCard]:
    cards: list[DossierCard] = []
    for claim in _records(ledger.get("claims"))[:18]:
        claim_id = _str(claim.get("id"), "claim")
        claim_type = _str(claim.get("type"), "claim")
        title = _str(claim.get("title") or claim.get("sourceTitle") or claim_id, claim_id)
        summary = _str(claim.get("statement") or claim.get("summary") or claim.get("value"), "")
        card_type = DossierCardType.EVIDENCE if "external" in claim_type.lower() else DossierCardType.CLAIM
        cards.append(DossierCard(f"ledger-{claim_id}", card_type, title, summary, "sourceLedger", (claim_id,), _priority(claim)))
    for warning in _records(ledger.get("warnings"))[:8]:
        warning_id = _str(warning.get("id") or warning.get("code"), "warning")
        cards.append(DossierCard(f"ledger-warning-{warning_id}", DossierCardType.RISK, "Ledger warning", _str(warning.get("message") or warning, ""), "sourceLedger", priority="high"))
    return cards


def _public_evidence_cards(public_evidence: dict[str, Any]) -> list[DossierCard]:
    cards: list[DossierCard] = []
    for item in _records(public_evidence.get("items"))[:10]:
        item_id = _str(item.get("id"), "public-evidence")
        title = _str(item.get("sourceTitle") or item.get("title") or item.get("sourceUrl"), item_id)
        summary = _str(item.get("snippet") or item.get("textSummary") or item.get("summary"), "")
        cards.append(DossierCard(f"public-{item_id}", DossierCardType.EVIDENCE, title, summary, "publicEvidence", (item_id,), _priority(item)))
    synthesis = _record(public_evidence.get("evidenceSynthesis")) or _record(public_evidence.get("synthesis"))
    for claim in _records(synthesis.get("externalClaims"))[:10]:
        item_id = _str(claim.get("publicEvidenceItemId") or claim.get("id"), "external-claim")
        cards.append(DossierCard(f"synthesis-{item_id}", DossierCardType.CLAIM, "External evidence claim", _str(claim.get("statement"), ""), "evidenceSynthesis", (item_id,), _priority(claim)))
    for attempt in _records(public_evidence.get("attempts"))[:12]:
        if _str(attempt.get("status"), "") in {"failed", "notConfigured"}:
            cards.append(DossierCard(f"public-attempt-{_str(attempt.get('id'), 'attempt')}", DossierCardType.OPEN_QUESTION, "Unresolved source task", _str(attempt.get("instruction") or attempt.get("target") or attempt.get("kind"), ""), "publicEvidence", priority="medium"))
    return cards


def _contract_cards(contract: dict[str, Any]) -> list[DossierCard]:
    cards: list[DossierCard] = []
    if contract.get("thesis"):
        cards.append(DossierCard("contract-thesis", DossierCardType.DECISION, "Locked thesis", _str(contract.get("thesis"), ""), "postContract", priority="high"))
    if contract.get("cta"):
        cards.append(DossierCard("contract-cta", DossierCardType.DECISION, "CTA", _str(contract.get("cta"), ""), "postContract"))
    for index, move in enumerate(_strings(contract.get("forbiddenMoves"))[:8], start=1):
        cards.append(DossierCard(f"contract-forbidden-{index}", DossierCardType.REJECTED_MOVE, "Forbidden move", move, "postContract", priority="high"))
    for index, risk in enumerate(_strings(contract.get("riskNotes"))[:8], start=1):
        cards.append(DossierCard(f"contract-risk-{index}", DossierCardType.RISK, "Contract risk", risk, "postContract", priority="high"))
    return cards


def _rule_cards(rule_pack: dict[str, Any]) -> list[DossierCard]:
    registry = _record(rule_pack.get("ruleRegistrySnapshot"))
    cards: list[DossierCard] = []
    for rule in _records(registry.get("rules"))[:10]:
        rule_id = _str(rule.get("id"), "rule")
        severity = _str(rule.get("severity"), "")
        if severity in {"hard", "critical"}:
            cards.append(DossierCard(f"rule-{rule_id}", DossierCardType.DECISION, _str(rule.get("title"), rule_id), _str(rule.get("observableCriteria") or rule.get("repairPolicy") or ""), "ruleRegistry", (rule_id,), "high"))
    return cards


def _material_cards(material_plan: dict[str, Any]) -> list[DossierCard]:
    cards: list[DossierCard] = []
    for index, item in enumerate(_strings(material_plan.get("availableEvidence"))[:10], start=1):
        cards.append(DossierCard(f"material-evidence-{index}", DossierCardType.EVIDENCE, "Selected evidence", item, "materialPlan"))
    for index, item in enumerate(_strings(material_plan.get("riskyClaims"))[:8], start=1):
        cards.append(DossierCard(f"material-risk-{index}", DossierCardType.RISK, "Risky claim", item, "materialPlan", priority="high"))
    for index, item in enumerate(_strings(material_plan.get("openQuestions"))[:8], start=1):
        cards.append(DossierCard(f"material-question-{index}", DossierCardType.OPEN_QUESTION, "Open question", item, "materialPlan"))
    return cards


def _strategy_cards(strategy: dict[str, Any]) -> list[DossierCard]:
    cards: list[DossierCard] = []
    if strategy.get("thesisAngle"):
        cards.append(DossierCard("strategy-angle", DossierCardType.ANGLE, "Strategy angle", _str(strategy.get("thesisAngle"), ""), "draftStrategy", priority="high"))
    if strategy.get("openingMove"):
        cards.append(DossierCard("strategy-opening", DossierCardType.DECISION, "Opening move", _str(strategy.get("openingMove"), ""), "draftStrategy"))
    return cards


def _rhetorical_cards(plan_set: dict[str, Any]) -> list[DossierCard]:
    cards: list[DossierCard] = []
    for plan in _records(plan_set.get("plans"))[:6]:
        plan_id = _str(plan.get("id"), "plan")
        title = _str(plan.get("title") or plan.get("angle"), plan_id)
        cards.append(DossierCard(f"rhetorical-{plan_id}", DossierCardType.ANGLE, title, _str(plan.get("whyThisPlan") or plan.get("angle"), ""), "rhetoricalPlans", (plan_id,), _priority(plan)))
        for risk in _strings(plan.get("risks"))[:3]:
            cards.append(DossierCard(f"rhetorical-risk-{plan_id}-{len(cards)}", DossierCardType.RISK, "Plan risk", risk, "rhetoricalPlans", (plan_id,), "high"))
    return cards


def _draft_cards(draft_artifact: dict[str, Any]) -> list[DossierCard]:
    cards: list[DossierCard] = []
    selected = _record(draft_artifact.get("selection")).get("selectedCandidateId")
    for candidate in _records(draft_artifact.get("candidates"))[:6]:
        candidate_id = _str(candidate.get("id"), "candidate")
        card_type = DossierCardType.DECISION if selected == candidate_id else DossierCardType.ANGLE
        cards.append(DossierCard(f"candidate-{candidate_id}", card_type, _str(candidate.get("title"), candidate_id), _str(candidate.get("rationale") or candidate.get("body"), "")[:500], "draftCandidates", (candidate_id,), "high" if selected == candidate_id else "medium"))
        for weakness in _strings(candidate.get("weaknesses"))[:3]:
            cards.append(DossierCard(f"candidate-weakness-{candidate_id}-{len(cards)}", DossierCardType.RISK, "Candidate weakness", weakness, "draftCandidates", (candidate_id,), "high"))
    return cards


def _validation_cards(validation_artifact: dict[str, Any]) -> list[DossierCard]:
    cards: list[DossierCard] = []
    for report in _records(validation_artifact.get("candidateReports"))[:8]:
        candidate_id = _str(report.get("candidateId"), "candidate")
        for finding in _records(report.get("findings"))[:8]:
            finding_id = _str(finding.get("validatorId"), "finding")
            cards.append(DossierCard(f"validation-{candidate_id}-{finding_id}", DossierCardType.RISK, _str(finding.get("message"), finding_id), _str(finding.get("repairGuidance") or finding.get("evidenceExcerpt"), ""), "validation", (candidate_id,), _severity_priority(finding)))
    loop = _record(_record(validation_artifact.get("rankingRevision")).get("revisionLoop"))
    for cycle in _records(loop.get("cycles"))[:5]:
        if cycle.get("accepted") is False:
            cycle_id = _str(cycle.get("cycleNumber"), "cycle")
            cards.append(DossierCard(f"revision-rejected-{cycle_id}", DossierCardType.REJECTED_MOVE, "Rejected revision move", _str(cycle.get("rejectionReasons"), ""), "revisionLoop", priority="high"))
    return cards


def _dedupe(cards: list[DossierCard]) -> list[DossierCard]:
    seen: set[str] = set()
    result: list[DossierCard] = []
    for card in cards:
        if card.id not in seen and card.summary.strip():
            result.append(card)
            seen.add(card.id)
    return result


def _records(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in value if str(item).strip()] if isinstance(value, list) else []


def _str(value: Any, fallback: str = "") -> str:
    if isinstance(value, list):
        return "; ".join(str(item).strip() for item in value if str(item).strip())
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _priority(payload: dict[str, Any]) -> str:
    allowed = _str(payload.get("allowedUse"), "")
    confidence = _str(payload.get("confidence"), "")
    if allowed in {"canState", "needsQualification"} or confidence == "high":
        return "high"
    if allowed == "doNotState" or confidence == "low":
        return "low"
    return "medium"


def _severity_priority(payload: dict[str, Any]) -> str:
    return "high" if _str(payload.get("severity"), "") in {"critical", "hard"} else "medium"
