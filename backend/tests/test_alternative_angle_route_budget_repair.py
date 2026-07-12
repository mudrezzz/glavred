from __future__ import annotations

import json
from dataclasses import replace

import pytest

from backend.app.drafting.application.dossiers.provider_dossier_factories import AlternativeAngleDossierFactory
from backend.app.drafting.application.operations.payload_budget import DraftRunPayloadBudgetPolicy
from backend.app.drafting.application.operations.provider_message_budget_guard import ProviderMessageBudgetGuard
from backend.app.drafting.application.validation.draft_alternative_angle_dossier_attempt import AlternativeAngleDossierAttemptBuilder
from backend.tests.provider_dossier_test_support import ProviderDossierTestFixture


def test_live_sized_route_dossier_is_bounded_and_candidate_projection_is_symmetric() -> None:
    payload = _stress_payload()

    result = DraftRunPayloadBudgetPolicy().compact(
        "alternativeAngleRoute",
        payload,
        execution_mode="standard",
        model="route-model",
        model_role="anotherAngle",
    )

    assert len(json.dumps(payload, ensure_ascii=False, sort_keys=True)) > 34_000
    assert result.payload_budget["promptCharEstimate"] <= 18_500
    assert result.incident is None
    assert result.trimmed_counts["candidatesChars"] > 0
    candidates = result.compact_payload["candidates"]
    assert len(candidates) == 3
    assert len({tuple(candidate) for candidate in candidates}) == 1
    assert all(len(json.dumps(candidate, ensure_ascii=False, sort_keys=True)) <= 1_800 for candidate in candidates)
    assert all(candidate["id"] and candidate["title"] and candidate["idea"] and candidate["opening"] for candidate in candidates)
    assert {"postContract", "critiqueSignals", "validationIssues", "rejectedMoves", "evidence", "rules"} <= set(result.compact_payload)


def test_route_compactor_prioritizes_critical_issue_for_each_candidate() -> None:
    payload = _stress_payload()
    payload["validationIssues"] = [
        _issue("candidate-1", "observation", "observation"),
        _issue("candidate-1", "critical", "critical"),
        _issue("candidate-2", "warning", "warning"),
        _issue("candidate-3", "warning", "warning"),
    ]

    result = DraftRunPayloadBudgetPolicy().compact("alternativeAngleRoute", payload, execution_mode="standard")

    selected = {item["candidateId"]: item for item in result.compact_payload["validationIssues"]}
    assert selected["candidate-1"]["severity"] == "critical"
    assert "critical" in selected["candidate-1"]["message"]


def test_attempt_budget_includes_bounded_repair_context_and_actual_messages() -> None:
    base = AlternativeAngleDossierFactory(ProviderDossierTestFixture.access()).build()
    dossier = replace(base, sent={key: value for key, value in _stress_payload().items() if key != "dossierId"})
    repair_context = {
        "previousAttempt": {
            "label": "repair",
            "status": "error",
            "validation": "ошибка " * 2_000,
            "rawResponse": "must-not-be-sent" * 2_000,
        },
        "requiredShape": "object with one alternative route",
    }

    prepared = AlternativeAngleDossierAttemptBuilder().prepare(
        dossier=dossier,
        model="route-model",
        model_role="anotherAngle",
        attempt={"label": "repair", "repair": True, "backup": False},
        model_selection={"modelRole": "anotherAngle", "selectedModel": "route-model"},
        generation_params={"temperature": 0.45},
        execution_mode="standard",
        repair_context=repair_context,
    )

    request = prepared.request_payload
    user_payload = json.loads(prepared.messages[1]["content"])
    assert prepared.blocked_reason is None
    assert request["payloadBudget"]["promptCharEstimate"] == request["messageCharCount"]
    assert request["messageCharCount"] <= 22_000
    assert request["payloadBudget"]["providerInputCharEstimate"] <= 20_000
    assert request["repairContextCharCount"] <= 1_500
    assert "repairContext" not in request["providerInput"]
    assert user_payload["repairContext"]["previousAttempt"]["validation"]
    assert "rawResponse" not in user_payload["repairContext"]["previousAttempt"]
    assert request["payloadBudget"].get("incident") is None


