from backend.app.drafting.application.revision.draft_revision_loop_config import revision_iteration_limit
from backend.app.drafting.application.artifacts.draft_run_context_builder import build_draft_run_context_summary
from backend.app.drafting.application.artifacts.draft_run_budget_resolver import budget_from_context, resolve_draft_run_budget
from backend.app.drafting.application.evidence.public_evidence_budgeting import budget_public_evidence_tasks, trim_public_evidence_items
from backend.app.drafting.application.evidence.source_research_budgeting import apply_source_research_budget
from backend.app.domain.draft_public_evidence import PublicEvidenceAllowedUse, PublicEvidenceItem
from backend.app.settings import BackendSettings
from backend.app.domain.draft_run_context import DraftRunContext
from backend.tests.test_draft_run_pipeline import make_request


def test_budget_resolver_uses_fabula_depth_and_standard_mode() -> None:
    budget = resolve_draft_run_budget(
        {"fabula": {"researchDepth": "marketResearch"}},
        BackendSettings(DRAFT_RUN_EXECUTION_MODE="standard", DRAFT_REVISION_MAX_ITERATIONS=4),
    )

    assert budget.research_depth.value == "marketResearch"
    assert budget.execution_mode.value == "standard"
    assert budget.caps.max_research_tasks == 12
    assert budget.caps.max_external_claims == 60
    assert budget.caps.max_revision_iterations == 4


def test_invalid_execution_mode_normalizes_to_standard() -> None:
    budget = resolve_draft_run_budget(
        {"fabula": {"researchDepth": "unknown"}},
        BackendSettings(DRAFT_RUN_EXECUTION_MODE="turbo"),
    )

    assert budget.research_depth.value == "standard"
    assert budget.execution_mode.value == "standard"


def test_smoke_mode_applies_hard_caps_and_revision_limit() -> None:
    settings = BackendSettings(DRAFT_RUN_EXECUTION_MODE="smoke", DRAFT_REVISION_MAX_ITERATIONS=5)
    budget = resolve_draft_run_budget({"fabula": {"researchDepth": "deep"}}, settings)

    assert budget.caps.max_search_tasks == 1
    assert budget.caps.max_url_reads == 1
    assert budget.caps.max_search_results_per_task == 2
    assert budget.caps.max_accepted_evidence_items == 3
    assert budget.caps.max_external_claims == 5
    assert budget.caps.max_draft_candidates == 2
    assert revision_iteration_limit(settings) == 1


def test_source_research_budget_caps_tasks_and_records_skips() -> None:
    artifact = {
        "researchPlan": {
            "verificationTasks": [
                {"id": "t1", "kind": "readUrl", "target": "https://a.example"},
                {"id": "t2", "kind": "readUrl", "target": "https://b.example"},
                {"id": "t3", "kind": "findPublicSources", "instruction": "find leaders"},
            ]
        }
    }

    budgeted = apply_source_research_budget(
        artifact_payload=artifact,
        context_artifact={"draftRunBudget": resolve_draft_run_budget({"fabula": {"researchDepth": "light"}}).to_payload()},
    )

    tasks = budgeted["researchPlan"]["verificationTasks"]
    assert [task["id"] for task in tasks] == ["t1", "t3"]
    assert budgeted["budgetTrace"]["budgetSkipped"][0]["id"] == "t2"


def test_public_evidence_budget_caps_retrieval_tasks_and_trims_items() -> None:
    context = {"draftRunBudget": resolve_draft_run_budget({"fabula": {"researchDepth": "light"}}).to_payload()}
    tasks = [
        {"id": "url-1", "kind": "readUrl", "target": "https://one.example"},
        {"id": "url-2", "kind": "readUrl", "target": "https://two.example"},
        {"id": "search-1", "kind": "findPublicSources", "instruction": "find one"},
        {"id": "search-2", "kind": "verifyClaim", "instruction": "verify two"},
    ]

    kept, skipped, warnings, trace = budget_public_evidence_tasks(tasks, context)

    assert [task["id"] for task in kept] == ["url-1", "search-1"]
    assert [attempt.id for attempt in skipped] == ["budget-skip-url-2", "budget-skip-search-2"]
    assert warnings[0].code == "public-evidence-budget-skipped"
    assert trace["usedCounts"]["searchTasks"] == 1

    items = [
        PublicEvidenceItem(f"i-{index}", "a", None, "source", "snippet", "summary", "search", "medium", PublicEvidenceAllowedUse.NEEDS_QUALIFICATION)
        for index in range(6)
    ]
    trimmed, trim_warnings, metadata = trim_public_evidence_items(items, context)
    assert len(trimmed) == 5
    assert trim_warnings[0].code == "public-evidence-budget-trimmed"
    assert len(metadata["trimmedEvidenceItems"]) == 1


def test_budget_from_context_reads_artifact_payload() -> None:
    payload = resolve_draft_run_budget({"fabula": {"researchDepth": "deep"}}, BackendSettings(DRAFT_RUN_EXECUTION_MODE="smoke")).to_payload()

    budget = budget_from_context({"draftRunBudget": payload})

    assert budget.research_depth.value == "deep"
    assert budget.execution_mode.value == "smoke"
    assert budget.caps.max_draft_candidates == 2


def test_context_summary_preserves_fabula_research_depth_for_budget() -> None:
    summary = build_draft_run_context_summary(
        make_request(),
        DraftRunContext(fabula={"id": "fabula-1", "title": "Market research", "researchDepth": "marketResearch"}),
    )

    budget = resolve_draft_run_budget(summary, BackendSettings())

    assert summary["fabula"]["researchDepth"] == "marketResearch"
    assert budget.research_depth.value == "marketResearch"
