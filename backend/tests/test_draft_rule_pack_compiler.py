from backend.app.application.draft_rule_pack_compiler import DraftRulePackCompiler
from backend.app.application.draft_run_context_builder import build_draft_run_context_summary
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_from_payload
from backend.tests.test_draft_run_context_builder import make_context, make_payload


def test_rule_pack_compiler_uses_full_context_categories() -> None:
    payload = make_payload()
    context = make_context()
    context["publisherRules"].append(
        {
            "id": "rule-2",
            "group": "forbiddenTopic",
            "title": "No hype",
            "statement": "Do not sell generic AI magic.",
            "status": "active",
        }
    )
    payload["draftContext"] = context

    pack = compile_payload(payload)

    assert pack["metadata"]["version"] == "rule-pack-v1"
    assert pack["metadata"]["registryVersion"] == "rule-registry-v2"
    assert pack["metadata"]["missingContextCount"] == 1
    assert pack["warnings"][0]["entity"] == "topic"
    assert pack["ruleRegistrySnapshot"]["metadata"]["ruleCount"] >= 10
    assert pack["draftIntent"]["thesis"] == "Demo magic is not adoption."
    assert pack["draftIntent"]["conflict"] == "Demo looks strong, rollout remains weak."
    assert has_source(pack["softConstraints"], "publisherRules.styleVoice")
    assert has_source(pack["hardConstraints"], "publisherRules.forbiddenTopic")
    assert has_source(pack["hardConstraints"], "candidate")
    assert has_source(pack["evidenceRequirements"], "sourceSignal")
    assert has_source(pack["evidenceRequirements"], "fabula")
    assert has_source(pack["dramaturgyRequirements"], "fabula")
    assert has_source(pack["topicFitRequirements"], "topic")
    assert has_source(pack["forbiddenMoves"], "candidate")
    assert len(pack["qualityRubric"]) == 4


def test_rule_pack_compiler_keeps_brief_only_request_compatible() -> None:
    pack = compile_payload(make_payload())

    assert pack["metadata"]["briefOnly"] is True
    assert pack["draftIntent"]["title"] == "AI-B2B demo"
    assert has_source(pack["softConstraints"], "publisherRules.styleRules")
    assert has_source(pack["hardConstraints"], "publisherRules.forbiddenTopics")
    assert has_source(pack["softConstraints"], "publisherRules.goals")
    assert pack["warnings"] == []
    assert pack["ruleRegistrySnapshot"]["metadata"]["briefOnly"] is True
    assert len(pack["qualityRubric"]) == 4


def compile_payload(payload: dict) -> dict:
    summary = build_draft_run_context_summary(
        request=request_from_payload(payload),
        context=context_from_payload(payload),
    )
    return DraftRulePackCompiler().compile(summary).to_payload()


def has_source(items: list[dict], source: str) -> bool:
    return any(item["source"] == source for item in items)
