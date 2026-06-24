from typing import Any

RHETORICAL_PLAN_KEYS = {"plans"}
RHETORICAL_PLAN_TEMPERATURE = 0.35


def build_rhetorical_plan_messages(
    *,
    context_summary: dict[str, Any],
    rule_registry: dict[str, Any],
    post_contract: dict[str, Any],
    material_plan: dict[str, Any],
    draft_strategy: dict[str, Any],
    repair_context: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are Glavred's rhetorical planning agent. Return strict JSON only. "
                "Create 2-3 distinct Russian editorial routes for writing one post. "
                "Do not invent claims. Use claim ids and rule ids from the provided contract and registry."
            ),
        },
        {
            "role": "user",
            "content": _json_like(
                {
                    "task": "Build rhetorical plans before draft candidate generation.",
                    "expectedShape": {
                        "plans": [{
                            "id": "research|contrast|practical",
                            "title": "short Russian title",
                            "angle": "writing angle",
                            "openingMove": "opening move",
                            "moves": [{"label": "move label", "purpose": "why", "claimIds": ["claim-id"]}],
                            "claimsToUse": [{"claimId": "claim-id", "use": "support|frame|qualify", "caution": "optional"}],
                            "claimIdsToAvoid": ["claim-id"],
                            "requiredRuleIds": ["rule-id"],
                            "sizeIntent": "compact|standard|deep",
                            "ctaRoute": "CTA route",
                            "risks": ["risk"],
                            "whyThisPlan": "why this route is useful",
                        }]
                    },
                    "contextSummary": context_summary,
                    "postContract": post_contract,
                    "ruleRegistrySnapshot": rule_registry,
                    "materialPlan": material_plan,
                    "draftStrategy": draft_strategy,
                    "repairContext": repair_context,
                }
            ),
        },
    ]


def _json_like(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
