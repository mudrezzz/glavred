import json
from dataclasses import dataclass
from typing import Any

from backend.app.application.ai_run_service import AiRunService
from backend.app.application.deterministic_pairwise_ranking import DeterministicPairwiseRanker
from backend.app.application.draft_directed_revision_service import DraftDirectedRevisionService
from backend.app.application.draft_pairwise_ranking_service import DraftPairwiseRankingService
from backend.app.application.draft_ranking_revision_service import DraftRankingRevisionService
from backend.app.domain.draft_generation import DraftBriefContext, DraftEditorialModelContext, DraftGenerationRequest
from backend.app.infrastructure.openrouter_config import OpenRouterConfigValidator
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.settings import BackendSettings


@dataclass
class FakeJsonResult:
    payload: dict[str, Any]
    raw_response: dict[str, Any]


class SequenceAdapter:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, **kwargs: Any) -> FakeJsonResult:
        self.calls.append(kwargs)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return FakeJsonResult(response, {"id": f"call-{len(self.calls)}", "model": kwargs.get("model")})


def test_deterministic_ranking_prefers_fewer_validation_findings_on_score_tie() -> None:
    report = DeterministicPairwiseRanker().rank(
        draft_artifact={
            "candidates": [{"id": "a"}, {"id": "b"}],
            "selection": {"scorecard": [{"candidateId": "a", "total": 80}, {"candidateId": "b", "total": 80}]},
        },
        validation_report={
            "candidateReports": [
                {"candidateId": "a", "criticalCount": 0, "warningCount": 2},
                {"candidateId": "b", "criticalCount": 0, "warningCount": 0},
            ]
        },
    )

    assert report.decision.winner_candidate_id == "b"
    assert report.comparisons[0].winner_candidate_id == "b"


def test_pairwise_ranking_retries_malformed_json_and_uses_repair(tmp_path) -> None:
    adapter = SequenceAdapter([
        {"winnerCandidateId": "missing", "reason": "bad", "comparisons": []},
        {"winnerCandidateId": "b", "reason": "better validation", "comparisons": [{"leftCandidateId": "a", "rightCandidateId": "b", "winnerCandidateId": "b", "reason": "cleaner"}]},
    ])
    service = DraftPairwiseRankingService(
        settings=settings(configured=True, review_model="review-model"),
        ai_run_service=ai_service(tmp_path),
        openrouter_validator=OpenRouterConfigValidator(),
        openrouter_adapter=adapter,
    )

    report = service.rank(
        draft_artifact={"candidates": [{"id": "a"}, {"id": "b"}], "selection": {"scorecard": []}},
        validation_report={"candidateReports": []},
        context_artifact={},
        rule_pack={},
        material_plan={},
    )

    assert report.decision.winner_candidate_id == "b"
    assert [attempt["label"] for attempt in report.attempts] == ["primary", "primary-repair"]
    assert adapter.calls[0]["model"] == "review-model"
    assert report.attempts[0]["modelRole"] == "review"
    assert report.attempts[0]["status"] == "error"
    assert len(report.ai_run_ids) == 2


def test_ranking_revision_accepts_non_regressing_revision(tmp_path) -> None:
    ranking_adapter = SequenceAdapter([
        {"winnerCandidateId": "candidate-1", "reason": "winner", "comparisons": []},
        {"title": "Revised", "body": "Revised body with CTA and source marker alanknox", "changeLog": ["Added attribution"]},
        {"winnerCandidateId": "revised-candidate-1", "reason": "better", "comparisons": [{"leftCandidateId": "candidate-1", "rightCandidateId": "revised-candidate-1", "winnerCandidateId": "revised-candidate-1", "reason": "resolved"}]},
    ])
    service = ranking_revision_service(tmp_path, ranking_adapter)

    result = service.run(
        request=request(),
        draft_artifact=draft_artifact(),
        validation_report=validation_report(),
        context_artifact=context_artifact(),
        rule_pack={},
        material_plan={},
    )

    assert result.final_draft is not None
    assert result.final_draft.title == "Revised"
    assert result.artifact_payload["finalDecision"]["source"] == "revisionLoop"
    assert result.artifact_payload["revisionLoop"]["cycles"][0]["accepted"] is True


def test_ranking_revision_rejects_revision_that_breaks_hard_max(tmp_path) -> None:
    ranking_adapter = SequenceAdapter([
        {"winnerCandidateId": "candidate-1", "reason": "winner", "comparisons": []},
        {"title": "Too long", "body": "x" * 200, "changeLog": ["Expanded"]},
        {"winnerCandidateId": "candidate-1", "reason": "old is safer", "comparisons": [{"leftCandidateId": "candidate-1", "rightCandidateId": "revised-candidate-1", "winnerCandidateId": "candidate-1", "reason": "too long"}]},
    ])
    service = ranking_revision_service(tmp_path, ranking_adapter)

    result = service.run(
        request=request(),
        draft_artifact=draft_artifact(),
        validation_report=validation_report(),
        context_artifact=context_artifact(),
        rule_pack={},
        material_plan={},
    )

    assert result.final_draft is not None
    assert result.final_draft.title == "Original"
    assert result.artifact_payload["finalDecision"]["source"] == "originalCandidate"
    assert result.artifact_payload["revisionLoop"]["cycles"][0]["accepted"] is False
    assert "revised-critical-count-increased" in result.artifact_payload["revisionLoop"]["cycles"][0]["rejectionReasons"]


