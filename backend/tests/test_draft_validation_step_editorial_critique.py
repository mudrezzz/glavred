from typing import Any

from backend.app.drafting.application.planning.draft_planning_result import DraftPlanningStepResult
from backend.app.drafting.application.validation.draft_validation_step_service import DraftValidationStepService


def test_validation_step_attaches_editorial_critique_report() -> None:
    service = DraftValidationStepService(editorial_critic=FakeEditorialCritic())

    result = service.validate(
        draft_artifact={"candidates": [{"id": "candidate-1", "title": "Title", "body": "Body"}], "selection": {"selectedCandidateId": "candidate-1"}},
        context_artifact={},
        rule_pack={},
        material_plan={},
    )

    assert result.artifact_payload["editorialCritiqueReport"]["status"] == "warning"
    assert result.ai_run_ids == ["ai-critic-1"]


class FakeEditorialCritic:
    def critique(self, **_: Any) -> DraftPlanningStepResult:
        return DraftPlanningStepResult(
            artifact_payload={
                "status": "warning",
                "candidateReports": [
                    {
                        "candidateId": "candidate-1",
                        "editorialRisk": "high",
                        "findings": [{"validatorId": "critic.genericAiProse", "message": "Too generic."}],
                    }
                ],
            },
            ai_run_id="ai-critic-1",
            ai_run_ids=["ai-critic-1"],
        )
