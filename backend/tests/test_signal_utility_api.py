from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.settings import BackendSettings
from backend.app.upstream.application.signal_utility_provider import SignalUtilityProviderResult
from backend.tests.portfolio_test_helpers import login_portfolio


class ApiSignalUtilityProvider:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, **kwargs: Any) -> SignalUtilityProviderResult:
        self.calls += 1
        provider_input = json.loads(kwargs["messages"][1]["content"])
        requirements = provider_input["evaluationContract"]["criteria"]
        return SignalUtilityProviderResult(
            payload={
                "signalEvaluations": [
                    {
                        "signalKey": signal["key"],
                        "criteria": [
                            {
                                "criterionKey": requirement["key"],
                                "status": "matched",
                                "summary": "Промышленный кейс соответствует активной настройке.",
                                "reasonCodes": ["industrial-context-matched"],
                                "evidenceKeys": [signal["evidenceRefs"][0]["key"]],
                                "uncertainty": "Источник является кейсом поставщика.",
                            }
                            for requirement in requirements
                        ],
                    }
                    for signal in provider_input["signals"]
                ],
            },
            usage={"prompt_tokens": 510, "completion_tokens": 140, "total_tokens": 650},
            request_id=f"utility-http-{self.calls}",
            model=kwargs["model"],
        )


def test_manual_scoring_and_review_are_persisted_without_mutating_evidence(tmp_path: Path) -> None:
    client = utility_client(tmp_path)
    login_portfolio(client, "founder@example.test")
    provider = ApiSignalUtilityProvider()
    client.app.state.signal_utility_provider = provider
    workspace = utility_workspace()
    save = client.put(
        "/api/projects/project-ai-design-patterns/workspace",
        json={"workspace": workspace},
    )
    assert save.status_code == 200

    scoring = client.post(
        "/api/projects/project-ai-design-patterns/radar-runs/run-utility-api/signal-scoring",
    )

    assert scoring.status_code == 200
    scored = scoring.json()["sourceSignals"][0]
    assert scoring.json()["signalScoringReport"]["status"] == "succeeded"
    assert scored["utilityReport"]["recommendation"] in {"recommended", "reviewWithCaution"}
    assert provider.calls == 1
    evidence_before = deepcopy(scored["evidence"])

    approved = client.post(
        "/api/projects/project-ai-design-patterns/source-signals/signal-utility-api/review",
        json={"action": "approve", "reason": "", "expectedReviewRevision": 0},
    )

    assert approved.status_code == 200
    reviewed = approved.json()["sourceSignal"]
    assert reviewed["reviewStatus"] == "approved"
    assert reviewed["reviewRevision"] == 1
    assert reviewed["reviewHistory"][0]["actorId"] == "user-founder-editor"
    assert reviewed["evidence"] == evidence_before

    stale = client.post(
        "/api/projects/project-ai-design-patterns/source-signals/signal-utility-api/review",
        json={"action": "reopen", "reason": "", "expectedReviewRevision": 0},
    )
    assert stale.status_code == 409
    assert stale.json()["detail"] == "signal-review-revision-conflict"

    persisted = client.get("/api/projects/project-ai-design-patterns/workspace").json()["workspace"]
    persisted_signal = persisted["sourceSignals"][0]
    assert persisted_signal["reviewStatus"] == "approved"
    assert persisted_signal["evidence"] == evidence_before
    assert len(persisted["radarRuns"][0]["operations"]) == 1


