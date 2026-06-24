from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DraftCandidateDirection:
    id: str
    title: str
    angle: str
    instruction: str
    rhetorical_plan_id: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "angle": self.angle,
            "instruction": self.instruction,
            "rhetoricalPlanId": self.rhetorical_plan_id,
        }


@dataclass(frozen=True)
class DraftCandidate:
    id: str
    direction: DraftCandidateDirection
    title: str
    body: str
    rationale: str
    used_evidence: list[str] = field(default_factory=list)
    rule_coverage: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)

    def to_payload(self, *, source: str, ai_run_id: str | None, fallback_used: bool) -> dict[str, Any]:
        return {
            "id": self.id,
            "direction": self.direction.to_payload(),
            "rhetoricalPlanId": self.direction.rhetorical_plan_id or self.direction.id,
            "title": self.title,
            "body": self.body,
            "rationale": self.rationale,
            "usedEvidence": self.used_evidence,
            "ruleCoverage": self.rule_coverage,
            "risks": self.risks,
            "weaknesses": self.weaknesses,
            "source": source,
            "aiRunId": ai_run_id,
            "fallbackUsed": fallback_used,
        }


@dataclass(frozen=True)
class DraftCandidateScore:
    candidate_id: str
    hard_constraint_fit: int
    evidence_grounding: int
    topic_fit: int
    fabula_fit: int
    audience_value: int
    risk_penalty: int
    publishable: bool = True
    selection_status: str = "eligible"
    selection_penalty: int = 0
    selection_reasons: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return (
            self.hard_constraint_fit
            + self.evidence_grounding
            + self.topic_fit
            + self.fabula_fit
            + self.audience_value
            - self.risk_penalty
            - self.selection_penalty
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "hardConstraintFit": self.hard_constraint_fit,
            "evidenceGrounding": self.evidence_grounding,
            "topicFit": self.topic_fit,
            "fabulaFit": self.fabula_fit,
            "audienceValue": self.audience_value,
            "riskPenalty": self.risk_penalty,
            "publishable": self.publishable,
            "selectionStatus": self.selection_status,
            "selectionPenalty": self.selection_penalty,
            "selectionReasons": self.selection_reasons,
            "total": self.total,
        }


@dataclass(frozen=True)
class DraftCandidateSelection:
    selected_candidate_id: str | None
    reason: str
    scorecard: list[DraftCandidateScore]
    unresolved_risks: list[str] = field(default_factory=list)

    def to_payload(self) -> dict[str, Any]:
        return {
            "selectedCandidateId": self.selected_candidate_id,
            "reason": self.reason,
            "scorecard": [score.to_payload() for score in self.scorecard],
            "unresolvedRisks": self.unresolved_risks,
        }


def candidate_from_payload(candidate_id: str, direction: DraftCandidateDirection, payload: dict[str, Any]) -> DraftCandidate:
    return DraftCandidate(
        id=candidate_id,
        direction=direction,
        title=str(payload.get("title") or direction.title),
        body=str(payload.get("body") or ""),
        rationale=str(payload.get("rationale") or ""),
        used_evidence=_strings(payload.get("usedEvidence")),
        rule_coverage=_strings(payload.get("ruleCoverage")),
        risks=_strings(payload.get("risks")),
        weaknesses=_strings(payload.get("weaknesses")),
    )


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