def test_revision_loop_carries_rejection_constraints_to_next_cycle(tmp_path) -> None:
    adapter = SequenceAdapter([
        {"winnerCandidateId": "candidate-1", "reason": "winner", "comparisons": []},
        {"title": "Too long", "body": "x" * 200, "changeLog": ["Expanded"]},
        {"winnerCandidateId": "candidate-1", "reason": "old is safer", "comparisons": [{"leftCandidateId": "candidate-1", "rightCandidateId": "revised-candidate-1", "winnerCandidateId": "candidate-1", "reason": "too long"}]},
        {"title": "Revised", "body": "Revised body with CTA and source marker alanknox", "changeLog": ["Fixed"]},
        {"winnerCandidateId": "revised-candidate-1", "reason": "better", "comparisons": [{"leftCandidateId": "candidate-1", "rightCandidateId": "revised-candidate-1", "winnerCandidateId": "revised-candidate-1", "reason": "fixed"}]},
    ])
    service = ranking_revision_service(tmp_path, adapter, max_iterations=2)

    result = service.run(
        request=request(),
        draft_artifact=draft_artifact(),
        validation_report=validation_report(),
        context_artifact=context_artifact(),
        rule_pack={},
        material_plan={},
    )

    assert result.final_draft is not None
    assert result.final_draft.title == "Revised"
    cycles = result.artifact_payload["revisionLoop"]["cycles"]
    assert [cycle["accepted"] for cycle in cycles] == [False, True]
    second_revision_call = _directed_revision_calls(adapter)[1]
    instruction = json.loads(second_revision_call["messages"][1]["content"])["revisionInstruction"]
    assert any("Do not repeat failed move" in item for item in instruction["constraints"])


def ranking_revision_service(tmp_path, adapter: SequenceAdapter, max_iterations: int = 1) -> DraftRankingRevisionService:
    ai = ai_service(tmp_path)
    return DraftRankingRevisionService(
        ranking_service=DraftPairwiseRankingService(
            settings=settings(configured=True, review_model="review-model"),
            ai_run_service=ai,
            openrouter_validator=OpenRouterConfigValidator(),
            openrouter_adapter=adapter,
        ),
        revision_service=DraftDirectedRevisionService(
            settings=settings(configured=True, writer_model="writer-model"),
            ai_run_service=ai,
            openrouter_validator=OpenRouterConfigValidator(),
            openrouter_adapter=adapter,
        ),
        max_iterations=max_iterations,
    )


def draft_artifact() -> dict[str, Any]:
    return {
        "candidates": [{"id": "candidate-1", "title": "Original", "body": "Original body with CTA", "source": "openrouter"}],
        "selection": {"scorecard": [{"candidateId": "candidate-1", "total": 80, "selectionStatus": "eligible", "publishable": True}]},
    }


def validation_report() -> dict[str, Any]:
    return {
        "candidateReports": [
            {
                "candidateId": "candidate-1",
                "criticalCount": 0,
                "warningCount": 1,
                "findings": [
                    {
                        "validatorId": "evidence.attribution",
                        "severity": "warning",
                        "message": "Needs attribution",
                        "repairGuidance": "Name the source.",
                        "metadata": {"missingClaimIds": ["external-1"]},
                    }
                ],
            }
        ]
    }


def context_artifact() -> dict[str, Any]:
    return {
        "postContract": {
            "cta": "CTA",
            "publicationSizeContract": {
                "minChars": 1,
                "maxChars": 120,
                "hardMaxChars": 120,
                "paragraphRange": {"min": 1, "max": 5},
            },
        },
        "sourceLedger": {"claims": []},
    }


def request() -> DraftGenerationRequest:
    return DraftGenerationRequest(
        brief=DraftBriefContext(
            id="brief-1",
            title="Brief",
            rubric="",
            audience="",
            thesis="thesis",
            conflict="",
            author_position="",
            evidence=[],
            examples=[],
            structure=[],
            cta="CTA",
            risks=[],
            sources=[],
        ),
        editorial_model=DraftEditorialModelContext(audience="", style_rules=[], forbidden_topics=[], goals=[]),
    )


def settings(*, configured: bool, review_model: str = "", writer_model: str = "") -> BackendSettings:
    return BackendSettings(
        _env_file=None,
        OPENROUTER_API_KEY="sk-test-secret" if configured else "",
        OPENROUTER_DEFAULT_MODEL="primary-model" if configured else "",
        DRAFT_REVIEW_MODEL=review_model,
        DRAFT_WRITER_MODEL=writer_model,
    )


def ai_service(tmp_path) -> AiRunService:
    return AiRunService(SqliteAiRunRepository(tmp_path / "ai-runs.sqlite3"))


def _directed_revision_calls(adapter: SequenceAdapter) -> list[dict[str, Any]]:
    return [
        call
        for call in adapter.calls
        if json.loads(call["messages"][1]["content"]).get("task") == "Revise the selected draft candidate once."
    ]
