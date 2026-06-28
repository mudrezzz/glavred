from typing import Any

import pytest

from backend.app.infrastructure.openrouter_json_adapter import OpenRouterJsonAdapter, OpenRouterJsonResponseError
from backend.app.settings import BackendSettings


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


def settings() -> BackendSettings:
    return BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="sk-test",
        OPENROUTER_DEFAULT_MODEL="default-model",
    )


def test_openrouter_json_adapter_sends_top_p(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_post(*args: Any, **kwargs: Any) -> FakeResponse:
        captured.update(kwargs["json"])
        return FakeResponse({"choices": [{"message": {"content": '{"title":"ok"}'}}]})

    monkeypatch.setattr("backend.app.infrastructure.openrouter_json_adapter.httpx.post", fake_post)

    result = OpenRouterJsonAdapter().complete_json(
        settings=settings(),
        messages=[{"role": "user", "content": "return json"}],
        expected_keys={"title"},
        temperature=0.65,
        top_p=0.9,
        model="writer-model",
    )

    assert result.payload == {"title": "ok"}
    assert captured["temperature"] == 0.65
    assert captured["top_p"] == 0.9


def test_openrouter_json_adapter_parse_error_carries_raw_excerpt(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*args: Any, **kwargs: Any) -> FakeResponse:
        return FakeResponse({"choices": [{"message": {"content": "```json\\nnot json\\n```"}}]})

    monkeypatch.setattr("backend.app.infrastructure.openrouter_json_adapter.httpx.post", fake_post)

    with pytest.raises(OpenRouterJsonResponseError) as error:
        OpenRouterJsonAdapter().complete_json(
            settings=settings(),
            messages=[{"role": "user", "content": "return json"}],
            expected_keys={"title"},
            temperature=0.15,
            model="writer-model",
        )

    assert "parse failed" in str(error.value)
    assert error.value.raw_response_excerpt == "```json\\nnot json\\n```"