def test_review_reason_is_required_for_rejection(tmp_path: Path) -> None:
    client = utility_client(tmp_path)
    login_portfolio(client, "founder@example.test")
    assert client.put(
        "/api/projects/project-ai-design-patterns/workspace",
        json={"workspace": utility_workspace()},
    ).status_code == 200

    response = client.post(
        "/api/projects/project-ai-design-patterns/source-signals/signal-utility-api/review",
        json={"action": "reject", "reason": "", "expectedReviewRevision": 0},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "signal-review-reason-required"


def test_correction_rescores_the_complete_run_without_dropping_other_signal_evaluations(tmp_path: Path) -> None:
    client = utility_client(tmp_path)
    login_portfolio(client, "founder@example.test")
    provider = ApiSignalUtilityProvider()
    client.app.state.signal_utility_provider = provider
    workspace = utility_workspace()
    second = deepcopy(workspace["sourceSignals"][0])
    second["id"] = "signal-utility-api-second"
    second["evidence"][0]["id"] = "evidence-utility-api-second"
    workspace["sourceSignals"].append(second)
    assert client.put(
        "/api/projects/project-ai-design-patterns/workspace",
        json={"workspace": workspace},
    ).status_code == 200
    assert client.post(
        "/api/projects/project-ai-design-patterns/radar-runs/run-utility-api/signal-scoring",
    ).status_code == 200

    corrected = client.post(
        "/api/projects/project-ai-design-patterns/source-signals/signal-utility-api/review",
        json={
            "action": "correct",
            "reason": "Уточнить редакционную формулировку",
            "editorialPatch": {"title": "Уточненный русский заголовок", "summary": "Уточненная сводка", "authorCorrection": "Причина"},
            "expectedReviewRevision": 0,
        },
    )

    assert corrected.status_code == 200
    persisted = client.get("/api/projects/project-ai-design-patterns/workspace").json()["workspace"]
    report = persisted["radarRuns"][0]["signalScoring"]
    assert report["signalIds"] == ["signal-utility-api", "signal-utility-api-second"]
    assert len(report["evaluations"]) == 2
    assert next(item for item in persisted["sourceSignals"] if item["id"] == "signal-utility-api")["reviewHistory"][0]["action"] == "correct"


def utility_client(tmp_path: Path) -> TestClient:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="test-token",
        OPENROUTER_DEFAULT_MODEL="test-model",
        PORTFOLIO_DB_PATH=tmp_path / "portfolio.sqlite3",
        AI_RUN_AUDIT_DB_PATH=tmp_path / "ai-runs.sqlite3",
        GLAVRED_DEV_AUTH_PASSWORD="secret-demo",
    )
    return TestClient(create_app(settings=settings))


def utility_workspace() -> dict[str, Any]:
    evidence = [{
        "id": "evidence-utility-api",
        "materialId": "material-utility-api",
        "fragmentId": "fragment-utility-api",
        "sourceTitle": "Industrial maintenance case",
        "sourceUrl": "https://example.com/industrial-case",
        "quote": "The pilot detected developing faults before downtime.",
        "summary": "Промышленный пилот с наблюдаемым результатом.",
    }]
    signal = {
        "id": "signal-utility-api",
        "radarId": "radar-utility-api",
        "radarRunId": "run-utility-api",
        "type": "case",
        "title": "Пилот обнаружил неисправности до простоя",
        "summary": "Система выявляла развивающиеся неисправности заранее.",
        "source": "Industrial case",
        "capturedAt": "2026-07-17",
        "reviewStatus": "candidate",
        "confidence": "high",
        "uncertainty": "Доступен только один источник.",
        "mechanism": "Мониторинг выявляет отклонения до отказа.",
        "outcome": "Команда успевает вмешаться до простоя.",
        "limitations": ["Один пилот."],
        "editorialLanguage": "ru",
        "sourceLanguage": "en",
        "localizationStatus": "localized",
        "evidence": evidence,
        "evidenceRefs": [{
            "materialId": "material-utility-api",
            "fragmentId": "fragment-utility-api",
            "quote": evidence[0]["quote"],
        }],
    }
    return {
        "projectId": "project-ai-design-patterns",
        "projectProfile": {"name": "Сборочная", "description": "Промышленные AI-системы."},
        "radars": [{
            "id": "radar-utility-api",
            "title": "Промышленные AI-кейсы",
            "filters": [{
                "id": "filter-industrial-context",
                "dimension": "topics",
                "enabled": True,
                "mode": "mustMatch",
                "instruction": "Нужен промышленный контекст.",
            }],
        }],
        "radarRuns": [{
            "id": "run-utility-api",
            "radarId": "radar-utility-api",
            "operations": [],
            "budget": {"usedOperations": 0},
        }],
        "sourceSignals": [signal],
        "foundMaterials": [],
        "editorialRules": [],
        "authorPositionAssertions": [],
        "topics": [],
        "postCandidates": [],
        "contentPlanItems": [],
    }
