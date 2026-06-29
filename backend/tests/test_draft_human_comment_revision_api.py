from dataclasses import dataclass
from typing import Any

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.settings import BackendSettings


@dataclass
class JsonResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class SuccessfulJsonAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> JsonResult:
        self.calls.append(kwargs)
        return JsonResult(
            payload={
                "title": "Human revised title",
                "body": "Human revised body",
                "revisionSummary": "Applied editor comment.",
            },
            raw_response={"id": "human-revision-provider-id", "model": kwargs.get("model")},
        )


def test_revise_with_comment_creates_child_ai_run(tmp_path) -> None:
    adapter = SuccessfulJsonAdapter()
    client = TestClient(
        create_app(
            settings=BackendSettings(
                _env_file=None,
                OPENROUTER_API_KEY="secret-token",
                OPENROUTER_DEFAULT_MODEL="default-model",
                DRAFT_WRITER_MODEL="writer-model",
                AI_RUN_AUDIT_DB_PATH=str(tmp_path / "audit.sqlite3"),
                DRAFT_RUN_DB_PATH=str(tmp_path / "draft-runs.sqlite3"),
            ),
            openrouter_json_adapter=adapter,
        )
    )

    response = client.post(
        "/api/drafts/revise-with-comment",
        json={
            "draftRunId": None,
            "currentVersion": {
                "id": "draft-1-v1",
                "versionNumber": 1,
                "title": "Current title",
                "body": "Current body",
            },
            "editorComment": "Make the author stance sharper.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["body"] == "Human revised body"
    assert payload["revisionSummary"] == "Applied editor comment."
    assert payload["aiRunId"]
    assert payload["attempts"][0]["modelRole"] == "writer"
    assert adapter.calls[0]["model"] == "writer-model"
    ai_run = client.get(f"/api/ai-runs/{payload['aiRunId']}").json()
    assert ai_run["requestPayload"]["draftRunStep"] == "humanCommentRevision"
    assert ai_run["requestPayload"]["editorComment"] == "Make the author stance sharper."
    assert "secret-token" not in response.text


def test_revise_with_comment_returns_503_when_provider_unconfigured(tmp_path) -> None:
    client = TestClient(
        create_app(
            settings=BackendSettings(
                _env_file=None,
                OPENROUTER_API_KEY="",
                OPENROUTER_DEFAULT_MODEL="",
                AI_RUN_AUDIT_DB_PATH=str(tmp_path / "audit.sqlite3"),
                DRAFT_RUN_DB_PATH=str(tmp_path / "draft-runs.sqlite3"),
            )
        )
    )

    response = client.post(
        "/api/drafts/revise-with-comment",
        json={
            "currentVersion": {
                "id": "draft-1-v1",
                "versionNumber": 1,
                "title": "Current title",
                "body": "Current body",
            },
            "editorComment": "Improve it.",
        },
    )

    assert response.status_code == 503
    assert "OpenRouter is not configured" in response.text
