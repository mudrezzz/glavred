"""Owner: upstream.application

Used by: signal utility scoring and canonical signal presentation.
Does not own: provider transport, project utility, persistence, or human review.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from collections import defaultdict
from difflib import SequenceMatcher
import re
from typing import Any

from backend.app.upstream.domain.signal_utility import (
    SignalRelationship,
    SignalRelationshipKind,
    SignalRelationshipReport,
)


class SignalRelationshipPolicy:
    MAX_PAIRS = 15
    _STOP_WORDS = frozenset({"в", "во", "как", "для", "и", "или", "по", "на", "это", "модуль"})

    def candidate_payload(self, signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        for index, left in enumerate(signals):
            for right in signals[index + 1:]:
                relation, reasons = self._deterministic_relation(left, right)
                if relation != SignalRelationshipKind.DISTINCT or self._title_similarity(left, right) >= 0.45:
                    left_id, right_id = self._ordered_ids(left, right)
                    candidates.append({
                        "pairId": f"{left_id}|{right_id}",
                        "leftSignalId": left_id,
                        "rightSignalId": right_id,
                        "deterministicHint": relation.value,
                        "reasonCodes": reasons,
                    })
        return candidates[: self.MAX_PAIRS]

    def reports(
        self,
        signals: list[dict[str, Any]],
        provider_relations: dict[str, dict[str, str]] | None = None,
    ) -> dict[str, SignalRelationshipReport]:
        by_id = {str(item.get("id") or ""): item for item in signals}
        provider_candidate_ids = {
            str(item["pairId"])
            for item in self.candidate_payload(signals)
        }
        relations: dict[str, list[SignalRelationship]] = defaultdict(list)
        for index, left in enumerate(signals):
            for right in signals[index + 1:]:
                left_id, right_id = self._ordered_ids(left, right)
                pair_id = f"{left_id}|{right_id}"
                deterministic, _ = self._deterministic_relation(left, right)
                provider = (provider_relations or {}).get(pair_id)
                kind = self._provider_kind(provider)
                if kind is None:
                    if deterministic == SignalRelationshipKind.DISTINCT:
                        if pair_id not in provider_candidate_ids:
                            continue
                        kind = SignalRelationshipKind.INCONCLUSIVE
                    else:
                        kind = deterministic
                summary = str((provider or {}).get("summary") or self._summary(kind))
                refs = self._shared_evidence(left, right)
                relations[left_id].append(SignalRelationship(right_id, kind, summary, refs))
                relations[right_id].append(SignalRelationship(left_id, kind, summary, refs))
        canonical = self._canonical_ids(signals, relations)
        return {
            signal_id: SignalRelationshipReport(
                status="checked" if relations.get(signal_id) else "notChecked",
                canonical_signal_id=canonical.get(signal_id, signal_id),
                relations=tuple(relations.get(signal_id, [])),
            )
            for signal_id in by_id
        }

    def _deterministic_relation(
        self, left: dict[str, Any], right: dict[str, Any]
    ) -> tuple[SignalRelationshipKind, list[str]]:
        raw_left_title = str(left.get("title") or "")
        raw_right_title = str(right.get("title") or "")
        left_title = self._normalize(raw_left_title)
        right_title = self._normalize(raw_right_title)
        same_material = bool(self._materials(left) & self._materials(right))
        same_fragment = bool(self._fragments(left) & self._fragments(right))
        if (
            same_material
            and self._basic_normalize(raw_left_title)
            and self._basic_normalize(raw_left_title) == self._basic_normalize(raw_right_title)
            and str(left.get("type")) == str(right.get("type"))
        ):
            return SignalRelationshipKind.EXACT_DUPLICATE, ["same-type", "normalized-title-equal"]
        similarity = SequenceMatcher(None, left_title, right_title).ratio()
        if same_material and (similarity >= 0.82 or (same_fragment and similarity >= 0.65)):
            return SignalRelationshipKind.SAME_CLAIM, ["near-identical-title", *( ["shared-fragment"] if same_fragment else [])]
        if same_material:
            return SignalRelationshipKind.RELATED_SAME_SOURCE, ["shared-material", "distinct-claim"]
        if similarity >= 0.82:
            return SignalRelationshipKind.CORROBORATES, ["same-claim", "different-material"]
        codes = {str(item) for item in (*left.get("reasonCodes", []), *right.get("reasonCodes", []))}
        if "contradiction" in codes:
            return SignalRelationshipKind.CONTRADICTS, ["structured-contradiction"]
        return SignalRelationshipKind.DISTINCT, ["no-material-or-claim-overlap"]

    def _canonical_ids(
        self,
        signals: list[dict[str, Any]],
        relations: dict[str, list[SignalRelationship]],
    ) -> dict[str, str]:
        by_id = {str(item.get("id") or ""): item for item in signals}
        canonical = {signal_id: signal_id for signal_id in by_id}
        for signal_id, items in relations.items():
            duplicate_ids = [item.other_signal_id for item in items if item.kind in {SignalRelationshipKind.EXACT_DUPLICATE, SignalRelationshipKind.SAME_CLAIM}]
            if not duplicate_ids:
                continue
            group = [signal_id, *duplicate_ids]
            winner = sorted(group, key=lambda item: (-len(by_id.get(item, {}).get("evidenceRefs") or []), item))[0]
            for item in group:
                canonical[item] = winner
        return canonical

    def _provider_kind(self, value: dict[str, str] | None) -> SignalRelationshipKind | None:
        if not value:
            return None
        try:
            return SignalRelationshipKind(value.get("kind", ""))
        except ValueError:
            return None

    def _ordered_ids(self, left: dict[str, Any], right: dict[str, Any]) -> tuple[str, str]:
        return tuple(sorted((str(left.get("id") or ""), str(right.get("id") or ""))))  # type: ignore[return-value]

    def _title_similarity(self, left: dict[str, Any], right: dict[str, Any]) -> float:
        return SequenceMatcher(None, self._normalize(str(left.get("title") or "")), self._normalize(str(right.get("title") or ""))).ratio()

    def _normalize(self, value: str) -> str:
        tokens = [item for item in re.sub(r"[^\w]+", " ", value.casefold()).split() if item not in self._STOP_WORDS]
        return " ".join(tokens)

    def _basic_normalize(self, value: str) -> str:
        return " ".join(re.sub(r"[^\w]+", " ", value.casefold()).split())

    def _materials(self, signal: dict[str, Any]) -> set[str]:
        return {str(item.get("materialId")) for item in signal.get("evidenceRefs") or [] if isinstance(item, dict) and item.get("materialId")}

    def _fragments(self, signal: dict[str, Any]) -> set[str]:
        return {str(item.get("fragmentId")) for item in signal.get("evidenceRefs") or [] if isinstance(item, dict) and item.get("fragmentId")}

    def _shared_evidence(self, left: dict[str, Any], right: dict[str, Any]) -> tuple[dict[str, str], ...]:
        refs = []
        for item in [*(left.get("evidenceRefs") or []), *(right.get("evidenceRefs") or [])]:
            if not isinstance(item, dict) or not item.get("materialId") or not item.get("fragmentId"):
                continue
            ref = {"materialId": str(item["materialId"]), "fragmentId": str(item["fragmentId"])}
            if ref not in refs:
                refs.append(ref)
        return tuple(refs)

    def _summary(self, kind: SignalRelationshipKind) -> str:
        return {
            SignalRelationshipKind.EXACT_DUPLICATE: "Совпадают тип и нормализованное утверждение; используется одна каноническая карточка.",
            SignalRelationshipKind.SAME_CLAIM: "Сигналы выражают один основной тезис и объединены в каноническую группу.",
            SignalRelationshipKind.RELATED_SAME_SOURCE: "Сигналы извлечены из одного материала, но описывают разные тезисы.",
            SignalRelationshipKind.CORROBORATES: "Другой материал подтверждает тот же основной тезис.",
            SignalRelationshipKind.CONTRADICTS: "Сигналы содержат структурированное противоречие.",
            SignalRelationshipKind.DISTINCT: "Значимого пересечения тезисов и доказательств не найдено.",
            SignalRelationshipKind.INCONCLUSIVE: "Данных недостаточно для честного определения связи.",
        }[kind]


__all__ = ("SignalRelationshipPolicy",)
