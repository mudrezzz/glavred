"""Owner: infrastructure

Used by: radar-run API composition as the OpenRouter signal-extraction transport.
Does not own: extraction policy, retries, budgets, grounding, or AiRun persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from backend.app.infrastructure.openrouter_json_adapter import OpenRouterJsonAdapter
from backend.app.settings import BackendSettings
from backend.app.upstream.application.signal_extraction_provider import SignalExtractionProviderResult


class OpenRouterSignalExtractionAdapter:
    def __init__(self, *, settings: BackendSettings, json_adapter: OpenRouterJsonAdapter | None = None) -> None:
        self._settings = settings
        self._json = json_adapter or OpenRouterJsonAdapter()

    def complete(
        self,
        *,
        messages: list[dict[str, str]],
        model: str,
        max_output_tokens: int,
    ) -> SignalExtractionProviderResult:
        result = self._json.complete_json(
            settings=self._settings,
            messages=messages,
            expected_keys={"signals", "materialDecisions"},
            temperature=0.15,
            top_p=0.85,
            model=model,
            max_tokens=max_output_tokens,
        )
        raw = result.raw_response
        return SignalExtractionProviderResult(
            payload=result.payload,
            usage=raw.get("usage") if isinstance(raw.get("usage"), dict) else None,
            request_id=str(raw.get("id")) if raw.get("id") else None,
            model=str(raw.get("model")) if raw.get("model") else model,
        )


__all__ = ("OpenRouterSignalExtractionAdapter",)
