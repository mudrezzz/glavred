"""Owner: drafting.application.generation

Used by: DraftRun generation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import json

from backend.app.domain.draft_generation import DraftGenerationRequest


def build_draft_prompt_messages(request: DraftGenerationRequest) -> list[dict[str, str]]:
    brief = request.brief
    model = request.editorial_model
    return [
        {
            "role": "system",
            "content": (
                "You are Glavred, an editorial drafting assistant. "
                "Return strict JSON only with keys title and body. "
                "Write in Russian unless the source material clearly requires another language."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "brief": {
                        "title": brief.title,
                        "rubric": brief.rubric,
                        "audience": brief.audience,
                        "thesis": brief.thesis,
                        "conflict": brief.conflict,
                        "authorPosition": brief.author_position,
                        "evidence": brief.evidence,
                        "examples": brief.examples,
                        "structure": brief.structure,
                        "cta": brief.cta,
                        "risks": brief.risks,
                        "sources": brief.sources,
                    },
                    "editorialModel": {
                        "audience": model.audience,
                        "styleRules": model.style_rules,
                        "forbiddenTopics": model.forbidden_topics,
                        "goals": model.goals,
                    },
                },
                ensure_ascii=False,
            ),
        },
    ]
