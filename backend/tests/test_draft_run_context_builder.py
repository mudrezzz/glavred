from backend.app.application.draft_run_context_builder import build_draft_run_context_summary
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_from_payload


def test_context_builder_normalizes_full_draft_context() -> None:
    payload = make_payload()
    payload["draftContext"] = make_context()
    request_context = context_from_payload(payload)

    summary = build_draft_run_context_summary(request=request_from_payload(payload), context=request_context)

    assert summary["workItem"]["id"] == "work-item-1"
    assert summary["brief"]["conflict"] == payload["brief"]["conflict"]
    assert summary["brief"]["authorPosition"] == payload["brief"]["authorPosition"]
    assert summary["brief"]["cta"] == payload["brief"]["cta"]
    assert summary["planSlot"]["expectedEffect"] == "Clarify adoption gap"
    assert summary["candidate"]["confidence"] == 88
    assert summary["sourceSignal"]["authorCorrection"] == "Use workflow framing"
    assert summary["topic"]["rules"] == ["Avoid model ranking"]
    assert summary["fabula"]["proofRequirements"] == ["Show pilot evidence"]
    assert summary["publisherRules"]["groups"]["styleVoice"][0]["title"] == "Research voice"
    assert summary["authorPositionEvidence"]["items"][0]["status"] == "confirmed"
    assert summary["missingContext"] == [{"entity": "topic", "id": "missing", "reason": "test"}]


def test_context_builder_keeps_old_minimal_request_compatible() -> None:
    payload = make_payload()
    request = request_from_payload(payload)

    summary = build_draft_run_context_summary(request=request, context=None)

    assert summary["brief"]["title"] == payload["brief"]["title"]
    assert summary["compatibility"]["briefOnly"] is True
    assert summary["missingContext"] == []


def make_context() -> dict:
    return {
        "workItem": {
            "id": "work-item-1",
            "title": "AI-B2B demo",
            "platform": "Telegram",
            "date": "2026-06-20",
            "time": "10:00",
            "topicId": "topic-1",
            "fabulaId": "fabula-1",
            "stage": "brief",
            "status": "inProgress",
        },
        "planSlot": {
            "id": "plan-1",
            "title": "AI-B2B demo",
            "platform": "Telegram",
            "date": "2026-06-20",
            "time": "10:00",
            "approvalStatus": "approved",
            "expectedEffect": "Clarify adoption gap",
            "topicId": "topic-1",
            "fabulaId": "fabula-1",
        },
        "candidate": {
            "id": "candidate-1",
            "title": "AI-B2B demo",
            "thesis": "Demo is not adoption",
            "audience": "AI PM",
            "value": "Explain rollout loop",
            "goal": "Help adoption",
            "platform": "Telegram",
            "confidence": 88,
            "risks": ["Do not sound anti-demo"],
            "evidenceSummary": "Pilots do not become usage",
        },
        "sourceSignal": {
            "id": "signal-1",
            "title": "Pilots stall",
            "source": "Telegram",
            "summary": "Usage stalls after pilot.",
            "rawNote": "Demo magic does not become workflow.",
            "evidence": [{"summary": "pilot evidence"}],
            "authorCorrection": "Use workflow framing",
        },
        "topic": {
            "id": "topic-1",
            "title": "AI product discovery",
            "purpose": "Explain product loops",
            "audienceValue": "Actionable rollout criteria",
            "authorStance": "Workflow before model",
            "rules": ["Avoid model ranking"],
            "forbiddenAngles": ["Model leaderboard"],
            "weightRange": {"min": 20, "max": 30},
        },
        "fabula": {
            "id": "fabula-1",
            "title": "Research note",
            "dramaturgy": "Observation to principle",
            "structure": ["conflict", "principle"],
            "proofRequirements": ["Show pilot evidence"],
            "rules": ["No hype"],
            "weightRange": {"min": 25, "max": 35},
        },
        "publisherRules": [
            {
                "id": "rule-1",
                "group": "styleVoice",
                "title": "Research voice",
                "statement": "Write as product researcher",
                "status": "active",
            }
        ],
        "authorPositionEvidence": [
            {
                "id": "assertion-1",
                "title": "Workflow first",
                "statement": "Adoption starts with workflow",
                "confidence": 0.9,
                "status": "confirmed",
            }
        ],
        "missingContext": [{"entity": "topic", "id": "missing", "reason": "test"}],
    }


def make_payload() -> dict:
    return {
        "brief": {
            "id": "brief-demo",
            "title": "AI-B2B demo",
            "rubric": "AI product discovery",
            "audience": "AI PM",
            "thesis": "Demo magic is not adoption.",
            "conflict": "Demo looks strong, rollout remains weak.",
            "authorPosition": "Workflow before model.",
            "evidence": ["usage after pilot does not grow"],
            "examples": ["no evals"],
            "structure": ["conflict", "position"],
            "cta": "Check product loop.",
            "risks": ["do not sound anti-prototype"],
            "sources": ["author note"],
        },
        "editorialModel": {
            "audience": "AI Product Manager",
            "styleRules": ["research tone"],
            "forbiddenTopics": ["generic AI hype"],
            "goals": ["explain adoption gap"],
        },
    }
