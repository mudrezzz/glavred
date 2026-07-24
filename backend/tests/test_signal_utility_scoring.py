from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.domain.ai_run import AiRun, AiRunCapability
from backend.app.settings import BackendSettings
from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfileRegistry
from backend.app.upstream.application.signal_review_lifecycle import SourceSignalReviewLifecyclePolicy
from backend.app.upstream.application.signal_utility_dossier import SignalUtilityDossierFactory
from backend.app.upstream.application.signal_utility_attempt_request import SignalUtilityAttemptRequestBuilder
from backend.app.upstream.application.signal_utility_profile import ProjectEditorialOpportunityProfileFactory
from backend.app.upstream.application.signal_utility_provider import SignalUtilityProviderResult
from backend.app.upstream.application.signal_utility_service import SignalUtilityScoringService
from backend.app.upstream.domain.signal_review import SourceSignalReviewCommand, SourceSignalReviewError
from backend.app.upstream.domain.signal_utility import (
    ProjectEditorialSetting,
    SignalUtilityDimension,
    SignalUtilityDimensionResult,
    SignalUtilityImportance,
    SignalUtilityStatus,
)
from backend.app.upstream.application.signal_utility_decision import SignalUtilityDecisionPolicy


class MemoryAiRunRepository:
    def __init__(self) -> None:
        self.runs: list[AiRun] = []

    def save(self, run: AiRun) -> AiRun:
        self.runs.append(run)
        return run

    def get(self, run_id: str) -> AiRun | None:
        return next((item for item in self.runs if item.id == run_id), None)

    def list(self, *, limit: int, capability: AiRunCapability | None = None) -> list[AiRun]:
        return [item for item in reversed(self.runs) if capability is None or item.capability == capability][:limit]


