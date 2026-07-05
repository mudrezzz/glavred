"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.draft_editorial_critique import EditorialCritiqueObservation
from backend.app.domain.draft_validation import DraftValidatorFinding, DraftValidatorStatus

_DIMENSIONS = {
    "ideaStrength",
    "tension",
    "authorStance",
    "readerValue",
    "sourceIntegration",
    "genericAiProse",
    "argumentDepth",
    "unsupportedLeap",
    "overCompression",
    "overExplanation",
}


class EditorialCritiqueParser:
    def parse(
        self,
        *,
        candidate_id: str,
        payload: dict[str, Any],
    ) -> tuple[list[DraftValidatorFinding], list[EditorialCritiqueObservation]]:
        findings = [self._finding(candidate_id, _dict(item)) for item in _list(payload.get("findings"))]
        observations = [self._observation(candidate_id, _dict(item)) for item in _list(payload.get("observations"))]
        return findings, observations

    def critique_dimension(self, value: Any) -> str:
        text = str(value or "").strip()
        return text if text in _DIMENSIONS else "ideaStrength"

    def editorial_risk(self, value: Any) -> str:
        text = str(value or "").strip().lower()
        return text if text in {"low", "medium", "high", "unknown"} else "unknown"

    def _finding(self, candidate_id: str, raw: dict[str, Any]) -> DraftValidatorFinding:
        dimension = self.critique_dimension(raw.get("editorialDimension") or raw.get("dimension"))
        return DraftValidatorFinding(
            validator_id=_critic_id(raw, dimension),
            severity=_severity(raw.get("severity")),
            candidate_id=candidate_id,
            message=str(raw.get("message") or "Editorial critic found an actionable weakness."),
            evidence_excerpt=str(raw.get("evidenceExcerpt") or "")[:500],
            repair_guidance=str(raw.get("repairGuidance") or raw.get("recommendedRepair") or "Strengthen this candidate editorially."),
            rule_ids=_strings(raw.get("ruleIds")),
            claim_ids=_strings(raw.get("claimIds")),
            metadata={**_dict(raw.get("metadata")), "editorialDimension": dimension},
        )

    def _observation(self, candidate_id: str, raw: dict[str, Any]) -> EditorialCritiqueObservation:
        dimension = self.critique_dimension(raw.get("editorialDimension") or raw.get("dimension"))
        return EditorialCritiqueObservation(
            critic_id=_critic_id(raw, dimension),
            candidate_id=candidate_id,
            message=str(raw.get("message") or "Editorial critic recorded an observation."),
            evidence_excerpt=str(raw.get("evidenceExcerpt") or "")[:500],
            editorial_dimension=dimension,
            metadata=_dict(raw.get("metadata")),
        )


def _critic_id(raw: dict[str, Any], dimension: str) -> str:
    value = str(raw.get("criticId") or raw.get("validatorId") or "").strip()
    if value:
        return value if value.startswith("critic.") else f"critic.{value}"
    return f"critic.{dimension}"


def _severity(value: Any) -> DraftValidatorStatus:
    return DraftValidatorStatus.CRITICAL if str(value or "").lower() == "critical" else DraftValidatorStatus.WARNING


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in _list(value) if str(item).strip()]
