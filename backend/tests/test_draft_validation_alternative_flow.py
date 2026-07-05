from typing import Any

from backend.app.drafting.application.validation.draft_validation_alternative_flow import DraftValidationAlternativeFlow
from backend.app.drafting.application.validation.draft_validation_report_flow import DraftValidationReportFlowResult


def test_alternative_flow_validates_only_challenger_after_merge() -> None:
    reports = RecordingReports()
    flow = DraftValidationAlternativeFlow(reports=reports, alternative=FakeAlternative())
    initial = {"status": "warning", "candidateReports": [{"candidateId": "candidate-1", "status": "warning"}]}

    merged, artifact, ai_run_ids = flow.apply(
        request=object(),
        context_summary={},
        draft_artifact={"candidates": [{"id": "candidate-1"}]},
        initial_validation=initial,
        initial_ai_run_ids=["ai-initial"],
        context_artifact={},
        rule_pack={},
        material_plan={},
        draft_strategy={},
        progress=None,
    )

    assert reports.seen_candidate_ids == [["alternative-angle-1"]]
    assert [item["candidateId"] for item in artifact["candidateReports"]] == ["candidate-1", "alternative-angle-1"]
    assert ai_run_ids == ["ai-initial", "ai-alt", "ai-validation-alternative-angle-1"]
    assert merged["alternativeAngleCandidateId"] == "alternative-angle-1"


class FakeAlternative:
    def run(self, **_: Any):
        merged = {
            "candidates": [{"id": "candidate-1"}, {"id": "alternative-angle-1"}],
            "alternativeAngleCandidateId": "alternative-angle-1",
        }
        return merged, {"status": "succeeded"}, ["ai-alt"]


class RecordingReports:
    def __init__(self) -> None:
        self.seen_candidate_ids: list[list[str]] = []

    def run(self, *, draft_artifact: dict[str, Any], **_: Any) -> DraftValidationReportFlowResult:
        ids = [str(item.get("id")) for item in draft_artifact.get("candidates", []) if isinstance(item, dict)]
        self.seen_candidate_ids.append(ids)
        report = {"status": "passed", "candidateReports": [{"candidateId": candidate_id, "status": "passed"} for candidate_id in ids]}
        return DraftValidationReportFlowResult(report, [f"ai-validation-{candidate_id}" for candidate_id in ids])