@pytest.mark.parametrize(("message_chars", "blocked"), [(21_999, False), (22_000, False), (22_001, True)])
def test_message_budget_guard_enforces_serialized_boundary(message_chars: int, blocked: bool) -> None:
    messages = _messages_with_serialized_size(message_chars)
    result = ProviderMessageBudgetGuard().evaluate(
        messages=messages,
        request_fields={
            "payloadBudget": {"promptCharEstimate": 18_500, "limits": {"maxPromptChars": 22_000}},
            "inputStats": {},
            "payloadStats": {},
        },
        repair_context_char_count=0,
    )

    assert result.request_fields["messageCharCount"] == message_chars
    assert bool(result.blocked_reason) is blocked
    if blocked:
        assert result.request_fields["payloadBudget"]["incident"]["incidentType"] == "contextOverBudget"


def _stress_payload() -> dict:
    candidates = []
    critiques = []
    issues = []
    for index in range(1, 4):
        candidate_id = f"candidate-{index}"
        candidates.append(
            {
                "id": candidate_id,
                "title": f"Route candidate {index}",
                "rhetoricalPlanId": f"plan-{index}",
                "bodyExcerpt": "Промышленный сценарий и решение. " * 80,
                "bodyWindows": {"opening": "Начало. " * 220, "middle": "Аргумент. " * 220, "ending": "Вывод. " * 220},
                "usedEvidence": [{"id": f"evidence-{item}", "full": "данные " * 80} for item in range(12)],
                "ruleCoverage": [{"id": f"rule-{item}", "full": "правило " * 80} for item in range(12)],
                "risks": ["Риск применимости. " * 40],
                "weaknesses": ["Слабая сторона. " * 40],
            }
        )
        critiques.append(
            {
                "candidateId": candidate_id,
                "status": "warning",
                "editorialRisk": "medium",
                "weakestMove": "Слабый редакционный ход. " * 50,
                "recommendedEditorialMove": "Изменить рамку и начало. " * 50,
                "findings": [{"severity": "warning", "validatorId": "critic.structure", "message": "Замечание. " * 50}],
            }
        )
        issues.append(_issue(candidate_id, "warning", "Нужно исправить аргумент. " * 30))
    return {
        "dossierId": "alternative-angle-route-v1",
        "candidates": candidates,
        "critiqueSignals": critiques,
        "validationIssues": issues,
        "rejectedMoves": [
            {"candidateId": "candidate-1", "severity": "warning", "validatorId": "critic.source", "message": "Не повторять. " * 40, "repairGuidance": "Сменить ход. " * 40},
            {"candidateId": "candidate-2", "severity": "warning", "validatorId": "critic.tone", "message": "Не повторять. " * 40, "repairGuidance": "Сменить ход. " * 40},
        ],
        "postContract": {
            "title": "Decision workbench",
            "thesis": "Тезис и границы решения. " * 40,
            "audience": "Руководители цифровизации. " * 30,
            "cta": "Проверить собственный процесс. " * 20,
            "platform": "Telegram",
            "claims": [{"id": f"claim-{item}", "statement": "Утверждение. " * 30} for item in range(8)],
            "forbiddenMoves": ["Запрещенный ход. " * 25 for _ in range(8)],
            "evidenceObligations": ["Доказательное обязательство. " * 25 for _ in range(8)],
            "fabulaObligations": ["Сюжетное обязательство. " * 25 for _ in range(8)],
        },
        "evidence": [{"id": f"evidence-{item}", "statement": "Факт. " * 50, "allowedUse": "canState", "confidence": "medium"} for item in range(2)],
        "rules": [{"id": f"rule-{item}", "severity": "hard", "category": "contract", "statement": "Ограничение. " * 50} for item in range(2)],
    }


def _issue(candidate_id: str, severity: str, message: str) -> dict:
    return {
        "candidateId": candidate_id,
        "severity": severity,
        "validatorId": f"validator.{severity}",
        "source": "deterministic",
        "message": message,
        "repairGuidance": "Исправить без потери доказательности. " * 20,
        "ruleIds": ["rule-1"],
    }


def _messages_with_serialized_size(target: int) -> list[dict[str, str]]:
    empty = [{"role": "user", "content": ""}]
    overhead = len(json.dumps(empty, ensure_ascii=False, sort_keys=True))
    messages = [{"role": "user", "content": "x" * (target - overhead)}]
    assert len(json.dumps(messages, ensure_ascii=False, sort_keys=True)) == target
    return messages
