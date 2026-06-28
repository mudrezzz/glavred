from backend.app.application.source_research_plan_sanitizer import sanitize_research_plan_for_source_intent


def test_research_plan_sanitizer_does_not_read_named_source_as_url() -> None:
    plan = {
        "verificationTasks": [{
            "id": "task-1",
            "kind": "readUrl",
            "target": "Ben Thompson Stratechery",
            "instruction": "Read the named source for the product strategy angle.",
            "sourceIntentItemId": "source-intent-1",
        }],
        "warnings": [],
    }
    intent = {"items": [{"id": "source-intent-1", "kind": "namedSource", "instruction": "Ben Thompson Stratechery"}]}

    sanitized = sanitize_research_plan_for_source_intent(plan_payload=plan, source_intent_payload=intent)

    task = sanitized["verificationTasks"][0]
    assert task["kind"] == "findPublicSources"
    assert task["metadata"]["sanitizedFrom"] == "readUrl"
    assert "changed from readUrl" in sanitized["warnings"][0]