class RecordedUtilityProvider:
    def __init__(self, responses: list[dict[str, Any] | Exception]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def complete(self, **kwargs: Any) -> SignalUtilityProviderResult:
        self.calls.append(kwargs)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return SignalUtilityProviderResult(
            payload=response,
            usage={"prompt_tokens": 1100, "completion_tokens": 400, "total_tokens": 1500},
            request_id="utility-test-1",
            model=kwargs["model"],
        )


class EchoBatchUtilityProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def complete(self, **kwargs: Any) -> SignalUtilityProviderResult:
        self.calls.append(kwargs)
        provider_input = json.loads(kwargs["messages"][1]["content"])
        requirements = provider_input["evaluationContract"]["criteria"]
        evaluations = []
        for signal in provider_input["signals"]:
            evaluations.append({
                "signalKey": signal["key"],
                "criteria": [
                    {
                        "criterionKey": item["key"],
                        "status": "matched",
                        "summary": f"Настройка {item['settingId']} подтверждена.",
                        "reasonCodes": ["echo-batch-match"],
                        "evidenceKeys": [signal["evidenceRefs"][0]["key"]],
                    }
                    for item in requirements
                ],
            })
        return SignalUtilityProviderResult(
            payload={"signalEvaluations": evaluations},
            usage={"prompt_tokens": 1200, "completion_tokens": 500, "total_tokens": 1700},
            request_id=f"utility-batch-{len(self.calls)}",
            model=kwargs["model"],
        )


def test_arcelor_vendor_case_is_review_with_caution_not_false_topic_rejection() -> None:
    provider = RecordedUtilityProvider([utility_payload("matched")])
    repository = MemoryAiRunRepository()

    result = service(provider, repository).score(
        workspace=workspace(),
        radar=radar(),
        run={"id": "radar-run-arcelor"},
        signals=[arcelor_signal()],
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )

    utility = result["sourceSignals"][0]["utilityReport"]
    assert utility["recommendation"] == "reviewWithCaution"
    assert utility["blockingReasons"] == []
    radar_criteria = {item["criterionId"]: item for item in utility["radarCriteria"]}
    quality_checks = {item["checkId"]: item for item in utility["qualityChecks"]}
    assert radar_criteria["filter-industrial-context"]["verdict"] == "СОВПАДАЕТ"
    assert quality_checks["mechanism-support"]["classification"] == "reported"
    assert quality_checks["outcome-support"]["classification"] == "reported"
    assert quality_checks["source-posture"]["classification"] == "vendor"
    assert repository.runs[0].capability == AiRunCapability.SIGNAL_SCORING
    assert repository.runs[0].request_payload["payloadBudget"]["status"] == "directlyBudgeted"
    assert repository.runs[0].request_payload["messageCharCount"] <= 22000


def test_only_proven_blocking_conflict_produces_not_recommended() -> None:
    result = service(RecordedUtilityProvider([utility_payload("conflict")]), MemoryAiRunRepository()).score(
        workspace=workspace(), radar=radar(), run={"id": "run-conflict"}, signals=[arcelor_signal()],
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )
    assert result["sourceSignals"][0]["utilityReport"]["recommendation"] == "notRecommended"


def test_not_proven_blocking_filter_stays_reviewable() -> None:
    result = service(RecordedUtilityProvider([utility_payload("notProven")]), MemoryAiRunRepository()).score(
        workspace=workspace(), radar=radar(), run={"id": "run-unproven"}, signals=[arcelor_signal()],
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )
    utility = result["sourceSignals"][0]["utilityReport"]
    assert utility["recommendation"] == "reviewWithCaution"
    assert utility["blockingReasons"] == []


def test_invalid_primary_uses_structured_repair_and_keeps_direct_budget_proof() -> None:
    provider = RecordedUtilityProvider([{"signalEvaluations": []}, utility_payload("matched")])
    repository = MemoryAiRunRepository()
    result = service(provider, repository).score(
        workspace=workspace(), radar=radar(), run={"id": "run-repair"}, signals=[arcelor_signal()],
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )
    attempts = result["signalScoringReport"]["providerAttempts"]
    assert [item["status"] for item in attempts] == ["failed", "accepted"]
    assert len(repository.runs[1].request_payload["providerInput"]["repairContext"]) <= 1200
    assert all(item.request_payload["payloadBudget"]["status"] == "directlyBudgeted" for item in repository.runs)


def test_missing_active_filter_dimension_triggers_repair() -> None:
    incomplete = utility_payload("matched")
    incomplete["signalEvaluations"][0]["dimensions"] = incomplete["signalEvaluations"][0]["dimensions"][:1]
    provider = RecordedUtilityProvider([incomplete, utility_payload("matched")])

    result = service(provider, MemoryAiRunRepository()).score(
        workspace=workspace(), radar=radar(), run={"id": "run-filter-repair"}, signals=[arcelor_signal()],
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )

    attempts = result["signalScoringReport"]["providerAttempts"]
    assert [item["status"] for item in attempts] == ["failed", "accepted"]
    assert result["sourceSignals"][0]["utilityReport"]["recommendation"] == "reviewWithCaution"


def test_equivalent_signal_id_map_payload_is_accepted_without_text_parsing() -> None:
    payload = utility_payload("matched")
    evaluation = payload["signalEvaluations"][0]
    payload["signalEvaluations"] = {evaluation["signalId"]: {"dimensions": evaluation["dimensions"]}}

    result = service(RecordedUtilityProvider([payload]), MemoryAiRunRepository()).score(
        workspace=workspace(), radar=radar(), run={"id": "run-map-payload"}, signals=[arcelor_signal()],
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )

    assert result["signalScoringReport"]["status"] == "succeeded"


def test_more_than_one_batch_scores_every_signal_without_trimming_them_away() -> None:
    provider = EchoBatchUtilityProvider()
    signals = [{**arcelor_signal(), "id": f"signal-{index}"} for index in range(7)]

    result = service(provider, MemoryAiRunRepository()).score(
        workspace=workspace(), radar=radar(), run={"id": "run-two-batches"}, signals=signals,
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )

    assert len(provider.calls) == 2
    assert len(result["sourceSignals"]) == 7
    assert result["signalScoringReport"]["batchCount"] == 2
    assert result["signalScoringReport"]["decisionCoverageComplete"] is True
    assert {item["utilityReport"]["recommendation"] for item in result["sourceSignals"]} == {"reviewWithCaution"}


def test_provider_failure_is_terminal_inconclusive_without_changing_review_status() -> None:
    provider = RecordedUtilityProvider([RuntimeError("timeout"), RuntimeError("timeout"), RuntimeError("timeout")])
    result = service(provider, MemoryAiRunRepository()).score(
        workspace=workspace(), radar=radar(), run={"id": "run-failed"}, signals=[arcelor_signal()],
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )
    signal = result["sourceSignals"][0]
    assert signal["utilityReport"]["recommendation"] == "inconclusive"
    assert signal["reviewStatus"] == "candidate"


def test_dossier_is_bounded_and_forbids_full_workspace_fields() -> None:
    profile = ProjectEditorialOpportunityProfileFactory().build(
        workspace=workspace(), radar=radar(),
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )
    budget = UpstreamProviderBudgetProfileRegistry().resolve(operation_id="signalScoring", execution_mode="standard")
    signals = [{**arcelor_signal(), "id": f"signal-{index}"} for index in range(20)]
    dossier = SignalUtilityDossierFactory().build(profile=profile, signals=signals, budget=budget)
    text = str(dossier.provider_input)
    assert len(dossier.signal_ids) == 6
    assert all(name not in text for name in SignalUtilityDossierFactory.NEVER_SEND)
    assert dossier.readiness in {"READY", "DEGRADED"}
    assert len(str(dossier.provider_input)) < budget.max_provider_input_chars


def test_large_dossier_reserves_budget_for_structured_repair_context() -> None:
    source = workspace()
    source["editorialRules"] = [
        {
            "id": f"rule-{index}",
            "group": "positioning",
            "title": f"Правило {index}",
            "statement": "Промышленный контекст, механизм, ограничения и ответственность. " * 12,
            "status": "active",
        }
        for index in range(24)
    ]
    source["topics"] = [
        {
            "id": f"topic-{index}",
            "title": f"Тема {index}",
            "description": "Промышленная диагностика и производственные данные. " * 10,
            "purpose": "Практический критерий внедрения.",
            "audienceValue": "Проверяемая польза.",
            "authorStance": "Инженерная рамка.",
            "status": "active",
        }
        for index in range(12)
    ]
    profile = ProjectEditorialOpportunityProfileFactory().build(
        workspace=source, radar=radar(),
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )
    budget = UpstreamProviderBudgetProfileRegistry().resolve(operation_id="signalScoring", execution_mode="standard")
    dossier = SignalUtilityDossierFactory().build(
        profile=profile,
        signals=[{**arcelor_signal(), "id": f"signal-{index}"} for index in range(3)],
        budget=budget,
    )

    request = SignalUtilityAttemptRequestBuilder().build(
        dossier=dossier,
        profile=budget,
        label="repair",
        model="primary/model",
        repair_errors=["signalEvaluations-must-be-list", "missing-required-filter-dimension"],
    )

    assert dossier.readiness in {"READY", "DEGRADED"}
    assert request.blocked_reason is None
    assert request.fields["payloadBudget"]["status"] == "directlyBudgeted"
    assert request.fields["messageCharCount"] <= budget.max_message_chars
    system_prompt = request.messages[0]["content"]
    assert "summary не длиннее 120 символов" in system_prompt
    assert "evidenceKeys" in system_prompt


def test_confirmed_author_position_is_retained_in_project_profile() -> None:
    source = workspace()
    source["authorPositionAssertions"] = [{
        "id": "assertion-hitl",
        "status": "confirmed",
        "confidence": 0.6,
        "type": "position",
        "title": "Контроль человека",
        "statement": "Автоматизация должна оставлять проверяемое решение человеку.",
    }]

    profile = ProjectEditorialOpportunityProfileFactory().build(
        workspace=source,
        radar=radar(),
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )

    assert any(item.id == "assertion-hitl" for item in profile.settings)


def test_project_model_author_audience_goals_and_prohibitions_are_referenceable_settings() -> None:
    source = workspace()
    source["editorialModel"] = {
        "author": "Практик промышленного AI.",
        "audience": "Руководители цифровизации.",
        "positioning": "Инженерный разбор вместо новостей.",
        "goals": ["Давать применимые критерии."],
        "forbiddenTopics": ["Рекламный AI-шум без механизма."],
    }

    profile = ProjectEditorialOpportunityProfileFactory().build(
        workspace=source,
        radar=radar(),
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )

    ids = {item.id for item in profile.settings}
    assert {
        "project-model-author",
        "project-model-audience",
        "project-model-positioning",
        "project-model-goal-1",
        "project-model-forbidden-1",
    } <= ids
    forbidden = next(item for item in profile.settings if item.id == "project-model-forbidden-1")
    assert forbidden.mode == "mustNotMatch"


def test_recorded_golden_signal_utility_benchmark_covers_all_terminal_recommendations() -> None:
    strong = {**arcelor_signal(), "id": "signal-independent", "source": "Independent engineering report"}
    strong["evidence"][0]["sourceTitle"] = "Independent engineering report"
    strong["evidence"][0]["sourceUrl"] = "https://ieee.org/industrial-maintenance-report"
    strong["reasonCodes"] = ["source-independent", "outcome-observed"]
    scenarios = [
        (strong, utility_payload_for("signal-independent", "matched"), "recommended"),
        (arcelor_signal(), utility_payload("matched"), "reviewWithCaution"),
        (strong, utility_payload_for("signal-independent", "conflict"), "notRecommended"),
    ]
    recommendations = []
    for index, (signal, payload, expected) in enumerate(scenarios):
        result = service(RecordedUtilityProvider([payload]), MemoryAiRunRepository()).score(
            workspace=workspace(), radar=radar(), run={"id": f"golden-{index}"}, signals=[signal],
            project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
        )
        recommendation = result["sourceSignals"][0]["utilityReport"]["recommendation"]
        assert recommendation == expected
        recommendations.append(recommendation)
    failed = service(
        RecordedUtilityProvider([RuntimeError("offline"), RuntimeError("offline"), RuntimeError("offline")]),
        MemoryAiRunRepository(),
    ).score(
        workspace=workspace(), radar=radar(), run={"id": "golden-inconclusive"}, signals=[strong],
        project_context={"projectId": "project-ai-design-patterns", "editorialLanguage": "ru"},
    )
    recommendations.append(failed["sourceSignals"][0]["utilityReport"]["recommendation"])
    assert recommendations == ["recommended", "reviewWithCaution", "notRecommended", "inconclusive"]


def test_setting_mutation_changes_only_the_linked_utility_dimension() -> None:
    policy = SignalUtilityDecisionPolicy()
    settings = (
        ProjectEditorialSetting(
            id="filter-industrial-context",
            kind="radarFilter:topicAffinity",
            title="Промышленный контекст",
            statement="Сигнал относится к промышленной эксплуатации.",
            mode="mustMatch",
            dimension="topicAffinity",
            origin="radar",
        ),
    )
    common = utility_dimension(SignalUtilityDimension.AUTHOR_FIT, SignalUtilityStatus.MATCHED, "rule-industrial-position")
    matched = policy.evaluate(
        signal=arcelor_signal(),
        provider_dimensions=(common, utility_dimension(SignalUtilityDimension.TOPIC_AFFINITY, SignalUtilityStatus.MATCHED, "filter-industrial-context")),
        settings=settings,
    )
    conflict = policy.evaluate(
        signal=arcelor_signal(),
        provider_dimensions=(common, utility_dimension(SignalUtilityDimension.TOPIC_AFFINITY, SignalUtilityStatus.CONFLICT, "filter-industrial-context")),
        settings=settings,
    )
    matched_by_id = {item.dimension: item.status for item in matched.dimensions}
    conflict_by_id = {item.dimension: item.status for item in conflict.dimensions}
    changed = {key for key in matched_by_id if matched_by_id[key] != conflict_by_id[key]}

    assert changed == {SignalUtilityDimension.TOPIC_AFFINITY}
    assert matched.recommendation.value == "reviewWithCaution"
    assert conflict.recommendation.value == "notRecommended"


def test_review_lifecycle_is_revision_checked_reversible_and_evidence_immutable() -> None:
    policy = SourceSignalReviewLifecyclePolicy()
    signal = arcelor_signal()
    evidence_before = deepcopy(signal["evidence"])
    approved = policy.apply(signal, command("approve", 0)).signal
    reopened = policy.apply(approved, command("reopen", 1)).signal
    corrected = policy.apply(
        reopened,
        SourceSignalReviewCommand(
            action="correct",
            actor_id="user-founder",
            reason="Уточнить редакционную формулировку",
            expected_revision=2,
            editorial_patch={"title": "Русский заголовок", "summary": "Уточненная сводка", "mechanism": "tamper"},
        ),
    ).signal
    assert corrected["reviewStatus"] == "corrected"
    assert corrected["evidence"] == evidence_before
    assert corrected["mechanism"] == signal["mechanism"]
    assert [item["action"] for item in corrected["reviewHistory"]] == ["approve", "reopen", "correct"]
    try:
        policy.apply(corrected, command("approve", 2))
    except SourceSignalReviewError as exc:
        assert exc.code == "signal-review-revision-conflict"
    else:
        raise AssertionError("stale review revision must fail")


def service(provider: RecordedUtilityProvider, repository: MemoryAiRunRepository) -> SignalUtilityScoringService:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="test-key",
        UPSTREAM_SIGNAL_SCORING_MODEL="primary/model",
        OPENROUTER_BACKUP_MODEL="backup/model",
        DRAFT_RUN_EXECUTION_MODE="standard",
        AI_RUN_AUDIT_DB_PATH=Path("var/test-ai-runs.sqlite3"),
    )
    return SignalUtilityScoringService(settings=settings, provider=provider, ai_run_service=AiRunService(repository=repository))


