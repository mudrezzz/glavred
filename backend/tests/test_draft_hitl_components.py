import json

from backend.app.application.json_step_retry_policy import JsonStepAttempt
from backend.app.domain.draft_model_roles import DraftModelRole
from backend.app.drafting.application.hitl.human_comment_attempt_trace import HumanCommentAttemptTraceBuilder
from backend.app.drafting.application.hitl.human_comment_context import HumanCommentVersionCompactor
from backend.app.drafting.application.hitl.human_comment_prompts import (
    HumanCommentQualityPromptBuilder,
    HumanCommentRevisionPromptBuilder,
)
from backend.app.drafting.application.hitl.human_comment_quality_components import (
    HumanCommentQualityOverlayPolicy,
    HumanCommentQualityPayloadParser,
)


def test_human_comment_prompt_builders_preserve_required_json_shape() -> None:
    version = {"id": "v1", "versionNumber": 1, "title": "T", "body": "B", "ignored": "x"}
    trace_context = {"traceStatus": "available"}

    revision_messages = HumanCommentRevisionPromptBuilder().build_messages(
        current_version=version,
        editor_comment="Make it sharper.",
        trace_context=trace_context,
        repair_context={"requiredShape": "title, body, revisionSummary"},
    )
    quality_messages = HumanCommentQualityPromptBuilder().build_messages(
        base_version=version,
        revised_version={**version, "body": "B2"},
        editor_comment="Make it sharper.",
        trace_context=trace_context,
        repair_context=None,
    )

    assert [item["role"] for item in revision_messages] == ["system", "user"]
    assert [item["role"] for item in quality_messages] == ["system", "user"]
    revision_payload = json.loads(revision_messages[1]["content"])
    quality_payload = json.loads(quality_messages[1]["content"])
    assert revision_payload["requiredJson"] == {"title": "string", "body": "string", "revisionSummary": "string"}
    assert set(quality_payload["requiredJson"]) == {
        "status",
        "commentComplianceStatus",
        "sourceIntegrityStatus",
        "publicProseStatus",
        "internalJargonLeaks",
        "regressionWarnings",
        "matchedCommentIntents",
        "missedCommentIntents",
        "summary",
    }
    assert revision_payload["currentVersion"] == HumanCommentVersionCompactor().compact(version)


def test_human_comment_attempt_trace_records_incidents_and_operation_envelope() -> None:
    builder = HumanCommentAttemptTraceBuilder(
        operation_id="humanCommentRevision",
        operation_kind="hitlWriterRevision",
        owner="test.owner",
        model_role=DraftModelRole.WRITER,
    )
    attempt = builder.attempt_record(
        JsonStepAttempt(label="primary", model="model-a"),
        "ai-1",
        "error",
        {"modelRole": "writer", "selectedModel": "model-a"},
        "malformed json",
        input_stats={"candidateCount": 1},
        payload_stats={"payloadBudget": {"profileId": "humanCommentRevision"}},
    )
    envelope = builder.operation_envelope(
        "failed",
        [attempt],
        safe_error="malformed json",
        failure_reason="provider-failed",
        payload_stats={"payloadBudget": {"profileId": "humanCommentRevision"}},
    )

    assert attempt["incident"]["incidentType"] == "malformedJson"
    assert envelope["operationId"] == "humanCommentRevision"
    assert envelope["incident"]["incidentType"] == "malformedJson"
    assert envelope["payloadStats"]["payloadBudget"]["profileId"] == "humanCommentRevision"


def test_human_comment_quality_parser_and_overlay_preserve_deterministic_checks() -> None:
    parser = HumanCommentQualityPayloadParser()
    check = parser.parse(
        {
            "status": "passed",
            "commentComplianceStatus": "passed",
            "sourceIntegrityStatus": "passed",
            "publicProseStatus": "passed",
            "internalJargonLeaks": [],
            "regressionWarnings": [],
            "matchedCommentIntents": ["shorter"],
            "missedCommentIntents": [],
            "summary": "Looks good.",
        },
        attempts=[{"label": "primary"}],
    )

    overlaid = HumanCommentQualityOverlayPolicy(parser).apply(
        check,
        base_body="Current body cites B2BNotes.",
        revised_body="Revised body exposes SourceLedger.",
    )

    assert overlaid.status == "warning"
    assert overlaid.public_prose_status == "warning"
    assert overlaid.source_integrity_status == "warning"
    assert "SourceLedger" in overlaid.internal_jargon_leaks
    assert any("B2BNotes" in warning for warning in overlaid.regression_warnings)
