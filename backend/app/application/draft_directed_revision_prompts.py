from typing import Any

DIRECTED_REVISION_KEYS = {"title", "body", "changeLog"}
DIRECTED_REVISION_TEMPERATURE = 0.2


def build_directed_revision_messages(
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
        "Improve only the listed validator and editorial goals. Preserve the post contract, "
        "allowed claims, forbidden moves, rhetorical route, source grounding, and every "
        "anti-regression constraint."
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
            "rules": ["Make targeted editorial improvements only.", "Preserve working source markers.", "Do not repeat rejected moves.", "If unsafe, leave unchanged and explain in changeLog."],
        },
    }
    return [{"role": "system", "content": system}, {"role": "user", "content": _json(payload)}]


def _json(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)