def command(action: str, revision: int) -> SourceSignalReviewCommand:
    return SourceSignalReviewCommand(action=action, actor_id="user-founder", reason="", expected_revision=revision, editorial_patch={})


def utility_payload(topic_status: str) -> dict[str, Any]:
    signal = arcelor_signal()
    evidence = [{"materialId": "material-arcelor", "fragmentId": "fragment-arcelor"}]
    return {
        "signalEvaluations": [{
            "signalId": signal["id"],
            "dimensions": [
                {
                    "dimension": "topicAffinity", "status": topic_status,
                    "summary": "Кейс относится к промышленному обслуживанию оборудования.",
                    "reasonCodes": ["industrial-maintenance-context"],
                    "settingRefs": ["filter-industrial-context"], "evidenceRefs": evidence,
                },
                {
                    "dimension": "authorFit", "status": "matched",
                    "summary": "Есть workflow, результат и ограничение вместо общего AI-обещания.",
                    "reasonCodes": ["author-workflow-fit"],
                    "settingRefs": ["rule-industrial-position"], "evidenceRefs": evidence,
                },
                {
                    "dimension": "actionability", "status": "matched",
                    "summary": "Кейс дает проверяемую схему пилота и ограничение применимости.",
                    "reasonCodes": ["actionable-pilot"],
                    "settingRefs": ["filter-actionability"], "evidenceRefs": evidence,
                },
                {
                    "dimension": "topicAffinity", "status": topic_status,
                    "summary": "Тема проекта охватывает промышленную диагностику и ТОиР.",
                    "reasonCodes": ["project-topic-fit"],
                    "settingRefs": ["topic-industrial"], "evidenceRefs": evidence,
                },
            ],
        }]
    }


