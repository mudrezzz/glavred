"""Owner: drafting.application.workflow

Used by: DraftWorkflow and DraftRun workflow tests.
Does not own: step implementation, provider adapters, API request parsing, SQLite persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from backend.app.domain.draft_run_steps import DraftRunStepKey
from backend.app.drafting.application.workflow.state import DraftWorkflowState


@dataclass(frozen=True)
class DraftWorkflowPhase:
    id: str
    step_keys: tuple[DraftRunStepKey, ...]
    execute: Callable[[DraftWorkflowState], None]


class DraftStepRegistry:
    def __init__(self, phases: Iterable[DraftWorkflowPhase]) -> None:
        self._phases = tuple(phases)
        seen: set[str] = set()
        duplicates: list[str] = []
        for phase in self._phases:
            if phase.id in seen:
                duplicates.append(phase.id)
            seen.add(phase.id)
        if duplicates:
            raise ValueError(f"Duplicate DraftWorkflow phase ids: {', '.join(duplicates)}")

    @property
    def phases(self) -> tuple[DraftWorkflowPhase, ...]:
        return self._phases

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(phase.id for phase in self._phases)
