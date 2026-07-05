"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any


class ExternalEvidenceSynthesisPromptsComponent:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def build_external_evidence_synthesis_messages(
        *,
        context_artifact: dict[str, Any],
        public_evidence: dict[str, Any],
    ) -> list[dict[str, str]]:
        brief = _as_dict(context_artifact.get("brief"))
        post_contract = _as_dict(context_artifact.get("postContract"))
        payload = {
            "task": "Synthesize accepted public evidence into conservative ledger claims. Return strict JSON only.",
            "brief": {
                "title": brief.get("title"),
                "thesis": brief.get("thesis"),
                "authorPosition": brief.get("authorPosition"),
            },
            "postContract": {
                "thesis": post_contract.get("thesis"),
                "audience": post_contract.get("audience"),
                "goal": post_contract.get("goal"),
            },
            "publicEvidenceItems": public_evidence.get("items") or [],
            "publicEvidenceWarnings": public_evidence.get("warnings") or [],
            "rules": [
                "Do not invent facts beyond publicEvidenceItems.",
                "Do not treat failed, skipped, rejected, or notConfigured attempts as proof.",
                "Use canState only for directly source-backed claims.",
                "Use needsQualification for interpretive summaries or broad claims.",
                "Use canUseAsFraming for context only.",
                "Use doNotState if evidence is unsafe, irrelevant, or contradictory.",
            ],
            "expected_json": {
                "externalClaims": [{
                    "publicEvidenceItemId": "id from publicEvidenceItems",
                    "statement": "source-backed claim",
                    "allowedUse": "canState|needsQualification|canUseAsFraming|doNotState",
                    "confidence": "high|medium|low|unknown",
                    "decision": "mergeDirectClaim|mergeQualifiedClaim|useAsFraming|doNotState",
                    "rationale": "why this use is allowed",
                    "riskFlags": ["optional flags"],
                }],
                "warnings": [{"code": "short-code", "message": "warning", "publicEvidenceItemId": "optional"}],
                "decisions": [{"decision": "short decision", "detail": "explanation"}],
            },
        }
        return [
            {"role": "system", "content": "You are Glavred's evidence synthesis analyst. Return strict JSON only."},
            {"role": "user", "content": _json(payload)},
        ]

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _json(value: Any) -> str:
        import json

        return json.dumps(value, ensure_ascii=False, indent=2)

build_external_evidence_synthesis_messages = ExternalEvidenceSynthesisPromptsComponent.build_external_evidence_synthesis_messages
_as_dict = ExternalEvidenceSynthesisPromptsComponent._as_dict
_json = ExternalEvidenceSynthesisPromptsComponent._json


__all__ = (
    'build_external_evidence_synthesis_messages',
    'ExternalEvidenceSynthesisPromptsComponent',
)
