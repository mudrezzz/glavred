import json
from typing import Any

from backend.app.domain.draft_candidates import DraftCandidateDirection

CANDIDATE_TEMPERATURE = 0.55
CANDIDATE_KEYS = {"title", "body", "rationale", "usedEvidence", "ruleCoverage", "risks", "weaknesses"}


def build_draft_candidate_messages(
    *,
    context_summary: dict[str, Any],
    rule_pack: dict[str, Any],
    material_plan: dict[str, Any],
    draft_strategy: dict[str, Any],
    direction: DraftCandidateDirection,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are Glavred's draft-writing agent. Return only valid JSON with keys: "
                "title, body, rationale, usedEvidence, ruleCoverage, risks, weaknesses. "
                "The draft must obey hard constraints and stay grounded in evidence."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "direction": direction.to_payload(),
                    "contextSummary": context_summary,
                    "rulePack": rule_pack,
                    "materialPlan": material_plan,
                    "draftStrategy": draft_strategy,
                    "outputLanguage": "ru",
                },
                ensure_ascii=False,
            ),
        },
    ]
