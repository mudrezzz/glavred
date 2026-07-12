"""Owner: drafting.application.operations

Used by: alternative-angle route payload compaction.
Does not own: section selection, total budgets, prompt wording, or provider calls.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


class AlternativeAngleRouteProjection:
    """Projects rich route inputs into fixed-shape, per-record bounded values."""

    def candidate(self, value: Mapping[str, Any]) -> dict[str, Any]:
        windows = self.mapping(value.get("bodyWindows"))
        opening = value.get("openingMove") or next((child for _, child in sorted(windows.items()) if child), None) or value.get("bodyExcerpt")
        idea = value.get("angle") or value.get("rationale") or value.get("bodyExcerpt")
        result = {
            "id": self.text(value.get("id"), 120),
            "title": self.text(value.get("title"), 180),
            "rhetoricalPlanId": self.text(value.get("rhetoricalPlanId"), 120),
            "idea": self.text(idea, 320),
            "opening": self.text(opening, 320),
            "strengths": self.texts(value.get("strengths"), 1, 160),
            "risks": self.texts(value.get("risks"), 1, 160),
            "weaknesses": self.texts(value.get("weaknesses"), 1, 160),
            "usedEvidence": self.identifiers(value.get("usedEvidence"), 4),
            "ruleCoverage": self.identifiers(value.get("ruleCoverage"), 4),
        }
        return self.fit(result, 1_800, ("idea", "opening"))

    def critique(self, value: Mapping[str, Any]) -> dict[str, Any]:
        findings = [
            {
                "severity": self.text(item.get("severity"), 24),
                "validatorId": self.text(item.get("validatorId") or item.get("dimension"), 100),
                "message": self.text(item.get("message") or item.get("finding"), 180),
            }
            for item in self.records(value.get("findings"))[:2]
        ]
        return self.fit({
            "candidateId": self.text(value.get("candidateId"), 120),
            "status": self.text(value.get("status"), 24),
            "editorialRisk": self.text(value.get("editorialRisk"), 24),
            "weakestMove": self.text(value.get("weakestMove"), 240),
            "recommendedEditorialMove": self.text(value.get("recommendedEditorialMove"), 240),
            "findings": findings,
        }, 900, ("recommendedEditorialMove", "weakestMove"))

    def validation_issue(self, value: Mapping[str, Any]) -> dict[str, Any]:
        return self.fit({
            "candidateId": self.text(value.get("candidateId"), 120),
            "severity": self.text(value.get("severity"), 24),
            "validatorId": self.text(value.get("validatorId") or value.get("id"), 100),
            "source": self.text(value.get("source"), 40),
            "message": self.text(value.get("message"), 220),
            "repairGuidance": self.text(value.get("repairGuidance"), 180),
            "ruleIds": self.identifiers(value.get("ruleIds"), 4),
            "claimIds": self.identifiers(value.get("claimIds"), 4),
        }, 600, ("repairGuidance", "message"))

    def rejected_move(self, value: Mapping[str, Any]) -> dict[str, Any]:
        return self.fit({
            "candidateId": self.text(value.get("candidateId"), 120),
            "severity": self.text(value.get("severity"), 24),
            "validatorId": self.text(value.get("validatorId"), 100),
            "message": self.text(value.get("message"), 140),
            "repairGuidance": self.text(value.get("repairGuidance"), 120),
        }, 350, ("repairGuidance", "message"))

    def evidence(self, value: Mapping[str, Any]) -> dict[str, Any]:
        return self.fit({
            "id": self.text(value.get("id"), 120),
            "statement": self.text(value.get("statement") or value.get("summary"), 220),
            "allowedUse": self.text(value.get("allowedUse"), 40),
            "confidence": self.text(value.get("confidence"), 24),
            "sourceId": self.text(value.get("sourceId") or value.get("source"), 100),
            "claimIds": self.identifiers(value.get("claimIds"), 3),
        }, 400, ("statement",))

    def rule(self, value: Mapping[str, Any]) -> dict[str, Any]:
        return self.fit({
            "id": self.text(value.get("id"), 120),
            "severity": self.text(value.get("severity"), 24),
            "category": self.text(value.get("category"), 60),
            "statement": self.text(value.get("statement") or value.get("rule"), 140),
        }, 250, ("statement",))

    def post_contract(self, value: Any) -> dict[str, Any]:
        contract = self.mapping(value)
        return self.fit({
            "title": self.text(contract.get("title"), 180),
            "thesis": self.text(contract.get("thesis"), 500),
            "audience": self.text(contract.get("audience"), 360),
            "cta": self.text(contract.get("cta"), 300),
            "platform": self.text(contract.get("platform"), 60),
            "publicationSizeContract": self.bounded(contract.get("publicationSizeContract"), 5, 180),
            "claims": self.bounded(contract.get("claims"), 4, 220),
            "forbiddenMoves": self.bounded(contract.get("forbiddenMoves"), 5, 180),
            "evidenceObligations": self.bounded(contract.get("evidenceObligations"), 4, 200),
            "fabulaObligations": self.bounded(contract.get("fabulaObligations"), 4, 200),
            "riskNotes": self.bounded(contract.get("riskNotes"), 3, 160),
        }, 4_000, ("riskNotes", "fabulaObligations", "evidenceObligations"))

    def repair_context(self, value: Any) -> dict[str, Any]:
        context = self.mapping(value)
        previous = self.mapping(context.get("previousAttempt"))
        return self.fit({
            "previousAttempt": {
                "label": self.text(previous.get("label"), 80),
                "status": self.text(previous.get("status"), 40),
                "backup": bool(previous.get("backup")),
                "validation": self.text(previous.get("validation"), 500),
            },
            "requiredShape": self.text(context.get("requiredShape"), 300),
            "missingKeys": self.identifiers(context.get("missingKeys"), 12),
            "errorType": self.text(context.get("errorType"), 100),
        }, 1_500, ("requiredShape",))

    def fit(self, value: dict[str, Any], limit: int, shrink_order: tuple[str, ...]) -> dict[str, Any]:
        for key in shrink_order:
            while self.chars(value) > limit and value.get(key):
                current = value[key]
                if isinstance(current, str):
                    value[key] = current[: max(0, len(current) - min(80, len(current)))]
                elif isinstance(current, list):
                    value[key] = current[:-1]
                else:
                    break
        return value

    def identifiers(self, value: Any, limit: int) -> list[str]:
        result = []
        for item in self.list(value)[:limit]:
            identity = item.get("id") if isinstance(item, Mapping) else item
            if identity not in (None, ""):
                result.append(self.text(identity, 120))
        return result

    def texts(self, value: Any, limit: int, text_limit: int) -> list[str]:
        return [self.text(item, text_limit) for item in self.list(value)[:limit]]

    def bounded(self, value: Any, list_limit: int, text_limit: int) -> Any:
        if isinstance(value, str):
            return self.text(value, text_limit)
        if isinstance(value, Mapping):
            return {str(key): self.bounded(child, list_limit, text_limit) for key, child in list(value.items())[:10]}
        if isinstance(value, list):
            return [self.bounded(child, list_limit, text_limit) for child in value[:list_limit]]
        return value

    def records(self, value: Any) -> list[dict[str, Any]]:
        return [dict(item) for item in self.list(value) if isinstance(item, Mapping)]

    def mapping(self, value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    def list(self, value: Any) -> list[Any]:
        return list(value) if isinstance(value, list) else []

    def text(self, value: Any, limit: int) -> str:
        return str(value or "")[:limit]

    def chars(self, value: Any) -> int:
        return len(json.dumps(value, ensure_ascii=False, sort_keys=True))


__all__ = ("AlternativeAngleRouteProjection",)
