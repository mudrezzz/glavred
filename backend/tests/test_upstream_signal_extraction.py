from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from pydantic import SecretStr

from backend.app.application.ai_run_service import AiRunService
from backend.app.domain.ai_run import AiRun, AiRunCapability
from backend.app.settings import BackendSettings
from backend.app.upstream.application.provider_budget_profiles import UpstreamProviderBudgetProfileRegistry
from backend.app.upstream.application.benchmark.signal_extraction_runner import run_signal_extraction_golden_benchmark
from backend.app.upstream.application.signal_extraction_context import (
    SignalExtractionContextFactory,
    SignalExtractionDossierFactory,
)
from backend.app.upstream.application.signal_extraction_fragments import FoundMaterialFragmentPolicy
from backend.app.upstream.application.signal_extraction_provider import SignalExtractionProviderResult
from backend.app.upstream.application.signal_extraction_service import SignalExtractionService


class MemoryAiRunRepository:
    def __init__(self) -> None:
        self.runs: list[AiRun] = []

    def save(self, run: AiRun) -> AiRun:
        self.runs.append(run)
        return run

    def get(self, run_id: str) -> AiRun | None:
        return next((run for run in self.runs if run.id == run_id), None)

    def list(self, *, limit: int, capability: AiRunCapability | None = None) -> list[AiRun]:
        runs = self.runs if capability is None else [run for run in self.runs if run.capability == capability]
        return list(reversed(runs))[:limit]


