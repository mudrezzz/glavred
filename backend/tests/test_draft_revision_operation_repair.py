from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_to_payload
from backend.app.application.draft_run_progress import DraftRunProgress
from backend.app.domain.draft_run import create_queued_draft_run
from backend.app.domain.draft_run_steps import DraftRunStepKey
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.tests.test_draft_ranking_revision import (
    SequenceAdapter,
    context_artifact,
    draft_artifact,
    ranking_revision_service,
    request,
    validation_report,
)
from backend.tests.test_draft_run_context_builder import make_context


def test_revision_cycle_failure_keeps_previous_best_and_marks_operation_failed(tmp_path) -> None:
    adapter = SequenceAdapter([
        {"winnerCandidateId": "candidate-1", "reason": "winner", "comparisons": []},
        {"title": "Revised", "body": "Revised body with CTA and source marker alanknox", "changeLog": ["Added attribution"]},
        {
            "winnerCandidateId": "revised-candidate-1",
            "reason": "Revision wins but still has an editorial gap.",
            "editorialDimensionScores": [
                {"dimension": "validatorHealth", "winnerCandidateId": "revised-candidate-1", "reason": "Attribution improved."},
                {"dimension": "ideaStrength", "winnerCandidateId": "revised-candidate-1", "reason": "Revision has a sharper idea."},
                {"dimension": "structure", "winnerCandidateId": "candidate-1", "reason": "Original is still cleaner structurally."},
            ],
            "comparisons": [{"leftCandidateId": "candidate-1", "rightCandidateId": "revised-candidate-1", "winnerCandidateId": "revised-candidate-1", "reason": "cleaner"}],
        },
        RuntimeError("writer provider stopped after response"),
        RuntimeError("writer provider stopped after response"),
        RuntimeError("writer provider stopped after response"),
    ])
    repository = SqliteDraftRunRepository(tmp_path / "draft-runs.sqlite3")
    req = request()
    run = create_queued_draft_run(
        request_payload=request_to_payload(req, context_from_payload({"draftContext": make_context()})),
        input_summary={"title": req.brief.title},
    )
    repository.save(run)
    progress = DraftRunProgress(repository, run.id).operation_sink(DraftRunStepKey.VALIDATION)

    result = ranking_revision_service(tmp_path, adapter, max_iterations=2).run(
        request=req,
        draft_artifact=draft_artifact(),
        validation_report={
            **validation_report(),
            "alternativeAngleTournament": {"route": {"risks": ["Do not overcomplicate the structure."]}},
        },
        context_artifact=context_artifact(),
        rule_pack={},
        material_plan={"materialPlan": {"openQuestions": ["Make the central idea sharper."]}},
        progress=progress,
    )

    assert result.final_draft is not None
    assert result.final_draft.title == "Revised"
    assert result.artifact_payload["finalDecision"]["source"] == "revisionLoop"
    assert result.artifact_payload["revisionLoop"]["stopReason"] == "provider-failed"
    assert result.artifact_payload["revisionLoop"]["cycles"][1]["accepted"] is False
    assert result.artifact_payload["revisionLoop"]["cycles"][1]["stopReason"] == "provider-failed"
    assert "directed-revision-provider-failed" in result.artifact_payload["revisionLoop"]["cycles"][1]["rejectionReasons"]
    step = next(item for item in repository.get(run.id).steps if item.key == DraftRunStepKey.VALIDATION)
    failed_op = [item for item in step.artifact_payload["progress"]["operations"] if item["id"] == "directed-revision-cycle-2"][0]
    assert failed_op["status"] == "failed"
    assert "writer provider stopped after response" in failed_op["error"]
