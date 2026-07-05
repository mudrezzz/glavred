"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from dataclasses import dataclass
from typing import Any

from backend.app.domain.draft_feasibility import FeasibilityFinding, FeasibilityStatus


@dataclass(frozen=True)
class FeasibilityDecision:
    status: FeasibilityStatus
    summary: str
    blocked: bool
    extra_findings: list[FeasibilityFinding]


class FeasibilityPolicy:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def decide_feasibility(
        context_artifact: dict[str, Any],
        brief: dict[str, Any],
        claims: list[dict[str, Any]],
        warnings: list[dict[str, Any]],
        risks: list[dict[str, Any]],
        allowed_ids: list[str],
        qualified_ids: list[str],
    ) -> FeasibilityDecision:
        warning_ids = {str(item.get("id")) for item in warnings}
        if not brief.get("title") or not brief.get("thesis"):
            return decision(FeasibilityStatus.INFEASIBLE, "Approved fabula has no stable title or thesis.", True)
        if not allowed_ids and not qualified_ids:
            return decision(FeasibilityStatus.INFEASIBLE, "No usable source-ledger claims are available for a safe post.", True)
        if "missing-source-signal" in warning_ids and not has_alternative_claims_without_source(context_artifact, claims):
            return decision(FeasibilityStatus.NEEDS_HUMAN_DECISION, "Source signal context is missing.", True)
        if "missing-candidate" in warning_ids and not has_safe_context_without_candidate(context_artifact, claims):
            return decision(
                FeasibilityStatus.NEEDS_HUMAN_DECISION,
                "Post candidate context is missing and source context is not strong enough to proceed.",
                True,
            )
        if "brief-thesis-no-evidence" in warning_ids or "missing-candidate-evidence" in warning_ids:
            return decision(FeasibilityStatus.NEEDS_RESEARCH, "The post thesis needs stronger evidence before prose generation.", True)
        if qualified_ids or warnings or risks:
            return decision(
                FeasibilityStatus.FEASIBLE_WITH_CONSTRAINTS,
                "Post can be written with explicit source and risk constraints.",
                False,
                _candidate_link_finding() if "missing-candidate" in warning_ids else None,
            )
        return decision(FeasibilityStatus.FEASIBLE, "Post can be written safely.", False)

    @staticmethod
    def decision(
        status: FeasibilityStatus,
        summary: str,
        blocked: bool,
        finding: FeasibilityFinding | None = None,
    ) -> FeasibilityDecision:
        return FeasibilityDecision(status, summary, blocked, [finding] if finding else [])

    @staticmethod
    def has_safe_context_without_candidate(context_artifact: dict[str, Any], claims: list[dict[str, Any]]) -> bool:
        return (
            has_source_evidence(context_artifact, claims)
            and has_brief_evidence(context_artifact, claims)
            and bool(_as_dict(context_artifact.get("topic")))
            and bool(_as_dict(context_artifact.get("fabula")))
        )

    @staticmethod
    def has_alternative_claims_without_source(context_artifact: dict[str, Any], claims: list[dict[str, Any]]) -> bool:
        return has_brief_evidence(context_artifact, claims) and len(_usable_claim_ids(claims)) >= 2

    @staticmethod
    def has_source_evidence(context_artifact: dict[str, Any], claims: list[dict[str, Any]]) -> bool:
        signal = _as_dict(context_artifact.get("sourceSignal"))
        return bool(signal.get("evidence")) or any(str(item.get("id", "")).startswith("signal-") for item in claims)

    @staticmethod
    def has_brief_evidence(context_artifact: dict[str, Any], claims: list[dict[str, Any]]) -> bool:
        brief = _as_dict(context_artifact.get("brief"))
        return int(brief.get("evidenceCount") or 0) > 0 or any(str(item.get("id", "")).startswith("brief-evidence") for item in claims)

    @staticmethod
    def _usable_claim_ids(claims: list[dict[str, Any]]) -> list[str]:
        return [
            str(item.get("id"))
            for item in claims
            if item.get("id") and item.get("allowedUse") in {"canState", "canUseAsFraming", "needsQualification"}
        ]

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _candidate_link_finding() -> FeasibilityFinding:
        return FeasibilityFinding(
            "candidate-link-recovered-from-source",
            "warning",
            "Candidate link missing",
            "Proceeding from source signal, approved brief evidence, topic and fabula.",
            "candidate",
        )

decide_feasibility = FeasibilityPolicy.decide_feasibility
decision = FeasibilityPolicy.decision
has_safe_context_without_candidate = FeasibilityPolicy.has_safe_context_without_candidate
has_alternative_claims_without_source = FeasibilityPolicy.has_alternative_claims_without_source
has_source_evidence = FeasibilityPolicy.has_source_evidence
has_brief_evidence = FeasibilityPolicy.has_brief_evidence
_usable_claim_ids = FeasibilityPolicy._usable_claim_ids
_as_dict = FeasibilityPolicy._as_dict
_candidate_link_finding = FeasibilityPolicy._candidate_link_finding


__all__ = (
    'FeasibilityDecision',
    'decide_feasibility',
    'decision',
    'has_safe_context_without_candidate',
    'has_alternative_claims_without_source',
    'has_source_evidence',
    'has_brief_evidence',
    'FeasibilityPolicy',
)
