"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.draft_feasibility import FeasibilityReport
from backend.app.domain.draft_post_contract import (
    PostContract,
    PostContractClaim,
    PostContractObligation,
)
from backend.app.drafting.application.evidence.publication_size_contract_resolver import PublicationSizeContractResolver


class PostContractBuilder:
    def __init__(self, publication_size_resolver: PublicationSizeContractResolver | None = None) -> None:
        self._publication_size_resolver = publication_size_resolver or PublicationSizeContractResolver()

    def build(self, context_artifact: dict[str, Any], report: FeasibilityReport) -> PostContract:
        brief = _as_dict(context_artifact.get("brief"))
        candidate = _as_dict(context_artifact.get("candidate"))
        work_item = _as_dict(context_artifact.get("workItem"))
        slot = _as_dict(context_artifact.get("planSlot"))
        topic = _as_dict(context_artifact.get("topic"))
        fabula = _as_dict(context_artifact.get("fabula"))
        ledger = _as_dict(context_artifact.get("sourceLedger"))
        claims = _as_list_of_dicts(ledger.get("claims"))
        return PostContract(
            title=str(brief.get("title") or candidate.get("title") or work_item.get("title") or ""),
            thesis=str(brief.get("thesis") or candidate.get("thesis") or ""),
            audience=_first_text(brief.get("audience"), candidate.get("audience")),
            value=_first_text(candidate.get("value")),
            goal=_first_text(candidate.get("goal")),
            cta=_first_text(brief.get("cta")),
            platform=_first_text(slot.get("platform"), work_item.get("platform"), candidate.get("platform")),
            date=_first_text(slot.get("date"), work_item.get("date")),
            time=_first_text(slot.get("time"), work_item.get("time")),
            topic_id=_first_text(topic.get("id"), work_item.get("topicId"), slot.get("topicId")),
            topic_title=_first_text(topic.get("title")),
            fabula_id=_first_text(fabula.get("id"), work_item.get("fabulaId"), slot.get("fabulaId")),
            fabula_title=_first_text(fabula.get("title")),
            claims=_contract_claims(report, claims),
            forbidden_moves=[str(item.get("statement")) for item in _as_list_of_dicts(ledger.get("forbiddenInferences")) if item.get("statement")],
            evidence_obligations=_obligations(claims, "evidence", {"sourceSignal", "sourceSignal.evidence", "candidate", "brief.evidence"}),
            fabula_obligations=_obligations(claims, "fabula", {"fabula.proofRequirements", "fabula.rules"}),
            publication_size_contract=self._publication_size_resolver.resolve(context_artifact),
            risk_notes=[str(item.get("detail")) for item in _as_list_of_dicts(ledger.get("risks")) if item.get("detail")],
            metadata={"version": "post-contract-v1", "feasibilityStatus": report.status.value},
        )

    def not_created(self, report: FeasibilityReport) -> dict[str, Any]:
        return {
            "status": "notCreated",
            "reason": report.summary,
            "feasibilityStatus": report.status.value,
            "blockedBy": "feasibility",
        }


class PostContractBuilderComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def _contract_claims(report: FeasibilityReport, claims: list[dict[str, Any]]) -> list[PostContractClaim]:
        by_id = {str(claim.get("id")): claim for claim in claims if claim.get("id")}
        result = [
            PostContractClaim(item_id, str(by_id.get(item_id, {}).get("allowedUse") or "canUseAsFraming"))
            for item_id in report.allowed_claim_ids
        ]
        result.extend(PostContractClaim(item_id, "needsQualification", "Use with careful wording") for item_id in report.qualified_claim_ids)
        return result

    @staticmethod
    def _obligations(claims: list[dict[str, Any]], kind: str, sources: set[str]) -> list[PostContractObligation]:
        return [
            PostContractObligation(
                id=f"{kind}-{index + 1}",
                kind=kind,
                statement=str(claim.get("statement")),
                source=str(claim.get("source")),
            )
            for index, claim in enumerate(claims)
            if claim.get("statement") and claim.get("source") in sources
        ]

    @staticmethod
    def _first_text(*values: Any) -> str | None:
        for value in values:
            if value:
                return str(value)
        return None

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

_contract_claims = PostContractBuilderComponent._contract_claims
_obligations = PostContractBuilderComponent._obligations
_first_text = PostContractBuilderComponent._first_text
_as_dict = PostContractBuilderComponent._as_dict
_as_list_of_dicts = PostContractBuilderComponent._as_list_of_dicts


__all__ = (
    'PostContractBuilder',
    'PostContractBuilderComponent',
)
