"""Owner: drafting.application.artifacts

Used by: DraftRun artifact migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.draft_generation import (
    DraftBriefContext,
    DraftEditorialModelContext,
    DraftGenerationRequest,
    GeneratedDraft,
)
from backend.app.domain.draft_run_context import DraftRunContext
from backend.app.drafting.application.artifacts.draft_run_context_payloads import context_input_summary, context_to_payload


class DraftRunPayloadsDTO:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def request_to_payload(request: DraftGenerationRequest, draft_context: DraftRunContext | None = None) -> dict[str, Any]:
        payload = {
            "brief": {
                "id": request.brief.id,
                "title": request.brief.title,
                "rubric": request.brief.rubric,
                "audience": request.brief.audience,
                "thesis": request.brief.thesis,
                "conflict": request.brief.conflict,
                "authorPosition": request.brief.author_position,
                "evidence": request.brief.evidence,
                "examples": request.brief.examples,
                "structure": request.brief.structure,
                "cta": request.brief.cta,
                "risks": request.brief.risks,
                "sources": request.brief.sources,
            },
            "editorialModel": {
                "audience": request.editorial_model.audience,
                "styleRules": request.editorial_model.style_rules,
                "forbiddenTopics": request.editorial_model.forbidden_topics,
                "goals": request.editorial_model.goals,
            },
        }
        if draft_context is not None:
            payload["draftContext"] = context_to_payload(draft_context)
        return payload

    @staticmethod
    def request_from_payload(payload: dict[str, Any]) -> DraftGenerationRequest:
        brief = payload["brief"]
        model = payload["editorialModel"]
        return DraftGenerationRequest(
            brief=DraftBriefContext(
                id=brief["id"],
                title=brief["title"],
                rubric=brief.get("rubric", ""),
                audience=brief.get("audience", ""),
                thesis=brief["thesis"],
                conflict=brief.get("conflict", ""),
                author_position=brief.get("authorPosition", ""),
                evidence=list(brief.get("evidence", [])),
                examples=list(brief.get("examples", [])),
                structure=list(brief.get("structure", [])),
                cta=brief.get("cta", ""),
                risks=list(brief.get("risks", [])),
                sources=list(brief.get("sources", [])),
            ),
            editorial_model=DraftEditorialModelContext(
                audience=model.get("audience", ""),
                style_rules=list(model.get("styleRules", [])),
                forbidden_topics=list(model.get("forbiddenTopics", [])),
                goals=list(model.get("goals", [])),
            ),
        )

    @staticmethod
    def draft_to_payload(draft: GeneratedDraft) -> dict[str, Any]:
        return {
            "id": draft.id,
            "briefId": draft.brief_id,
            "title": draft.title,
            "body": draft.body,
            "version": draft.version,
            "status": draft.status,
            "updatedAt": draft.updated_at,
        }

    @staticmethod
    def payload_section(artifact: dict[str, Any], key: str) -> dict[str, Any]:
        value = artifact.get(key)
        return value if isinstance(value, dict) else {}

    @staticmethod
    def input_summary_from_request(request: DraftGenerationRequest, draft_context: DraftRunContext | None = None) -> dict[str, Any]:
        summary = {
            "briefId": request.brief.id,
            "title": request.brief.title,
            "rubric": request.brief.rubric,
            "audience": request.brief.audience or request.editorial_model.audience,
            "evidenceCount": len(request.brief.evidence),
            "ruleCount": len(request.editorial_model.style_rules),
            "goalCount": len(request.editorial_model.goals),
        }
        if draft_context is not None:
            summary["context"] = context_input_summary(draft_context)
        return summary

request_to_payload = DraftRunPayloadsDTO.request_to_payload
request_from_payload = DraftRunPayloadsDTO.request_from_payload
draft_to_payload = DraftRunPayloadsDTO.draft_to_payload
payload_section = DraftRunPayloadsDTO.payload_section
input_summary_from_request = DraftRunPayloadsDTO.input_summary_from_request


__all__ = (
    'request_to_payload',
    'request_from_payload',
    'draft_to_payload',
    'payload_section',
    'input_summary_from_request',
    'DraftRunPayloadsDTO',
)
