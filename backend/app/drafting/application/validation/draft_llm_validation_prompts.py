"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

LLM_VALIDATION_KEYS = {"findings", "summary"}
LLM_VALIDATION_TEMPERATURE = 0.1


class LlmValidationPromptBuilder:
    def build_messages(
        self,
        *,
        candidate: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        deterministic_report: dict[str, Any],
        context_pack: dict[str, Any] | None = None,
        repair_context: dict[str, Any] | None = None,
    ) -> list[dict[str, str]]:
        payload = {
            "task": "Validate one Glavred draft candidate. Return strict JSON only.",
            "candidate": candidate,
            "sourceLedger": context_artifact.get("sourceLedger"),
            "postContract": context_artifact.get("postContract"),
            "ruleRegistrySnapshot": rule_pack.get("ruleRegistrySnapshot"),
            "contextPack": context_pack or {},
            "materialPlan": material_plan,
            "deterministicReport": deterministic_report,
            "requiredJson": {
                "summary": "short validator summary",
                "observations": [
                    {
                        "validatorId": "llm.source-grounding|llm.publisher-fit|llm.topic-fabula-fit|llm.coherence|llm.audience-value",
                        "status": "pass|positive|observation",
                        "ruleIds": ["rule ids when relevant"],
                        "claimIds": ["claim ids when relevant"],
                        "message": "positive or pass observation",
                        "evidenceExcerpt": "draft excerpt or claim reference",
                        "repairGuidance": "No repair needed",
                        "metadata": {"dimension": "sourceGrounding|publisherFit|topicFabulaFit|coherence|audienceValue"},
                    }
                ],
                "findings": [
                    {
                        "validatorId": "llm.source-grounding|llm.publisher-fit|llm.topic-fabula-fit|llm.coherence|llm.audience-value",
                        "severity": "warning|critical",
                        "ruleIds": ["rule ids when relevant"],
                        "claimIds": ["claim ids when relevant"],
                        "message": "human readable issue",
                        "evidenceExcerpt": "draft excerpt or claim reference",
                        "repairGuidance": "specific repair instruction",
                        "metadata": {"dimension": "sourceGrounding|publisherFit|topicFabulaFit|coherence|audienceValue"},
                    }
                ],
            },
            "rules": [
                "Do not invent provenance. Reference only provided ruleIds and claimIds.",
                "Put only actionable issues in findings. Positive checks and pass notes go into observations.",
                "Return empty findings when the candidate passes the LLM review, and record pass notes in observations.",
                "Findings are report-only. Do not rewrite the draft.",
            ],
        }
        if repair_context:
            payload["repairContext"] = repair_context
        return [
            {
                "role": "system",
                "content": (
                    "You are Glavred's editorial validator. Return strict JSON only. "
                    "Validate source grounding, publisher fit, topic/fabula fit, coherence, compression, and audience value."
                ),
            },
            {"role": "user", "content": _to_json_like(payload)},
        ]


def _to_json_like(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, sort_keys=True)
