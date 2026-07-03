from backend.app.application.draft_run_pipeline import DraftRunPipeline as LegacyDraftRunPipeline
from backend.app.application.draft_run_service import DraftRunService as LegacyDraftRunService
from backend.app.domain.draft_run import DraftRun as LegacyDraftRun
from backend.app.domain.draft_run import DraftRunStatus as LegacyDraftRunStatus
from backend.app.domain.draft_run_steps import DraftRunStepKey as LegacyDraftRunStepKey
from backend.app.domain.draft_run_steps import DraftRunStepStatus as LegacyDraftRunStepStatus
from backend.app.drafting.application.workflow.legacy_pipeline import DraftRunPipeline, DraftRunService
from backend.app.drafting.domain.legacy_run import (
    DraftRun,
    DraftRunStatus,
    DraftRunStepKey,
    DraftRunStepStatus,
)


def test_drafting_workflow_shim_reexports_legacy_entrypoints() -> None:
    assert DraftRunPipeline is LegacyDraftRunPipeline
    assert DraftRunService is LegacyDraftRunService


def test_drafting_domain_shim_reexports_legacy_run_contracts() -> None:
    assert DraftRun is LegacyDraftRun
    assert DraftRunStatus is LegacyDraftRunStatus
    assert DraftRunStepKey is LegacyDraftRunStepKey
    assert DraftRunStepStatus is LegacyDraftRunStepStatus
