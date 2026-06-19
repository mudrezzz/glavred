from dataclasses import dataclass, field
from typing import Any

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.settings import BackendSettings


def make_payload() -> dict[str, Any]:
    return {
        "brief": {
            "id": "brief-demo",
            "title": "AI-B2B demo еще не продукт",
            "rubric": "AI product discovery",
            "audience": "AI PM",
            "thesis": "Demo magic не равно adoption.",
            "conflict": "Demo красиво, rollout слабый.",
            "authorPosition": "Сначала workflow, потом модель.",
            "evidence": ["usage после пилота не растет"],
            "examples": ["нет evals"],
            "structure": ["конфликт", "позиция"],
            "cta": "Проверьте продуктовую петлю.",
            "risks": ["не звучать против прототипов"],
            "sources": ["author note"],
        },
        "editorialModel": {
            "audience": "AI Product Manager",
            "styleRules": ["исследовательский тон"],
            "forbiddenTopics": ["generic AI hype"],
            "goals": ["объяснить adoption gap"],
        },
    }


@dataclass
class RecordingDispatcher:
    calls: list[str] = field(default_factory=list)

    def dispatch(self, run_id: str) -> None:
        self.calls.append(run_id)


@dataclass
class FailingDispatcher:
    def dispatch(self, run_id: str) -> None:
        raise RuntimeError("redis unavailable")


def make_client(tmp_path, dispatcher: object) -> TestClient:
    return TestClient(
        create_app(
            settings=BackendSettings(
                _env_file=None,
                DRAFT_RUN_DB_PATH=str(tmp_path / "draft-runs.sqlite3"),
            ),
            draft_run_dispatcher=dispatcher,
        )
    )


def test_create_draft_run_returns_queued_and_dispatches(tmp_path) -> None:
    dispatcher = RecordingDispatcher()
    client = make_client(tmp_path, dispatcher)

    response = client.post("/api/draft-runs", json=make_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "queued"
    assert dispatcher.calls == [payload["runId"]]


def test_get_draft_run_returns_steps_and_hides_paths(tmp_path) -> None:
    dispatcher = RecordingDispatcher()
    client = make_client(tmp_path, dispatcher)
    created = client.post("/api/draft-runs", json=make_payload()).json()

    response = client.get(f"/api/draft-runs/{created['runId']}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == created["runId"]
    assert payload["inputSummary"]["title"] == "AI-B2B demo еще не продукт"
    assert [step["key"] for step in payload["steps"]][0] == "context"
    assert str(tmp_path) not in response.text


def test_get_draft_run_missing_returns_404(tmp_path) -> None:
    client = make_client(tmp_path, RecordingDispatcher())

    response = client.get("/api/draft-runs/missing")

    assert response.status_code == 404


def test_dispatch_failure_marks_run_failed(tmp_path) -> None:
    client = make_client(tmp_path, FailingDispatcher())

    response = client.post("/api/draft-runs", json=make_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "failed"
    loaded = client.get(f"/api/draft-runs/{payload['runId']}").json()
    assert loaded["error"] == "redis unavailable"
