import json
from dataclasses import dataclass
from typing import Any

import httpx

from backend.app.settings import BackendSettings


@dataclass(frozen=True)
class OpenRouterJsonResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class OpenRouterJsonAdapter:
    def complete_json(
        self,
        *,
        settings: BackendSettings,
        messages: list[dict[str, str]],
        expected_keys: set[str],
        temperature: float,
        model: str | None = None,
    ) -> OpenRouterJsonResult:
        api_key = settings.openrouter_api_key.get_secret_value() if settings.openrouter_api_key else ""
        selected_model = model or settings.openrouter_default_model
        response = httpx.post(
            f"{settings.openrouter_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": settings.openrouter_http_referer,
                "X-OpenRouter-Title": settings.openrouter_app_name,
                "Content-Type": "application/json",
            },
            json={
                "model": selected_model,
                "messages": messages,
                "temperature": temperature,
                "response_format": {"type": "json_object"},
            },
            timeout=45,
        )
        response.raise_for_status()
        provider_payload = response.json()
        parsed = json.loads(self._extract_content(provider_payload))
        if not isinstance(parsed, dict):
            raise ValueError("OpenRouter response JSON is not an object")
        missing_keys = sorted(key for key in expected_keys if key not in parsed)
        if missing_keys:
            raise ValueError(f"OpenRouter response missing keys: {', '.join(missing_keys)}")
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
