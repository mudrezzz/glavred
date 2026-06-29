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
        expected_keys = kwargs.get("expected_keys", set())
        if "commentComplianceStatus" in expected_keys:
            return JsonResult(
                payload={
                    "status": "passed",
                    "commentComplianceStatus": "passed",
                    "sourceIntegrityStatus": "passed",
                    "publicProseStatus": "passed",
                    "internalJargonLeaks": [],
                    "regressionWarnings": [],
                    "matchedCommentIntents": ["author stance"],
                    "missedCommentIntents": [],
                    "summary": "The revised draft follows the editor comment.",
                },
                raw_response={"id": "quality-provider-id", "model": kwargs.get("model")},
            )
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
    assert payload["qualityCheck"]["status"] == "passed"
    assert payload["qualityCheck"]["matchedCommentIntents"] == ["author stance"]
    assert payload["aiRunId"]
    assert payload["attempts"][0]["modelRole"] == "writer"
    assert adapter.calls[0]["model"] == "writer-model"
    assert adapter.calls[1]["model"] == "default-model"
    ai_run = client.get(f"/api/ai-runs/{payload['aiRunId']}").json()
    assert ai_run["requestPayload"]["draftRunStep"] == "humanCommentRevision"
    assert ai_run["requestPayload"]["editorComment"] == "Make the author stance sharper."
    assert "secret-token" not in response.text


def test_revise_with_comment_returns_revision_when_quality_check_fails(tmp_path) -> None:
    class QualityFailingAdapter(SuccessfulJsonAdapter):
        def complete_json(self, **kwargs: Any) -> JsonResult:
            expected_keys = kwargs.get("expected_keys", set())
            if "commentComplianceStatus" in expected_keys:
                self.calls.append(kwargs)
                raise ValueError("not json")
            return super().complete_json(**kwargs)

    adapter = QualityFailingAdapter()
    client = TestClient(
        create_app(
            settings=BackendSettings(
                _env_file=None,
                OPENROUTER_API_KEY="secret-token",
                OPENROUTER_DEFAULT_MODEL="default-model",
                OPENROUTER_BACKUP_MODEL="backup-model",
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
            "currentVersion": {
                "id": "draft-1-v1",
                "versionNumber": 1,
                "title": "Current title",
                "body": "Current body",
            },
            "editorComment": "Improve it.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["body"] == "Human revised body"
    assert payload["qualityCheck"]["status"] == "notRun"
    assert [attempt["label"] for attempt in payload["qualityCheck"]["attempts"]] == [
        "primary",
        "primary-repair",
        "backup",
    ]
    assert payload["qualityCheck"]["attempts"][0]["modelRole"] == "review"


def test_quality_check_marks_internal_jargon_and_lost_source_marker(tmp_path) -> None:
    class LeakyRevisionAdapter(SuccessfulJsonAdapter):
        def complete_json(self, **kwargs: Any) -> JsonResult:
            self.calls.append(kwargs)
            expected_keys = kwargs.get("expected_keys", set())
            if "commentComplianceStatus" in expected_keys:
                return JsonResult(
                    payload={
                        "status": "passed",
                        "commentComplianceStatus": "passed",
                        "sourceIntegrityStatus": "passed",
                        "publicProseStatus": "passed",
                        "internalJargonLeaks": [],
                        "regressionWarnings": [],
                        "matchedCommentIntents": ["shorter"],
                        "missedCommentIntents": [],
                        "summary": "Looks good.",
                    },
                    raw_response={"id": "quality-provider-id", "model": kwargs.get("model")},
                )
            return JsonResult(
                payload={
                    "title": "Leaky revised title",
                    "body": "This public post explains SourceLedger but omits the original source marker.",
                    "revisionSummary": "Applied editor comment.",
                },
                raw_response={"id": "human-revision-provider-id", "model": kwargs.get("model")},
            )

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
            openrouter_json_adapter=LeakyRevisionAdapter(),
        )
    )

    response = client.post(
        "/api/drafts/revise-with-comment",
        json={
            "currentVersion": {
                "id": "draft-1-v1",
                "versionNumber": 1,
                "title": "Current title",
                "body": "Current body cites B2BNotes and WebProNews.",
            },
            "editorComment": "Make it shorter.",
        },
    )

    assert response.status_code == 200
    quality = response.json()["qualityCheck"]
    assert quality["status"] == "warning"
    assert quality["publicProseStatus"] == "warning"
    assert quality["sourceIntegrityStatus"] == "warning"
    assert "SourceLedger" in quality["internalJargonLeaks"]
    assert any("B2BNotes" in warning for warning in quality["regressionWarnings"])


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
