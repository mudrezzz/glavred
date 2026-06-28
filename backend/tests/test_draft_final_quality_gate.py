from typing import Any

from backend.app.application.draft_final_quality_gate import DraftFinalQualityGateService


class FakeRevisionService:
    def __init__(self, revised: dict[str, Any] | None) -> None:
        self.revised = revised
        self.calls: list[dict[str, Any]] = []

    def revise(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        if not self.revised:
            return {"status": "failed", "reason": "provider-failed", "attempts": [], "aiRunIds": []}
        return {"status": "succeeded", "revisedCandidate": self.revised, "attempts": [{"aiRunId": "ai-final-repair"}], "aiRunIds": ["ai-final-repair"]}


def test_final_quality_gate_passes_clean_public_draft_without_repair() -> None:
    revision = FakeRevisionService(None)
    result = service(revision).run(
        final_candidate=candidate("final-1", "Мой тезис: это важно. Поэтому если вы отвечаете за продукт, проверьте доверие к AI через один понятный сценарий."),
        final_source="revisionLoop",
        validation_report={"candidateReports": []},
        context_artifact=context(),
        rule_pack={},
        material_plan={},
        revision_loop_stop_reason="editorially-improved",
    )

    assert result.final_candidate["id"] == "final-1"
    assert result.artifact_payload["status"] == "passed"
    assert result.artifact_payload["repair"]["status"] == "not-run"
    assert revision.calls == []


def test_final_quality_gate_repairs_internal_jargon_leak() -> None:
    revision = FakeRevisionService(candidate("revised-final-1", "Мой тезис: читатель должен видеть не служебный отчет, а вывод. Поэтому если вы внедряете AI, начните с проверки доверия."))

    result = service(revision).run(
        final_candidate=candidate("final-1", "SourceLedger показывает publicEvidence, а validators нашли PostContract."),
        final_source="revisionLoop",
        validation_report={"candidateReports": []},
        context_artifact=context(),
        rule_pack={},
        material_plan={},
        revision_loop_stop_reason="max-iterations",
    )

    assert result.final_candidate["id"] == "revised-final-1"
    assert result.artifact_payload["status"] == "critical"
    assert result.artifact_payload["acceptedRepair"] is True
    assert result.artifact_payload["repair"]["decisionStatus"] == "accepted"
    assert result.artifact_payload["finalDecision"]["source"] == "finalQualityRepair"
    instruction = revision.calls[0]["instruction"]
    assert "SourceLedger" in instruction["constraints"][0]


def test_final_quality_gate_rejects_repair_that_keeps_jargon() -> None:
    revision = FakeRevisionService(candidate("revised-final-1", "SourceLedger снова показывает publicEvidence, validators и PostContract."))

    result = service(revision).run(
        final_candidate=candidate("final-1", "SourceLedger показывает publicEvidence, а validators нашли PostContract."),
        final_source="revisionLoop",
        validation_report={"candidateReports": []},
        context_artifact=context(),
        rule_pack={},
        material_plan={},
        revision_loop_stop_reason="max-iterations",
    )

    assert result.final_candidate["id"] == "final-1"
    assert result.artifact_payload["acceptedRepair"] is False
    assert result.artifact_payload["repair"]["decisionStatus"] == "rejected"
    assert "internal-jargon-not-improved" in result.artifact_payload["repair"]["rejectionReasons"]
    assert result.artifact_payload["finalDecision"]["source"] == "revisionLoop"


def service(revision: FakeRevisionService) -> DraftFinalQualityGateService:
    return DraftFinalQualityGateService(revision_service=revision)  # type: ignore[arg-type]


def candidate(candidate_id: str, body: str) -> dict[str, Any]:
    return {"id": candidate_id, "title": "Draft", "body": body, "source": "openrouter"}


def context() -> dict[str, Any]:
    return {
        "fabula": {"researchDepth": "standard"},
        "postContract": {
            "cta": "",
            "publicationSizeContract": {
                "minChars": 1,
                "maxChars": 9500,
                "hardMaxChars": 10240,
                "paragraphRange": {"min": 1, "max": 18},
            },
        },
        "sourceLedger": {"claims": []},
    }
