"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import json
from typing import Any

ALTERNATIVE_ANGLE_TEMPERATURE = 0.45
ALTERNATIVE_ANGLE_KEYS = {
    "id",
    "title",
    "angle",
    "openingMove",
    "whyDifferent",
    "critiqueInputs",
    "claimsToUse",
    "claimsToAvoid",
    "rulesToStress",
    "risks",
}


def build_alternative_angle_messages(
    *,
    draft_artifact: dict[str, Any],
    validation_report: dict[str, Any],
    context_artifact: dict[str, Any],
    rule_pack: dict[str, Any],
    material_plan: dict[str, Any],
    context_pack: dict[str, Any] | None = None,
    repair_context: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    payload = {
        "task": "Create one genuinely different editorial route for the same approved post contract.",
        "rules": [
            "Return strict JSON only.",
            "Do not create a technical backup or small rewrite of the current winner.",
            "Use critic findings, weak moves, rejected moves, tensions, and open questions.",
            "Preserve the approved thesis, allowed claims, forbidden moves, and size contract.",
            "Do not invent evidence; use only claim ids and evidence already available.",
        ],
        "expectedShape": {key: "string or string[]" for key in sorted(ALTERNATIVE_ANGLE_KEYS)},
        "draftArtifact": _compact_draft(draft_artifact),
        "validationReport": validation_report,
        "postContract": context_artifact.get("postContract"),
        "ruleRegistrySnapshot": rule_pack.get("ruleRegistrySnapshot"),
        "materialPlan": material_plan,
        "contextPack": context_pack or {},
        "repairContext": repair_context or {},
        "outputLanguage": "ru",
    }
    return [
        {
            "role": "system",
            "content": (
                "You are Glavred's alternative-angle editor. Your job is to escape a mediocre "
                "local optimum by proposing one different but contract-safe route. Return JSON only."
            ),
        },
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def _compact_draft(draft_artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "selection": draft_artifact.get("selection"),
        "directions": draft_artifact.get("directions"),
        "candidates": [
            {
                "id": item.get("id"),
                "rhetoricalPlanId": item.get("rhetoricalPlanId"),
                "title": item.get("title"),
                "rationale": item.get("rationale"),
                "risks": item.get("risks"),
                "weaknesses": item.get("weaknesses"),
            }
            for item in draft_artifact.get("candidates", [])
            if isinstance(item, dict)
        ],
    }
