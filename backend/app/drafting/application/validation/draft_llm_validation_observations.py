"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.draft_llm_validation import LlmValidatorObservation
from backend.app.domain.draft_validation import DraftValidatorStatus


PASS_STATUSES = {"pass", "passed", "ok", "info", "observation", "positive", "none"}
NO_REPAIR_VALUES = {"no repair needed", "no repair needed.", "none", "n/a", "not needed"}


class LlmValidationObservationNormalizer:
    def normalize_validator_id(self, raw: dict[str, Any]) -> str:
        validator_id = str(raw.get("validatorId") or "llm.editorial-quality")
        return validator_id if validator_id.startswith("llm.") else f"llm.{validator_id}"

    def is_observation_like(self, raw: dict[str, Any]) -> bool:
        severity = str(raw.get("severity") or raw.get("status") or raw.get("result") or "").strip().lower()
        if severity in PASS_STATUSES:
            return True
        if severity == DraftValidatorStatus.CRITICAL.value:
            return False
        return str(raw.get("repairGuidance") or "").strip().lower() in NO_REPAIR_VALUES

    def observation(
        self,
        *,
        candidate_id: str,
        payload: dict[str, Any],
        raw: dict[str, Any],
    ) -> LlmValidatorObservation:
        return LlmValidatorObservation(
            validator_id=self.normalize_validator_id(raw),
            candidate_id=candidate_id,
            message=str(raw.get("message") or raw.get("summary") or "LLM validator reported a positive observation."),
            evidence_excerpt=str(raw.get("evidenceExcerpt") or "")[:500],
            repair_guidance=str(raw.get("repairGuidance") or ""),
            rule_ids=_strings(raw.get("ruleIds")),
            claim_ids=_strings(raw.get("claimIds")),
            metadata={**_dict(raw.get("metadata")), "llmSummary": str(payload.get("summary") or "")},
        )


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in _list(value) if str(item).strip()]
