import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft
from backend.app.settings import BackendSettings


@dataclass(frozen=True)
class OpenRouterDraftResult:
    draft: GeneratedDraft
    raw_response: dict[str, Any]


class OpenRouterDraftAdapter:
    def generate(self, settings: BackendSettings, request: DraftGenerationRequest) -> OpenRouterDraftResult:
        api_key = settings.openrouter_api_key.get_secret_value() if settings.openrouter_api_key else ""
        response = httpx.post(
            f"{settings.openrouter_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": settings.openrouter_http_referer,
                "X-OpenRouter-Title": settings.openrouter_app_name,
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openrouter_default_model,
                "messages": self._messages(request),
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
            },
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
        content = self._extract_content(payload)
        draft_payload = json.loads(content)
        title = str(draft_payload.get("title", "")).strip()
        body = str(draft_payload.get("body", "")).strip()
        if not title or not body:
            raise ValueError("OpenRouter response did not include non-empty title and body")

        return OpenRouterDraftResult(
            draft=GeneratedDraft(
                id=f"draft-{request.brief.id}",
                brief_id=request.brief.id,
                title=title,
                body=body,
                version=1,
                status="draft",
                updated_at=datetime.now(UTC).isoformat(),
            ),
            raw_response={
                "id": payload.get("id"),
                "model": payload.get("model"),
                "usage": payload.get("usage"),
            },
        )

    def _messages(self, request: DraftGenerationRequest) -> list[dict[str, str]]:
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

    def _extract_content(self, payload: dict[str, Any]) -> str:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("OpenRouter response did not include choices")
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, str):
            return content
        raise ValueError("OpenRouter response did not include text content")