def utility_payload_for(signal_id: str, topic_status: str) -> dict[str, Any]:
    payload = utility_payload(topic_status)
    payload["signalEvaluations"][0]["signalId"] = signal_id
    return payload


def utility_dimension(
    dimension: SignalUtilityDimension,
    status: SignalUtilityStatus,
    setting_ref: str,
) -> SignalUtilityDimensionResult:
    return SignalUtilityDimensionResult(
        dimension=dimension,
        status=status,
        importance=SignalUtilityImportance.BLOCKING if dimension == SignalUtilityDimension.TOPIC_AFFINITY else SignalUtilityImportance.WEIGHTED,
        summary=f"Проверка {dimension.value}: {status.value}.",
        reason_codes=("recorded-setting-mutation",),
        setting_refs=(setting_ref,),
        evidence_refs=({"materialId": "material-arcelor", "fragmentId": "fragment-arcelor"},),
    )


def workspace() -> dict[str, Any]:
    return {
        "projectId": "project-ai-design-patterns",
        "projectProfile": {"name": "Сборочная", "description": "Промышленные AI-паттерны"},
        "editorialRules": [{
            "id": "rule-industrial-position", "group": "positioning", "title": "Инженерная рамка",
            "statement": "Показывать workflow, надежность, ограничения и ответственность.", "status": "active",
        }],
        "authorPositionAssertions": [],
        "topics": [{
            "id": "topic-industrial", "title": "Промышленные артефакты",
            "description": "ТОиР, EAM, диагностика и производственные данные.", "status": "active",
        }],
        "sourceSignals": [], "postCandidates": [], "contentPlanItems": [],
    }


