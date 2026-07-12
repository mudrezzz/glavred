from backend.app.drafting.application.context.draft_run_context_access import DraftRunContextAccessService
from backend.app.drafting.application.dossiers.provider_dossier_factories import (
    FinalQualityDossierFactory,
    RankingDossierFactory,
    ReviewDossierFactory,
    RevisionDossierFactory,
)
from backend.app.drafting.application.final_quality.draft_final_quality_dossier_attempt import FinalQualityDossierAttemptBuilder
from backend.app.drafting.application.revision.draft_pairwise_ranking_dossier_attempt import PairwiseRankingDossierAttemptBuilder
from backend.app.drafting.application.revision.draft_revision_dossier_attempt import RevisionDossierAttemptBuilder
from backend.app.drafting.application.validation.draft_llm_validation_dossier_attempt import LlmValidationDossierAttemptBuilder


def test_ranking_dossier_includes_persisted_challenger_with_equal_body_windows() -> None:
    access = DraftRunContextAccessService.from_snapshot(snapshot())
    dossier = RankingDossierFactory(access).build()

    candidates = dossier.provider_input()["candidates"]
    assert [item["id"] for item in candidates] == ["candidate-1", "candidate-2", "challenger-1"]
    assert all(set(item["bodyWindows"]) == {"opening", "middle", "ending"} for item in candidates)
    assert all(len("".join(item["bodyWindows"].values())) == 3000 for item in candidates)
    assert dossier.missing_required_inputs == ()
    assert all(access.resolve(handle).status.value == "resolved" for handles in dossier.handles.values() for handle in handles)


def test_review_ranking_revision_and_final_attempts_record_direct_budget() -> None:
    access = DraftRunContextAccessService.from_snapshot(snapshot())
    review = ReviewDossierFactory(access).build(candidate_id="candidate-1")
    ranking = RankingDossierFactory(access).build()
    revision = RevisionDossierFactory(access).build(candidate_id="candidate-1")
    final_quality = FinalQualityDossierFactory(access).build(candidate_id="candidate-1")
    review_attempt = LlmValidationDossierAttemptBuilder().prepare(
        dossier=review,
        candidate_id="candidate-1",
        model="review-model",
        attempt={"label": "primary", "model": "review-model"},
        model_selection={"modelRole": "review"},
        execution_mode="standard",
        repair_context=None,
    )
    ranking_attempt = PairwiseRankingDossierAttemptBuilder().prepare(
        dossier=ranking,
        model="review-model",
        attempt={"label": "primary", "model": "review-model"},
        model_selection={"modelRole": "review"},
        execution_mode="standard",
        repair_context=None,
    )
    ranking_repair_attempt = PairwiseRankingDossierAttemptBuilder().prepare(
        dossier=ranking,
        model="review-model",
        attempt={"label": "primary-repair", "model": "review-model", "repair": True},
        model_selection={"modelRole": "review"},
        execution_mode="standard",
        repair_context={"errorType": "schemaFailure", "validationDetails": {"missingPairs": [{"leftCandidateId": "candidate-1", "rightCandidateId": "candidate-2"}]}},
    )
    revision_attempt = RevisionDossierAttemptBuilder().prepare(
        dossier=revision,
        model="writer-model",
        attempt={"label": "primary", "model": "writer-model"},
        model_selection={"modelRole": "writer"},
        generation_params={"temperature": 0.2, "topP": 0.9},
        execution_mode="standard",
        repair_context=None,
    )
    final_attempt = FinalQualityDossierAttemptBuilder().prepare(
        dossier=final_quality,
        model="final-model",
        attempt={"label": "primary", "model": "final-model"},
        model_selection={"modelRole": "finalGate"},
        execution_mode="standard",
        model_independence="independent",
        repair_context=None,
    )

    for prepared in (review_attempt, ranking_attempt, ranking_repair_attempt, revision_attempt, final_attempt):
        request = prepared.request_payload
        assert request["providerDossier"]["runtimeMigrated"] is True
        assert request["payloadBudget"]["promptCharEstimate"] <= request["payloadBudget"]["limits"]["maxPromptChars"]
        assert request["operationId"] in {"llmValidation", "pairwiseRanking", "directedRevision", "finalQualityGateReview"}
        assert not ({"sourceLedger", "rulePack", "materialPlan", "candidatePool", "validationReport"} & set(request["providerInput"]))
    assert ranking_attempt.blocked_reason is None
    assert ranking_attempt.request_payload["messageCharCount"] <= 22000
    assert ranking_attempt.request_payload["providerInputCharEstimate"] <= 19000
    assert ranking_repair_attempt.blocked_reason is None
    assert ranking_repair_attempt.request_payload["repairContextCharCount"] > 0
    assert ranking_repair_attempt.request_payload["messageCharCount"] <= 22000
    assert final_attempt.request_payload["payloadBudget"]["profileId"] == "finalQualityReviewRepair"
    assert final_attempt.request_payload["payloadBudget"]["operationAlias"] == "finalQualityGateReview"


