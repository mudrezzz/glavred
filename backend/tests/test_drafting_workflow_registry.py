import pytest

from backend.app.domain.draft_run_steps import DraftRunStepKey
from backend.app.drafting.application.workflow.registry import DraftStepRegistry, DraftWorkflowPhase


def test_draft_step_registry_preserves_phase_order() -> None:
    registry = DraftStepRegistry(
        [
            DraftWorkflowPhase("context", (DraftRunStepKey.CONTEXT,), lambda state: None),
            DraftWorkflowPhase("complete", (DraftRunStepKey.COMPLETE,), lambda state: None),
        ]
    )

    assert registry.ids == ("context", "complete")
    assert [phase.step_keys for phase in registry.phases] == [
        (DraftRunStepKey.CONTEXT,),
        (DraftRunStepKey.COMPLETE,),
    ]


def test_draft_step_registry_rejects_duplicate_phase_ids() -> None:
    with pytest.raises(ValueError, match="Duplicate DraftWorkflow phase ids: context"):
        DraftStepRegistry(
            [
                DraftWorkflowPhase("context", (DraftRunStepKey.CONTEXT,), lambda state: None),
                DraftWorkflowPhase("context", (DraftRunStepKey.SOURCE_INTENT,), lambda state: None),
            ]
        )