class RecordedExtractionProvider:
    def __init__(self, responses: list[dict[str, Any] | Exception]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def complete(self, *, messages: list[dict[str, str]], model: str, max_output_tokens: int) -> SignalExtractionProviderResult:
        self.calls.append({"messages": messages, "model": model, "maxOutputTokens": max_output_tokens})
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return SignalExtractionProviderResult(
            payload=response,
            usage={"prompt_tokens": 900, "completion_tokens": 280, "total_tokens": 1180},
            request_id="recorded-extraction-1",
            model=model,
        )


def test_fragment_policy_creates_stable_bounded_hashes_and_offsets() -> None:
    policy = FoundMaterialFragmentPolicy()
    text = "Первый факт о внедрении. Второй факт описывает ограничение. " * 80

    first = policy.from_read_text(material_id="material-1", text=text)
    second = policy.from_read_text(material_id="material-1", text=text)

    assert first == second
    assert 1 <= len(first) <= policy.MAX_FRAGMENTS
    assert all(len(item["text"]) <= policy.MAX_FRAGMENT_CHARS for item in first)
    assert all(item["startChar"] < item["endChar"] for item in first)
    assert all(len(item["hash"]) == 64 for item in first)


def test_valid_primary_creates_grounded_candidate_and_terminal_decisions() -> None:
    material = readable_material()
    fragment = material["contentFragments"][0]
    provider = RecordedExtractionProvider([valid_payload(material["id"], fragment["id"], fragment["text"])])
    repository = MemoryAiRunRepository()

    result = service(provider, repository).extract(
        workspace=workspace(), radar=radar(), run=run(), materials=[material, metadata_material()]
    )

    assert result["signalExtractionReport"]["status"] == "succeeded"
    assert result["signalExtractionReport"]["decisionCoverageComplete"] is True
    assert len(result["signalExtractionReport"]["materialDecisions"]) == 2
    assert result["sourceSignals"][0]["reviewStatus"] == "candidate"
    assert result["sourceSignals"][0]["evidenceRefs"][0]["fragmentId"] == fragment["id"]
    assert "suggestedTopicId" not in result["sourceSignals"][0]
    assert repository.runs[0].capability == AiRunCapability.SIGNAL_EXTRACTION
    assert repository.runs[0].request_payload["payloadBudget"]["status"] == "directlyBudgeted"
    assert repository.runs[0].request_payload["messageCharCount"] <= 16000
    assert repository.runs[0].result_payload["providerUsage"]["total_tokens"] == 1180


def test_invalid_primary_is_repaired_without_copying_previous_response() -> None:
    material = readable_material()
    fragment = material["contentFragments"][0]
    provider = RecordedExtractionProvider(
        [
            {"signals": [{"type": "case"}], "materialDecisions": []},
            valid_payload(material["id"], fragment["id"], fragment["text"]),
        ]
    )
    repository = MemoryAiRunRepository()

    result = service(provider, repository).extract(workspace=workspace(), radar=radar(), run=run(), materials=[material])

    attempts = result["signalExtractionReport"]["providerAttempts"]
    assert [item["attemptLabel"] for item in attempts] == ["primary", "repair"]
    assert [item["status"] for item in attempts] == ["failed", "accepted"]
    assert len(provider.calls) == 2
    repair_user_message = provider.calls[1]["messages"][1]["content"]
    assert "repairContext" in repair_user_message
    assert len(repair_user_message) <= 16000
    assert repository.runs[0].request_payload["providerInput"].get("repairContext") is None
    assert repository.runs[0].result_payload["providerUsage"]["total_tokens"] == 1180
    assert len(repository.runs[1].request_payload["providerInput"]["repairContext"]) <= 1200


def test_confidence_accepts_case_insensitive_and_bounded_numeric_values() -> None:
    material = readable_material()
    fragment = material["contentFragments"][0]
    uppercase = valid_payload(material["id"], fragment["id"], fragment["text"])
    uppercase["signals"][0]["confidence"] = "HIGH"
    numeric = valid_payload(material["id"], fragment["id"], fragment["text"])
    numeric["signals"][0]["confidence"] = 0.65

    first = service(RecordedExtractionProvider([uppercase]), MemoryAiRunRepository()).extract(
        workspace=workspace(), radar=radar(), run=run(), materials=[material]
    )
    second = service(RecordedExtractionProvider([numeric]), MemoryAiRunRepository()).extract(
        workspace=workspace(), radar=radar(), run=run(), materials=[material]
    )

    assert first["sourceSignals"][0]["confidence"] == "high"
    assert second["sourceSignals"][0]["confidence"] == "medium"


def test_scalar_collection_fields_are_kept_as_single_values() -> None:
    material = readable_material()
    fragment = material["contentFragments"][0]
    payload = valid_payload(material["id"], fragment["id"], fragment["text"])
    payload["signals"][0].update(
        {
            "actors": "дежурный инженер",
            "limitations": "Работает только при полной истории отказов.",
            "reasonCodes": "industrial-case",
        }
    )
    payload["materialDecisions"][0]["reasonCodes"] = "grounded-case"

    result = service(RecordedExtractionProvider([payload]), MemoryAiRunRepository()).extract(
        workspace=workspace(), radar=radar(), run=run(), materials=[material]
    )

    signal = result["sourceSignals"][0]
    assert signal["actors"] == ["дежурный инженер"]
    assert signal["limitations"] == ["Работает только при полной истории отказов."]
    assert signal["reasonCodes"] == ["industrial-case"]
    assert result["signalExtractionReport"]["materialDecisions"][0]["reasonCodes"] == ["grounded-case"]


def test_more_than_three_signals_per_material_triggers_repair() -> None:
    material = readable_material()
    fragment = material["contentFragments"][0]
    overloaded = valid_payload(material["id"], fragment["id"], fragment["text"])
    overloaded["signals"] = [
        {**overloaded["signals"][0], "title": title}
        for title in ("Первый сигнал", "Второй сигнал", "Третий сигнал", "Четвертый сигнал")
    ]
    provider = RecordedExtractionProvider(
        [overloaded, valid_payload(material["id"], fragment["id"], fragment["text"])]
    )

    result = service(provider, MemoryAiRunRepository()).extract(
        workspace=workspace(), radar=radar(), run=run(), materials=[material]
    )

    assert [item["status"] for item in result["signalExtractionReport"]["providerAttempts"]] == ["failed", "accepted"]
    assert "too-many-signals-for-material" in result["signalExtractionReport"]["providerAttempts"][0]["error"]
    assert len(result["sourceSignals"]) == 1


def test_primary_and_repair_failure_use_backup_then_preserve_usage() -> None:
    material = readable_material()
    fragment = material["contentFragments"][0]
    provider = RecordedExtractionProvider(
        [
            RuntimeError("timeout"),
            {"signals": [], "materialDecisions": []},
            valid_payload(material["id"], fragment["id"], fragment["text"]),
        ]
    )
    repository = MemoryAiRunRepository()

    result = service(provider, repository).extract(workspace=workspace(), radar=radar(), run=run(), materials=[material])

    attempts = result["signalExtractionReport"]["providerAttempts"]
    assert [item["attemptLabel"] for item in attempts] == ["primary", "repair", "backup"]
    assert attempts[-1]["status"] == "accepted"
    assert provider.calls[-1]["model"] == "backup/model"
    assert repository.runs[-1].fallback_used is True


def test_unsupported_number_is_rejected_and_safe_fallback_emits_no_signal() -> None:
    material = readable_material()
    fragment = material["contentFragments"][0]
    bad = valid_payload(material["id"], fragment["id"], fragment["text"])
    bad["signals"][0]["summary"] = "Эффект составил 999 процентов."
    provider = RecordedExtractionProvider([bad, bad, bad])

    result = service(provider, MemoryAiRunRepository()).extract(
        workspace=workspace(), radar=radar(), run=run(), materials=[material]
    )

    assert result["sourceSignals"] == []
    assert result["signalExtractionReport"]["status"] == "failed"
    assert result["signalExtractionReport"]["groundingViolations"]
    assert result["signalExtractionReport"]["groundingViolations"][0]["reasonCode"] == "number-or-date-not-grounded"
    assert result["signalExtractionReport"]["materialDecisions"][0]["decision"] == "extractionFailed"
    assert result["signalExtractionReport"]["warnings"] == ["signal-extraction-safe-no-signal-fallback"]


def test_metadata_only_material_does_not_call_provider() -> None:
    provider = RecordedExtractionProvider([])

    result = service(provider, MemoryAiRunRepository()).extract(
        workspace=workspace(), radar=radar(), run=run(), materials=[metadata_material()]
    )

    assert provider.calls == []
    assert result["signalExtractionReport"]["status"] == "notRun"
    assert result["signalExtractionReport"]["materialDecisions"][0]["decision"] == "insufficient"


def test_blocked_current_call_budget_never_calls_provider() -> None:
    material = readable_material()
    material["id"] = "material-" + ("x" * 20_000)
    material["contentFragments"] = FoundMaterialFragmentPolicy().from_read_text(
        material_id=material["id"], text=material["summary"]
    )
    provider = RecordedExtractionProvider([])
    repository = MemoryAiRunRepository()

    result = service(provider, repository).extract(
        workspace=workspace(), radar=radar(), run=run(), materials=[material]
    )

    assert provider.calls == []
    assert len(result["signalExtractionReport"]["providerAttempts"]) == 1
    assert result["signalExtractionReport"]["providerAttempts"][0]["status"] == "blocked"
    assert repository.runs[0].request_payload["payloadBudget"]["status"] == "blocked"


def test_legacy_summary_is_degraded_and_high_confidence_is_capped() -> None:
    material = readable_material()
    material.pop("contentFragments")
    dossier = SignalExtractionDossierFactory().build(
        context=SignalExtractionContextFactory().build(workspace=workspace(), radar=radar()),
        materials=[material],
        profile=UpstreamProviderBudgetProfileRegistry().resolve(operation_id="signalExtraction", execution_mode="standard"),
    )
    fragment = next(iter(dossier.fragment_index.values()))
    fragment_id = fragment["id"]
    provider = RecordedExtractionProvider([valid_payload(material["id"], fragment_id, fragment["text"])])

    result = service(provider, MemoryAiRunRepository()).extract(
        workspace=workspace(), radar=radar(), run=run(), materials=[material]
    )

    assert result["signalExtractionReport"]["dossier"]["readiness"] == "DEGRADED"
    assert result["sourceSignals"][0]["confidence"] == "medium"
    assert "legacy-summary-confidence-capped" in result["sourceSignals"][0]["reasonCodes"]


def test_standard_profile_bounds_materials_fragments_input_and_output() -> None:
    profile = UpstreamProviderBudgetProfileRegistry().resolve(
        operation_id="signalExtraction", execution_mode="standard"
    )
    assert (profile.max_materials, profile.max_fragments_per_material, profile.max_fragment_chars) == (2, 4, 900)
    assert (profile.max_provider_input_chars, profile.max_message_chars, profile.max_approx_tokens) == (12000, 16000, 4000)
    assert profile.max_output_tokens == 2200


def test_stress_dossier_is_compacted_inside_each_execution_mode_budget() -> None:
    long_text = ("Проверяемый промышленный факт с механизмом и ограничением. " * 220).strip()
    materials = []
    for index in range(4):
        material_id = f"material-stress-{index}"
        material = readable_material()
        material.update({"id": material_id, "summary": long_text})
        material["contentFragments"] = FoundMaterialFragmentPolicy().from_read_text(
            material_id=material_id, text=long_text
        )
        materials.append(material)
    dense_radar = radar()
    dense_radar["scope"] = "Область поиска " * 100
    dense_radar["rules"] = [
        {"id": f"rule-{index}", "statement": "Проверять механизм, результат и ограничения " * 20, "status": "active"}
        for index in range(12)
    ]
    dense_radar["filters"] = [
        {"id": f"filter-{index}", "dimension": "author", "mode": "mustMatch", "instruction": "Контекст фильтра " * 30}
        for index in range(12)
    ]

    for mode, expected_materials in (("smoke", 1), ("standard", 2), ("full", 4)):
        profile = UpstreamProviderBudgetProfileRegistry().resolve(operation_id="signalExtraction", execution_mode=mode)
        dossier = SignalExtractionDossierFactory().build(
            context=SignalExtractionContextFactory().build(workspace=workspace(), radar=dense_radar),
            materials=materials,
            profile=profile,
        )
        serialized_size = len(json.dumps(dossier.provider_input, ensure_ascii=False, sort_keys=True))

        assert serialized_size <= profile.max_provider_input_chars
        assert len(dossier.eligible_material_ids) == expected_materials
        assert dossier.trimmed_fragment_count > 0
        assert dossier.readiness == "DEGRADED"
        assert all(key in dossier.fragment_index for key in [
            (material["id"], fragment["id"])
            for material in dossier.provider_input["materials"]
            for fragment in material["fragments"]
        ])


def test_recorded_golden_signal_extraction_benchmark_passes_all_cases() -> None:
    report = run_signal_extraction_golden_benchmark()
    assert report["status"] == "passed"
    assert report["caseCount"] == 8
    assert report["passedCount"] == 8
    assert report["failures"] == []


def service(provider: RecordedExtractionProvider, repository: MemoryAiRunRepository) -> SignalExtractionService:
    settings = BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY=SecretStr("test-key"),
        OPENROUTER_DEFAULT_MODEL="primary/model",
        OPENROUTER_BACKUP_MODEL="backup/model",
        DRAFT_RUN_EXECUTION_MODE="standard",
        AI_RUN_AUDIT_DB_PATH=Path("var/test-ai-runs.sqlite3"),
    )
    return SignalExtractionService(
        settings=settings,
        provider=provider,
        ai_run_service=AiRunService(repository=repository),
    )


