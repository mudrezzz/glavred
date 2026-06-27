from typing import Any


def build_source_research_plan_messages(
    *,
    context_artifact: dict[str, Any],
    source_intent: dict[str, Any],
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are Glavred's research planner. Return strict JSON only. "
                "Do not invent evidence and do not claim that you searched the web. "
                "Turn human-language source requests into a research plan with source targets, "
                "verification tasks, and query candidates."
            ),
        },
        {
            "role": "user",
            "content": _json_like({
                "task": "Build a research plan before public evidence retrieval.",
                "requiredKeys": [
                    "researchQuestions",
                    "sourceTargets",
                    "verificationTasks",
                    "queryCandidates",
                    "exclusions",
                    "warnings",
                    "metadata",
                ],
                "rules": [
                    "A plain request such as 'need opinions from opinion leaders' is a research request, not a raw keyword.",
                    "Query candidates are candidates for future search adapters, not proof.",
                    "Exclusions must remain exclusions.",
                    "Prefer credible public experts, primary sources, public reports, and interviews.",
                ],
                "context": {
                    "brief": context_artifact.get("brief"),
                    "candidate": context_artifact.get("candidate"),
                    "topic": context_artifact.get("topic"),
                    "fabula": context_artifact.get("fabula"),
                    "draftRunBudget": context_artifact.get("draftRunBudget"),
                },
                "sourceIntent": source_intent,
                "verificationTaskShape": {
                    "id": "string",
                    "kind": "readUrl|findPublicSources|verifyClaim|respectExclusion|useAsFraming",
                    "sourceIntentItemId": "string|null",
                    "instruction": "string",
                    "target": "string",
                    "priority": "high|medium|low",
                },
            }),
        },
    ]


def _json_like(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, ensure_ascii=False, indent=2)
