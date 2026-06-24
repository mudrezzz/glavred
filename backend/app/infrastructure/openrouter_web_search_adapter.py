from dataclasses import dataclass
from typing import Any

import httpx

from backend.app.settings import BackendSettings


@dataclass(frozen=True)
class OpenRouterWebSearchCitation:
    title: str
    url: str
    snippet: str


@dataclass(frozen=True)
class OpenRouterWebSearchResult:
    content: str
    citations: list[OpenRouterWebSearchCitation]
    raw_response: dict[str, Any]


class OpenRouterWebSearchAdapter:
    def search(self, *, settings: BackendSettings, query: str, messages: list[dict[str, str]]) -> OpenRouterWebSearchResult:
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
                "model": settings.openrouter_web_search_model_or_default,
                "messages": messages,
                "tools": [{"type": "openrouter:web_search", "parameters": {"max_results": settings.openrouter_web_search_max_results}}],
                "tool_choice": "auto",
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        message = _first_message(payload)
        return OpenRouterWebSearchResult(
            content=_content_text(message),
            citations=_extract_citations(message, payload),
            raw_response={
                "id": payload.get("id"),
                "model": payload.get("model"),
                "usage": payload.get("usage"),
                "query": query,
                "citationCount": len(_extract_citations(message, payload)),
            },
        )


def _first_message(payload: dict[str, Any]) -> dict[str, Any]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("OpenRouter web search response did not include choices")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict):
        raise ValueError("OpenRouter web search response did not include message")
    return message


def _content_text(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(item.get("text") or "") for item in content if isinstance(item, dict)).strip()
    return ""


def _extract_citations(message: dict[str, Any], payload: dict[str, Any]) -> list[OpenRouterWebSearchCitation]:
    citations: list[OpenRouterWebSearchCitation] = []
    for annotation in _annotation_records(message):
        citation = annotation.get("url_citation") if isinstance(annotation.get("url_citation"), dict) else annotation
        url = str(citation.get("url") or "").strip()
        if not url:
            continue
        citations.append(OpenRouterWebSearchCitation(
            title=str(citation.get("title") or url).strip(),
            url=url,
            snippet=str(citation.get("content") or citation.get("snippet") or citation.get("text") or "").strip(),
        ))
    for citation in payload.get("citations") if isinstance(payload.get("citations"), list) else []:
        if not isinstance(citation, dict):
            continue
        url = str(citation.get("url") or "").strip()
        if url and all(existing.url != url for existing in citations):
            citations.append(OpenRouterWebSearchCitation(
                title=str(citation.get("title") or url).strip(),
                url=url,
                snippet=str(citation.get("content") or citation.get("snippet") or "").strip(),
            ))
    return citations


def _annotation_records(message: dict[str, Any]) -> list[dict[str, Any]]:
    annotations = message.get("annotations")
    return [item for item in annotations if isinstance(item, dict)] if isinstance(annotations, list) else []
