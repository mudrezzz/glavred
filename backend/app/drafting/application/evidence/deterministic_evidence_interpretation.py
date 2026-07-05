"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.draft_evidence_interpretation import EvidenceInterpretation, EvidenceInterpretationItem


class DeterministicEvidenceInterpretationService:
    def interpret(
        self,
        *,
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
    ) -> EvidenceInterpretation:
        ledger = _record(context_artifact.get("sourceLedger"))
        public_evidence = _record(context_artifact.get("publicEvidence"))
        rule_ids = _rule_ids(rule_pack)
        claims = _external_claims(ledger)
        items_by_id = {
            str(item.get("id")): item
            for item in _records(public_evidence.get("items"))
            if item.get("id")
        }

        implications: list[EvidenceInterpretationItem] = []
        examples: list[EvidenceInterpretationItem] = []
        limits: list[EvidenceInterpretationItem] = []
        forbidden: list[EvidenceInterpretationItem] = []
        reader_hooks: list[EvidenceInterpretationItem] = []
        rejected: list[EvidenceInterpretationItem] = []

        for index, claim in enumerate(claims[:8], start=1):
            provenance = _record(claim.get("provenance"))
            item_id = str(provenance.get("publicEvidenceItemId") or "")
            source_title = str(provenance.get("sourceTitle") or "public source")
            claim_id = str(claim.get("id") or f"external-claim-{index}")
            statement = str(claim.get("statement") or "").strip()
            allowed_use = _allowed_use(str(claim.get("allowedUse") or "needsQualification"))
            confidence = str(claim.get("confidence") or "unknown")
            source_ids = _source_ids(provenance)
            related_item_ids = (item_id,) if item_id else ()

            if allowed_use in {"canState", "needsQualification", "canUseAsFraming"} and statement:
                implications.append(EvidenceInterpretationItem(
                    id=f"implication-{claim_id}",
                    title=f"What {source_title} changes",
                    summary=f"This source can shape the argument as: {statement}",
                    source_ids=source_ids,
                    public_evidence_item_ids=related_item_ids,
                    claim_ids=(claim_id,),
                    rule_ids=rule_ids,
                    confidence=confidence,
                    allowed_use=allowed_use,
                    reason="Derived from an accepted external ledger claim.",
                ))
                reader_hooks.append(EvidenceInterpretationItem(
                    id=f"reader-value-{claim_id}",
                    title=f"Reader value from {source_title}",
                    summary=f"Use this evidence to make the post more concrete for the reader: {statement}",
                    source_ids=source_ids,
                    public_evidence_item_ids=related_item_ids,
                    claim_ids=(claim_id,),
                    rule_ids=rule_ids,
                    confidence=confidence,
                    allowed_use="canUseAsFraming" if allowed_use == "needsQualification" else allowed_use,
                    reason="Keeps public evidence tied to audience value instead of citation decoration.",
                ))

            public_item = items_by_id.get(item_id)
            snippet = str((public_item or {}).get("snippet") or provenance.get("snippet") or "").strip()
            if snippet:
                examples.append(EvidenceInterpretationItem(
                    id=f"example-{claim_id}",
                    title=f"Usable example from {source_title}",
                    summary=snippet,
                    source_ids=source_ids,
                    public_evidence_item_ids=related_item_ids,
                    claim_ids=(claim_id,),
                    rule_ids=rule_ids,
                    confidence=confidence,
                    allowed_use="canUseAsFraming" if allowed_use == "needsQualification" else allowed_use,
                    reason="Example is source-backed and must keep attribution when used.",
                ))

            if allowed_use == "needsQualification":
                limits.append(_limit_item(claim_id, source_title, statement, source_ids, related_item_ids, rule_ids))
                forbidden.append(_overclaim_item(claim_id, source_title, statement, source_ids, related_item_ids, rule_ids))
            if allowed_use == "doNotState":
                rejected.append(EvidenceInterpretationItem(
                    id=f"rejected-{claim_id}",
                    title=f"Rejected use of {source_title}",
                    summary=statement,
                    source_ids=source_ids,
                    public_evidence_item_ids=related_item_ids,
                    claim_ids=(claim_id,),
                    rule_ids=rule_ids,
                    confidence=confidence,
                    allowed_use="doNotState",
                    reason="Ledger marks this claim as unsafe to state.",
                ))

        warnings = _warnings(context_artifact, public_evidence, claims)
        return EvidenceInterpretation(
            implications=tuple(implications),
            usable_examples=tuple(examples),
            limits=tuple(limits),
            forbidden_overclaims=tuple(forbidden),
            reader_value_hooks=tuple(reader_hooks),
            rejected_evidence_uses=tuple(rejected),
            warnings=tuple(warnings),
            metadata={"source": "deterministic", "ruleIdsUsed": list(rule_ids)},
        )


