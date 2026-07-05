"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import json
from typing import Any

DIRECTED_REVISION_KEYS = {"title", "body", "changeLog"}
DIRECTED_REVISION_TEMPERATURE = 0.2


class DirectedRevisionPromptBuilder:
    """Owns directed-revision provider message construction."""

    def build_messages(
        self,
        *,
        candidate: dict[str, Any],
        instruction: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        context_pack: dict[str, Any] | None = None,
        repair_context: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        system = (
            "You are Glavred's directed revision editor. Return strict JSON only. "
            "Improve only the listed validator/editorial goals. Preserve contract, claims, "
            "forbidden moves, route, grounding, and anti-regression constraints. "
            "Do not mechanically expose internal pipeline artifact names as dev-jargon, "
            "such as SourceLedger, publicEvidence, validators, RuleRegistry, or PostContract in public prose. "
            "Use them only if you intentionally frame and explain them as reader-facing concepts."
        )
        payload = {
            "task": "Revise the selected draft candidate once.",
            "requiredJson": {"title": "string", "body": "string", "changeLog": ["what changed"]},
            "candidate": candidate,
            "revisionInstruction": instruction,
            "postContract": context_artifact.get("postContract"),
            "ruleRegistry": rule_pack.get("ruleRegistrySnapshot"),
            "materialPlan": material_plan,
            "contextPack": context_pack or {},
            "sourceLedger": context_artifact.get("sourceLedger"),
            "repairContext": repair_context,
            "editorialGoalContract": {
                "dimensions": ["ideaStrength", "tension", "readerValue", "authorStance", "sourceIntegration", "structure", "validatorHealth"],
                "rules": [
                    "Make targeted editorial improvements only.",
                    "Preserve working source markers.",
                    "Do not repeat rejected moves.",
                    "Avoid internal pipeline jargon unless it is explicitly explained as a public concept.",
                    "If unsafe, leave unchanged and explain in changeLog.",
                ],
            },
        }
        return [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]
