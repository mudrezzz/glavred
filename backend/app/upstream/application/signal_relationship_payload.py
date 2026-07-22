"""Owner: upstream.application

Used by: signal utility payload validation.
Does not own: signal scoring dimensions, retry behavior, or relationship decisions.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.upstream.domain.signal_utility import SignalRelationshipKind, SignalUtilityDossier


class SignalRelationshipPayloadMapper:
    def map(
        self,
        value: Any,
        dossier: SignalUtilityDossier,
        errors: list[str],
    ) -> dict[str, dict[str, str]]:
        if value is None:
            return {}
        if not isinstance(value, list):
            errors.append("relationships-must-be-list")
            return {}
        result: dict[str, dict[str, str]] = {}
        for raw in value:
            if not isinstance(raw, dict):
                errors.append("relationship-must-be-object")
                continue
            pair_id = str(raw.get("pairId") or "")
            if pair_id not in dossier.relationship_pair_ids:
                errors.append(f"unknown-relationship-pair:{pair_id or '<blank>'}")
                continue
            if pair_id in result:
                errors.append(f"duplicate-relationship-pair:{pair_id}")
                continue
            try:
                kind = SignalRelationshipKind(str(raw.get("kind") or ""))
            except ValueError:
                errors.append(f"unknown-relationship-kind:{pair_id}")
                continue
            summary = " ".join(str(raw.get("summary") or "").split())
            if not summary:
                errors.append(f"missing-relationship-summary:{pair_id}")
            result[pair_id] = {"kind": kind.value, "summary": summary[:500]}
        return result


__all__ = ("SignalRelationshipPayloadMapper",)
