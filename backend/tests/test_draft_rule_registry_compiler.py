from backend.app.application.draft_quality_gate import DraftQualityGate
from backend.app.application.draft_rule_registry_compiler import DraftRuleRegistryCompiler
from backend.app.application.draft_run_context_builder import build_draft_run_context_summary
from backend.app.application.draft_run_context_payloads import context_from_payload
from backend.app.application.draft_run_payloads import request_from_payload
from backend.app.application.draft_source_ledger_builder import SourceLedgerBuilder
from backend.tests.test_draft_run_context_builder import make_context, make_payload


def test_rule_registry_compiler_builds_stable_validator_bindings_from_quality_context() -> None:
    context_artifact = build_quality_context(make_payload() | {"draftContext": make_context()})

    first = DraftRuleRegistryCompiler().compile(context_artifact).to_payload()
    second = DraftRuleRegistryCompiler().compile(context_artifact).to_payload()
    rules = first["rules"]
    rule_ids = {rule["id"] for rule in rules}

    assert [rule["id"] for rule in rules] == [rule["id"] for rule in second["rules"]]
    assert "contract:thesis" in rule_ids
    assert "ledger:forbidden:risks-are-not-facts" in rule_ids
    assert any(rule["binding"]["validatorType"] == "deterministic" for rule in rules)
    assert any(rule["severity"] == "hard" for rule in rules)
    assert any(rule["claimIds"] for rule in rules)
    assert first["metadata"]["feasibilityStatus"] == "feasible_with_constraints"
    assert first["metadata"]["postContractStatus"] == "created"


def test_rule_registry_compiler_preserves_missing_context_as_warnings() -> None:
    context = make_context()
    context.pop("candidate")
    context["missingContext"].append({"entity": "candidate", "id": "candidate-1", "reason": "missing"})
    context_artifact = build_quality_context(make_payload() | {"draftContext": context})

    snapshot = DraftRuleRegistryCompiler().compile(context_artifact).to_payload()

    assert snapshot["metadata"]["missingContextCount"] == 2
    assert any(warning.get("entity") == "candidate" for warning in snapshot["warnings"])


def build_quality_context(payload: dict) -> dict:
    request = request_from_payload(payload)
    summary = build_draft_run_context_summary(request=request, context=context_from_payload(payload))
    context_artifact = {**summary, "sourceLedger": SourceLedgerBuilder().build(summary, request).to_payload()}
    return DraftQualityGate().evaluate(context_artifact).context_artifact