def radar() -> dict[str, Any]:
    return {
        "id": "radar-industrial",
        "filters": [
            {"id": "filter-industrial-context", "dimension": "topics", "enabled": True, "mode": "mustMatch", "instruction": "Промышленный контекст обязателен."},
            {"id": "filter-actionability", "dimension": "actionability", "enabled": True, "mode": "shouldMatch", "instruction": "Нужна практическая применимость."},
        ],
    }


def arcelor_signal() -> dict[str, Any]:
    return {
        "id": "signal-arcelor", "type": "case", "title": "Пилот ArcelorMittal предотвратил простой",
        "summary": "За 12 месяцев система заранее обнаружила развивающиеся неисправности.",
        "source": "Samotics", "capturedAt": "2026-07-16", "reviewStatus": "candidate",
        "confidence": "high", "uncertainty": "Результат заявлен вендором и не подтвержден независимо.",
        "mechanism": "Мониторинг обнаруживал развивающиеся неисправности до простоя.",
        "outcome": "Предотвращен производственный простой.",
        "limitations": ["Один пилот; источник — вендор."],
        "reasonCodes": ["source-vendor"],
        "evidenceRefs": [{"materialId": "material-arcelor", "fragmentId": "fragment-arcelor", "quote": "The pilot prevented downtime."}],
        "evidence": [{"id": "evidence-arcelor", "materialId": "material-arcelor", "fragmentId": "fragment-arcelor", "sourceTitle": "Samotics ArcelorMittal case", "sourceUrl": "https://samotics.com/case", "quote": "The pilot prevented downtime.", "summary": "Кейс пилота"}],
        "editorialLanguage": "ru", "sourceLanguage": "en", "localizationStatus": "localized",
    }
