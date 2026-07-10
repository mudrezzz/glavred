"""Owner: drafting.application.context

Used by: DraftRunContextAccessService for compact contract, evidence, and rule reads.
Does not own: dossier policy, prompt construction, provider calls, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.app.drafting.application.context.draft_run_artifact_index import DraftRunArtifactIndex
from backend.app.drafting.domain.provider_dossier import ArtifactHandle, ContextSelection


class ContractEvidenceContextReader:
    def __init__(self, index: DraftRunArtifactIndex) -> None:
        self._index = index

    def post_contract(self) -> ContextSelection:
        contract = self._mapping(self._index.step_payload("postContract"))
        if not contract:
            return self._missing("postContract")
        compact: dict[str, Any] = {
            key: contract.get(key)
            for key in (
                "title", "thesis", "audience", "value", "goal", "cta", "platform", "publicationSizeContract",
            )
            if contract.get(key) not in (None, [], {})
        }
        trimmed = 0
        for key, fields, limit in (
            ("claims", ("id", "allowedUse", "qualification"), 12),
            ("forbiddenMoves", (), 8),
            ("evidenceObligations", ("id", "kind", "statement", "source"), 8),
            ("fabulaObligations", ("id", "kind", "statement", "source"), 8),
            ("riskNotes", (), 8),
        ):
            values = contract.get(key) if isinstance(contract.get(key), list) else []
            selected = values[:limit]
            compact[key] = [self._select(item, fields) if fields and isinstance(item, Mapping) else self._bounded_text(item) for item in selected]
            trimmed += max(0, len(values) - len(selected))
        handle = self._handle("postContract", (), "postContract", "artifact")
        return ContextSelection("postContract", compact, (handle,), total_count=1, selected_count=1, trimmed_count=trimmed)

    def evidence(self, limit: int = 12) -> ContextSelection:
        records: list[tuple[dict[str, Any], ArtifactHandle]] = []
        public = self._mapping(self._index.step_payload("publicEvidence"))
        ledger = self._mapping(public.get("enrichedSourceLedger"))
        for index, claim in enumerate(self._records(ledger.get("claims"))):
            if claim.get("allowedUse") == "doNotState":
                continue
            compact = {
                key: self._bounded_text(claim.get(key))
                for key in ("id", "statement", "allowedUse", "confidence", "riskFlags", "source")
                if claim.get(key) not in (None, [], {})
            }
            records.append((compact, self._handle("publicEvidence", ("enrichedSourceLedger", "claims", index), "evidence", str(claim.get("id") or "artifact"))))

        rule_pack = self._mapping(self._index.step_payload("rulePack"))
        interpretation = self._mapping(rule_pack.get("evidenceInterpretation"))
        for index, implication in enumerate(self._records(interpretation.get("implications"))):
            compact = {
                key: self._bounded_text(implication.get(key))
                for key in ("id", "title", "summary", "allowedUse", "confidence", "claimIds", "ruleIds")
                if implication.get(key) not in (None, [], {})
            }
            records.append((compact, self._handle("rulePack", ("evidenceInterpretation", "implications", index), "evidenceInterpretation", str(implication.get("id") or "artifact"))))

        records.sort(key=lambda item: (str(item[0].get("id") or ""), str(item[0].get("title") or "")))
        return self._limited("evidence", records, limit)

    def claims(self, limit: int = 12) -> ContextSelection:
        evidence = self.evidence(limit)
        claims = [item for item in evidence.copied_value() if item.get("statement") or item.get("summary")]
        return ContextSelection(
            "claims", claims, evidence.handles, evidence.available,
            evidence.total_count, len(claims), evidence.trimmed_count,
        )

    def rules(self, limit: int = 16) -> ContextSelection:
        rule_pack = self._mapping(self._index.step_payload("rulePack"))
        snapshot = self._mapping(rule_pack.get("ruleRegistrySnapshot"))
        records: list[tuple[dict[str, Any], ArtifactHandle]] = []
        for index, rule in enumerate(self._records(snapshot.get("rules"))):
            compact = {
                key: self._bounded_text(rule.get(key))
                for key in ("id", "scope", "category", "title", "statement", "priority", "severity", "claimIds", "contractRefs")
                if rule.get(key) not in (None, [], {})
            }
            records.append((compact, self._handle("rulePack", ("ruleRegistrySnapshot", "rules", index), "rule", str(rule.get("id") or "artifact"))))
        records.sort(key=lambda item: (int(item[0].get("priority") or 999), str(item[0].get("id") or "")))
        return self._limited("rules", records, limit)

    def _limited(self, key: str, records: list[tuple[dict[str, Any], ArtifactHandle]], limit: int) -> ContextSelection:
        selected = records[: max(0, limit)]
        return ContextSelection(
            key,
            [item for item, _ in selected],
            tuple(handle for _, handle in selected),
            available=bool(records),
            total_count=len(records),
            selected_count=len(selected),
            trimmed_count=max(0, len(records) - len(selected)),
        )

    def _handle(self, step_key: str, path: tuple[str | int, ...], artifact_type: str, artifact_id: str) -> ArtifactHandle:
        return ArtifactHandle.create(
            run_id=self._index.run_id,
            step_key=step_key,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            path=path,
        )

    def _missing(self, key: str) -> ContextSelection:
        return ContextSelection(key, None, available=False)

    def _mapping(self, value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    def _records(self, value: Any) -> list[dict[str, Any]]:
        return [dict(item) for item in value] if isinstance(value, list) else []

    def _select(self, value: Mapping[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
        return {key: self._bounded_text(value.get(key)) for key in fields if value.get(key) not in (None, [], {})}

    def _bounded_text(self, value: Any) -> Any:
        if isinstance(value, str):
            return value[:1200]
        if isinstance(value, list):
            return [self._bounded_text(item) for item in value[:12]]
        return value


__all__ = ("ContractEvidenceContextReader",)
