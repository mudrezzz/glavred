"""Owner: drafting.application.workflow

Used by: DraftWorkflow phases during behavior-preserving DraftRun orchestration.
Does not own: provider adapters, API request parsing, SQLite persistence, step business logic.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.app.application.draft_run_progress import DraftRunProgress
from backend.app.domain.draft_generation import DraftGenerationRequest, GeneratedDraft
from backend.app.domain.draft_run import DraftRun


@dataclass
class DraftWorkflowState:
    run: DraftRun
    request: DraftGenerationRequest
    progress: DraftRunProgress
    context_summary: dict[str, Any] = field(default_factory=dict)
    context_artifact: dict[str, Any] = field(default_factory=dict)
    rule_pack: dict[str, Any] = field(default_factory=dict)
    material_plan: dict[str, Any] = field(default_factory=dict)
    draft_strategy: dict[str, Any] = field(default_factory=dict)
    rhetorical_plans: dict[str, Any] = field(default_factory=dict)
    draft_artifact: dict[str, Any] = field(default_factory=dict)
    validation_artifact: dict[str, Any] = field(default_factory=dict)
    final_draft: GeneratedDraft | None = None
    source_result: Any | None = None
    draft_result: Any | None = None
    validation_result: Any | None = None
    stop_requested: bool = False
    stop_reason: str | None = None

    @property
    def run_id(self) -> str:
        return self.run.id

    def stop(self, reason: str) -> None:
        self.stop_requested = True
        self.stop_reason = reason
