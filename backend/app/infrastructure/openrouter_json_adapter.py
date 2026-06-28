import json
from dataclasses import dataclass
from typing import Any

import httpx

from backend.app.settings import BackendSettings


@dataclass(frozen=True)
class OpenRouterJsonResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class OpenRouterJsonResponseError(ValueError):
    def __init__(self, message: str, *, raw_response_excerpt: str | None = None) -> None:
        super().__init__(message)
        self.raw_response_excerpt = raw_response_excerpt


class OpenRouterJsonAdapter:
    def complete_json(
        self,
        *,
        settings: BackendSettings,
        messages: list[dict[str, str]],
        expected_keys: set[str],
        temperature: float,
        top_p: float | None = None,
        model: str | None = None,
    ) -> OpenRouterJsonResult:
        api_key = settings.openrouter_api_key.get_secret_value() if settings.openrouter_api_key else ""
        selected_model = model or settings.openrouter_default_model
        request_payload: dict[str, Any] = {
            "model": selected_model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        if top_p is not None:
            request_payload["top_p"] = top_p
        response = httpx.post(
            f"{settings.openrouter_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": settings.openrouter_http_referer,
                "X-OpenRouter-Title": settings.openrouter_app_name,
                "Content-Type": "application/json",
            },
            json=request_payload,
            timeout=45,
        )
        response.raise_for_status()
        provider_payload = response.json()
        content = self._extract_content(provider_payload)
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise OpenRouterJsonResponseError(
                f"OpenRouter response JSON parse failed: {exc.msg}",
                raw_response_excerpt=_excerpt(content),
            ) from exc
        if not isinstance(parsed, dict):
            raise OpenRouterJsonResponseError("OpenRouter response JSON is not an object", raw_response_excerpt=_excerpt(content))
        missing_keys = sorted(key for key in expected_keys if key not in parsed)
        if missing_keys:
            raise OpenRouterJsonResponseError(
                f"OpenRouter response missing keys: {', '.join(missing_keys)}",
                raw_response_excerpt=_excerpt(content),
            )
        return OpenRouterJsonResult(
            payload=parsed,
            raw_response={
                "id": provider_payload.get("id"),
                "model": provider_payload.get("model"),
                "usage": provider_payload.get("usage"),
            },
        )

    def _extract_content(self, payload: dict[str, Any]) -> str:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("OpenRouter response did not include choices")
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, str):
            return content
        raise ValueError("OpenRouter response did not include text content")


def _excerpt(value: str, limit: int = 1200) -> str:
    cleaned = " ".join(value.replace("\x00", " ").split())
    return cleaned[:limit]