def test_oversized_nested_review_context_is_compacted_before_prompt_construction() -> None:
    data = snapshot()
    validation = data["steps"]["validation"]
    context = validation["reviewContext"]
    for candidate in context["candidates"]:
        candidate["usedEvidence"] = [{"id": f"claim-{index}", "snippet": "E" * 900} for index in range(16)]
        candidate["ruleCoverage"] = [{"id": f"rule-{index}", "statement": "R" * 700} for index in range(16)]
    context["currentCandidate"] = dict(context["candidates"][0])
    findings = [
        {
            "id": f"finding-{index}",
            "candidateId": "candidate-1",
            "validatorId": f"validator-{index}",
            "severity": "warning",
            "message": "M" * 1600,
            "repairGuidance": "G" * 1600,
            "metadata": {"operationEnvelope": {"payloadBudget": {"nested": True}}},
        }
        for index in range(20)
    ]
    context["validationReport"] = {"candidateReports": [{"candidateId": "candidate-1", "findings": findings}]}
    context["revisionInstruction"] = {
        "candidateId": "candidate-1",
        "status": "created",
        "repairGoals": ["Goal " + "X" * 900 for _ in range(10)],
        "sourceFindings": findings,
        "editorialGoals": ["Editorial " + "Y" * 900 for _ in range(12)],
    }
    context["finalQualityContract"] = {
        "version": "v1",
        "thesis": "T" * 1200,
        "acceptanceCriteria": ["A" * 900 for _ in range(12)],
        "hardRuleIds": [f"rule-{index}" for index in range(40)],
    }
    context["deterministicGate"] = {
        "status": "warning",
        "candidateId": "candidate-1",
        "finalRepairGoals": ["Repair " + "Z" * 900 for _ in range(12)],
        "actionableAttributionFindings": findings,
        "operationEnvelope": {"payloadBudget": {"nested": True}},
    }
    access = DraftRunContextAccessService.from_snapshot(data)
    prepared = (
        LlmValidationDossierAttemptBuilder().prepare(
            dossier=ReviewDossierFactory(access).build(candidate_id="candidate-1"),
            candidate_id="candidate-1",
            model="review-model",
            attempt={"label": "primary", "model": "review-model"},
            model_selection={"modelRole": "review"},
            execution_mode="standard",
            repair_context=None,
        ),
        PairwiseRankingDossierAttemptBuilder().prepare(
            dossier=RankingDossierFactory(access).build(),
            model="review-model",
            attempt={"label": "primary", "model": "review-model"},
            model_selection={"modelRole": "review"},
            execution_mode="standard",
            repair_context=None,
        ),
        RevisionDossierAttemptBuilder().prepare(
            dossier=RevisionDossierFactory(access).build(candidate_id="candidate-1"),
            model="writer-model",
            attempt={"label": "primary", "model": "writer-model"},
            model_selection={"modelRole": "writer"},
            generation_params={"temperature": 0.2},
            execution_mode="standard",
            repair_context=None,
        ),
        FinalQualityDossierAttemptBuilder().prepare(
            dossier=FinalQualityDossierFactory(access).build(candidate_id="candidate-1"),
            model="final-model",
            attempt={"label": "primary", "model": "final-model"},
            model_selection={"modelRole": "finalGate"},
            execution_mode="standard",
            model_independence="independent",
            repair_context=None,
        ),
    )

    for attempt in prepared:
        request = attempt.request_payload
        max_chars = request["payloadBudget"]["limits"]["maxPromptChars"]
        assert request["payloadBudget"].get("incident") is None
        assert request["payloadBudget"]["promptCharEstimate"] <= max_chars
        assert sum(len(message["content"]) for message in attempt.messages) <= max_chars
        assert "operationEnvelope" not in str(request["providerInput"])
        assert "payloadBudget" not in str(request["providerInput"])


def snapshot() -> dict:
    long_body = "A" * 5000
    candidates = [
        {"id": "candidate-1", "title": "One", "body": long_body, "usedEvidence": ["claim-1"], "ruleCoverage": ["rule-1"]},
        {"id": "candidate-2", "title": "Two", "body": long_body.replace("A", "B"), "usedEvidence": ["claim-1"], "ruleCoverage": ["rule-1"]},
    ]
    challenger = {"id": "challenger-1", "title": "Three", "body": long_body.replace("A", "C"), "usedEvidence": ["claim-1"], "ruleCoverage": ["rule-1"]}
    reports = [
        {"candidateId": item["id"], "findings": [{"id": f"finding-{item['id']}", "validatorId": "voice", "severity": "warning", "message": "Issue"}]}
        for item in [*candidates, challenger]
    ]
    return {
        "runId": "review-dossier-test",
        "steps": {
            "postContract": {"thesis": "A controlled decision workflow", "audience": "Product leaders"},
            "publicEvidence": {"enrichedSourceLedger": {"claims": [{"id": "claim-1", "statement": "Evidence", "allowedUse": "canState"}]}},
            "rulePack": {"ruleRegistrySnapshot": {"rules": [{"id": "rule-1", "statement": "Ground claims"}]}},
            "draft": {"candidates": candidates},
            "validation": {
                "candidateReports": reports,
                "alternativeAngleTournament": {"status": "succeeded", "candidate": challenger},
                "reviewContext": {
                    "stage": "review-test",
                    "candidates": [*candidates, challenger],
                    "currentCandidate": candidates[0],
                    "validationReport": {"candidateReports": reports},
                    "revisionInstruction": {"status": "created", "candidateId": "candidate-1", "repairGoals": ["Fix issue"]},
                    "finalQualityContract": {"version": "final-quality-contract-v1", "criteria": ["Reader value"]},
                    "deterministicGate": {"status": "warning", "candidateId": "candidate-1"},
                    "repairHistory": {"cycles": []},
                },
            },
        },
    }
