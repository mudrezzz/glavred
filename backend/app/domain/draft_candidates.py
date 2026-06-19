from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DraftCandidateDirection:
    id: str
    title: str
    angle: str
    instruction: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "angle": self.angle,
            "instruction": self.instruction,
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

    @property
    def total(self) -> int:
        return (
            self.hard_constraint_fit
            + self.evidence_grounding
            + self.topic_fit
            + self.fabula_fit
            + self.audience_value
            - self.risk_penalty
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
            "total": self.total,
        }


@dataclass(frozen=True)
class DraftCandidateSelection:
    selected_candidate_id: str
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