class DeterministicEvidenceInterpretationPolicy:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def _limit_item(
        claim_id: str,
        source_title: str,
        statement: str,
        source_ids: tuple[str, ...],
        item_ids: tuple[str, ...],
        rule_ids: tuple[str, ...],
    ) -> EvidenceInterpretationItem:
        return EvidenceInterpretationItem(
            id=f"limit-{claim_id}",
            title=f"Qualification required for {source_title}",
            summary=f"This evidence qualifies the idea but does not prove the strongest version: {statement}",
            source_ids=source_ids,
            public_evidence_item_ids=item_ids,
            claim_ids=(claim_id,),
            rule_ids=rule_ids,
            confidence="medium",
            allowed_use="needsQualification",
            reason="Allowed use requires careful wording.",
        )

    @staticmethod
    def _overclaim_item(
        claim_id: str,
        source_title: str,
        statement: str,
        source_ids: tuple[str, ...],
        item_ids: tuple[str, ...],
        rule_ids: tuple[str, ...],
    ) -> EvidenceInterpretationItem:
        return EvidenceInterpretationItem(
            id=f"overclaim-{claim_id}",
            title=f"Forbidden overclaim from {source_title}",
            summary=f"Do not present this as stronger proof than the source supports: {statement}",
            source_ids=source_ids,
            public_evidence_item_ids=item_ids,
            claim_ids=(claim_id,),
            rule_ids=rule_ids,
            confidence="medium",
            allowed_use="doNotState",
            reason="Prevents citation injection from becoming unsupported certainty.",
        )

    @staticmethod
    def _external_claims(ledger: dict[str, Any]) -> list[dict[str, Any]]:
        return [claim for claim in _records(ledger.get("claims")) if claim.get("type") == "externalEvidenceClaim"]

    @staticmethod
    def _rule_ids(rule_pack: dict[str, Any]) -> tuple[str, ...]:
        registry = _record(rule_pack.get("ruleRegistrySnapshot"))
        return tuple(str(rule.get("id")) for rule in _records(registry.get("rules"))[:8] if rule.get("id"))

    @staticmethod
    def _source_ids(provenance: dict[str, Any]) -> tuple[str, ...]:
        values = [provenance.get("sourceUrl"), provenance.get("sourceTitle"), provenance.get("attemptId")]
        return tuple(str(value) for value in values if value)

    @staticmethod
    def _warnings(
        context_artifact: dict[str, Any],
        public_evidence: dict[str, Any],
        claims: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        warnings = []
        if not claims:
            warnings.append({
                "id": "evidence-interpretation-no-external-claims",
                "message": "No accepted external ledger claims were available for editorial interpretation.",
                "source": "evidenceInterpretation",
            })
        for warning in _records(public_evidence.get("warnings"))[:8]:
            warnings.append({
                "id": f"public-evidence-{warning.get('code') or len(warnings) + 1}",
                "message": str(warning.get("message") or warning.get("detail") or ""),
                "source": "publicEvidence",
            })
        if _record(context_artifact.get("evidenceSynthesis")).get("fallbackUsed"):
            warnings.append({
                "id": "evidence-synthesis-fallback",
                "message": "Evidence synthesis used fallback; interpretation should stay conservative.",
                "source": "evidenceSynthesis",
            })
        return warnings

    @staticmethod
    def _allowed_use(value: str) -> str:
        return value if value in {"canState", "needsQualification", "canUseAsFraming", "doNotState"} else "needsQualification"

    @staticmethod
    def _record(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _records(value: Any) -> list[dict[str, Any]]:
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

_limit_item = DeterministicEvidenceInterpretationPolicy._limit_item
_overclaim_item = DeterministicEvidenceInterpretationPolicy._overclaim_item
_external_claims = DeterministicEvidenceInterpretationPolicy._external_claims
_rule_ids = DeterministicEvidenceInterpretationPolicy._rule_ids
_source_ids = DeterministicEvidenceInterpretationPolicy._source_ids
_warnings = DeterministicEvidenceInterpretationPolicy._warnings
_allowed_use = DeterministicEvidenceInterpretationPolicy._allowed_use
_record = DeterministicEvidenceInterpretationPolicy._record
_records = DeterministicEvidenceInterpretationPolicy._records


DeterministicEvidenceInterpretationFallbackPolicy = DeterministicEvidenceInterpretationPolicy


__all__ = (
    'DeterministicEvidenceInterpretationService',
    'DeterministicEvidenceInterpretationPolicy',
    'DeterministicEvidenceInterpretationFallbackPolicy',
)
