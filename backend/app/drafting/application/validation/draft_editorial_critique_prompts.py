"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import json
from typing import Any

EDITORIAL_CRITIQUE_KEYS = {
    "summary",
    "editorialRisk",
    "overallJudgment",
    "strongestMove",
    "weakestMove",
    "recommendedEditorialMove",
    "findings",
    "observations",
}
EDITORIAL_CRITIQUE_TEMPERATURE = 0.2


class EditorialCritiquePromptBuilder:
    def build_messages(
        self,
        *,
        candidate: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        deterministic_report: dict[str, Any],
        llm_validation_report: dict[str, Any],
        context_pack: dict[str, Any] | None = None,
        repair_context: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        payload: dict[str, Any] = {
            "task": "Critique one Glavred draft candidate as an editor-prosecutor. Return strict JSON only.",
            "candidate": candidate,
            "postContract": context_artifact.get("postContract"),
            "sourceLedger": context_artifact.get("sourceLedger"),
            "ruleRegistrySnapshot": rule_pack.get("ruleRegistrySnapshot"),
            "evidenceInterpretation": rule_pack.get("evidenceInterpretation"),
            "materialPlan": material_plan,
            "contextPack": context_pack or {},
            "deterministicReport": deterministic_report,
            "llmValidationReport": llm_validation_report,
            "requiredJson": {
                "summary": "short editorial critique summary",
                "editorialRisk": "low|medium|high",
                "overallJudgment": "one paragraph on whether this works as a post",
                "strongestMove": "best editorial move in this candidate",
                "weakestMove": "weakest editorial move in this candidate",
                "recommendedEditorialMove": "one concrete next editorial move",
                "observations": [
                    {
                        "criticId": "critic.ideaStrength|critic.tension|critic.authorStance|critic.readerValue|critic.sourceIntegration|critic.genericAiProse|critic.argumentDepth|critic.unsupportedLeap|critic.overCompression|critic.overExplanation",
                        "editorialDimension": "ideaStrength|tension|authorStance|readerValue|sourceIntegration|genericAiProse|argumentDepth|unsupportedLeap|overCompression|overExplanation",
                        "message": "positive or neutral observation",
                        "evidenceExcerpt": "short draft excerpt",
                        "metadata": {"whyItMatters": "short reason"},
                    }
                ],
                "findings": [
                    {
                        "criticId": "critic.ideaStrength|critic.tension|critic.authorStance|critic.readerValue|critic.sourceIntegration|critic.genericAiProse|critic.argumentDepth|critic.unsupportedLeap|critic.overCompression|critic.overExplanation",
                        "severity": "warning|critical",
                        "editorialDimension": "ideaStrength|tension|authorStance|readerValue|sourceIntegration|genericAiProse|argumentDepth|unsupportedLeap|overCompression|overExplanation",
                        "ruleIds": ["rule ids when relevant"],
                        "claimIds": ["claim ids when relevant"],
                        "message": "actionable editorial weakness",
                        "evidenceExcerpt": "short draft excerpt",
                        "repairGuidance": "specific editorial repair instruction",
                        "metadata": {"whyItMatters": "short reason"},
                    }
                ],
            },
            "rules": [
                "Do not validate formal contract compliance; validators already do that.",
                "Attack editorial quality: boring thought, weak tension, missing author stance, forced references, generic AI prose, unsupported leap, unclear reader value.",
                "Put only actionable weaknesses in findings. Positive or neutral notes go into observations.",
                "Do not rewrite the draft. Do not change final selection. This report is diagnostic only.",
                "Reference only provided ruleIds and claimIds. Do not invent provenance.",
            ],
        }
        if repair_context:
            payload["repairContext"] = repair_context
        return [
            {
                "role": "system",
                "content": (
                    "You are Glavred's prosecutor-editor critic. Return strict JSON only. "
                    "You are not a validator and not a copywriter. Challenge the candidate's editorial strength, "
                    "idea tension, author stance, source integration, and reader value."
                ),
            },
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False, sort_keys=True)},
        ]