def readable_material() -> dict[str, Any]:
    text = (
        "На сборочной линии инженеры внедрили систему предиктивного обслуживания. "
        "Система сопоставляет вибрацию оборудования с журналом ремонтов и предупреждает мастера. "
        "Авторы отмечают ограничение: результат зависит от качества истории отказов."
    )
    return {
        "id": "material-case-1",
        "radarRunId": "radar-run-1",
        "sourceHandleId": "open-web",
        "title": "Промышленный кейс",
        "locator": "https://example.org/case",
        "summary": text,
        "status": "found",
        "capturedAt": "2026-07-14T10:00:00+00:00",
        "provenanceLabel": "example.org",
        "contentFragments": FoundMaterialFragmentPolicy().from_read_text(material_id="material-case-1", text=text),
    }


def metadata_material() -> dict[str, Any]:
    return {
        "id": "material-no-read",
        "radarRunId": "radar-run-1",
        "sourceHandleId": "open-web",
        "title": "Недоступная страница",
        "locator": "https://example.org/missing",
        "summary": "Краткий поисковый фрагмент",
        "status": "metadataOnly",
        "capturedAt": "2026-07-14T10:00:00+00:00",
        "provenanceLabel": "example.org",
    }


def valid_payload(material_id: str, fragment_id: str, quote: str) -> dict[str, Any]:
    return {
        "signals": [
            {
                "type": "case",
                "title": "Предиктивное обслуживание связывает вибрацию с историей ремонтов",
                "summary": "Система предупреждает мастера на основе двух производственных источников данных.",
                "confidence": "high",
                "uncertainty": "Применимость зависит от качества истории отказов.",
                "evidenceRefs": [{"materialId": material_id, "fragmentId": fragment_id, "quote": quote}],
                "mechanism": "Сопоставление вибрации оборудования с журналом ремонтов.",
                "actors": ["инженеры", "мастер"],
                "outcome": "Мастер получает предупреждение.",
                "limitations": ["Результат зависит от качества истории отказов."],
                "reasonCodes": ["industrial-case", "mechanism-present", "limitation-present"],
            }
        ],
        "materialDecisions": [
            {"materialId": material_id, "decision": "signalProducing", "reasonCodes": ["grounded-case"]}
        ],
    }


def workspace() -> dict[str, Any]:
    return {"id": "project-ai-design-patterns", "projectId": "project-ai-design-patterns"}


def radar() -> dict[str, Any]:
    return {
        "id": "ai-pattern-radar-industrial-cases",
        "scope": "Промышленные AI-кейсы с механизмом, результатом и ограничениями",
        "rules": [{"id": "rule-case", "statement": "Искать проверяемые производственные кейсы", "status": "active"}],
        "filters": [],
    }


def run() -> dict[str, Any]:
    return {"id": "radar-run-1", "radarId": "ai-pattern-radar-industrial-cases"}
