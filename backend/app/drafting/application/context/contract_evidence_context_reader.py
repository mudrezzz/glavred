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
            compact["kind"] = "claim"
            records.append((compact, self._handle("publicEvidence", ("enrichedSourceLedger", "claims", index), "evidence", str(claim.get("id") or "artifact"))))

        rule_pack = self._mapping(self._index.step_payload("rulePack"))
        interpretation = self._mapping(rule_pack.get("evidenceInterpretation"))
        for field_name, kind in (
            ("implications", "implication"),
            ("usableExamples", "usableExample"),
            ("limits", "limit"),
            ("forbiddenOverclaims", "forbiddenOverclaim"),
            ("rejectedEvidenceUses", "rejectedEvidenceUse"),
        ):
            for index, item in enumerate(self._records(interpretation.get(field_name))):
                compact = {
                    key: self._bounded_text(item.get(key))
                    for key in (
                        "id",
                        "title",
                        "summary",
                        "statement",
                        "reason",
                        "allowedUse",
                        "confidence",
                        "claimIds",
                        "ruleIds",
                        "sourceIds",
                    )
                    if item.get(key) not in (None, [], {})
                }
                compact["kind"] = kind
                records.append(
                    (
                        compact,
                        self._handle(
                            "rulePack",
                            ("evidenceInterpretation", field_name, index),
                            "evidenceInterpretation",
                            str(item.get("id") or f"{field_name}-{index}"),
                        ),
                    )
                )

        records = self._deduplicate_evidence(records)
        return self._curated_evidence(records, limit)

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

    def _curated_evidence(
        self,
        records: list[tuple[dict[str, Any], ArtifactHandle]],
        limit: int,
    ) -> ContextSelection:
        bounded_limit = max(0, limit)
        source_claims = sorted(
            [item for item in records if self._is_source_claim(item[0])],
            key=self._evidence_sort_key,
        )
        interpretations = sorted(
            [item for item in records if item[0].get("kind") != "claim"],
            key=self._evidence_sort_key,
        )
        framing_claims = sorted(
            [
                item
                for item in records
                if item[0].get("kind") == "claim" and not self._is_source_claim(item[0])
            ],
            key=self._evidence_sort_key,
        )
        source_quota = min(len(source_claims), max(1, bounded_limit // 2)) if bounded_limit else 0
        interpretation_quota = (
            min(len(interpretations), max(1, bounded_limit // 3)) if bounded_limit else 0
        )
        selected = source_claims[:source_quota] + interpretations[:interpretation_quota]
        selected_keys = {item[1].id for item in selected}
        remainder = source_claims[source_quota:] + interpretations[interpretation_quota:] + framing_claims
        for item in remainder:
            if len(selected) >= bounded_limit:
                break
            if item[1].id not in selected_keys:
                selected.append(item)
                selected_keys.add(item[1].id)
        return ContextSelection(
            "evidence",
            [item for item, _ in selected],
            tuple(handle for _, handle in selected),
            available=bool(records),
            total_count=len(records),
            selected_count=len(selected),
            trimmed_count=max(0, len(records) - len(selected)),
        )

    def _deduplicate_evidence(
        self,
        records: list[tuple[dict[str, Any], ArtifactHandle]],
    ) -> list[tuple[dict[str, Any], ArtifactHandle]]:
        unique: dict[tuple[str, str], tuple[dict[str, Any], ArtifactHandle]] = {}
        for item, handle in records:
            key = (str(item.get("kind") or "artifact"), str(item.get("id") or handle.id))
            unique.setdefault(key, (item, handle))
        return list(unique.values())

    def _is_source_claim(self, item: dict[str, Any]) -> bool:
        if item.get("kind") != "claim":
            return False
        allowed_use = str(item.get("allowedUse") or "")
        source = str(item.get("source") or "").lower()
        return allowed_use in {"canState", "needsQualification"} and not (
            source == "brief" or source.startswith("brief.") or source == "authorpositionevidence"
        )

    def _evidence_sort_key(
        self,
        record: tuple[dict[str, Any], ArtifactHandle],
    ) -> tuple[int, int, str]:
        item = record[0]
        allowed_rank = {
            "canState": 0,
            "needsQualification": 1,
            "canUseAsFraming": 2,
        }.get(str(item.get("allowedUse") or ""), 3)
        confidence_rank = {"high": 0, "medium": 1, "low": 2}.get(
            str(item.get("confidence") or ""),
            3,
        )
        return allowed_rank, confidence_rank, str(item.get("id") or item.get("title") or "")

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
