"""Owner: drafting.application.context

Used by: DraftRun context access and handle resolution.
Does not own: provider projection policy, prompt construction, budgets, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from backend.app.domain.draft_run import DraftRun


@dataclass(frozen=True)
class DraftRunArtifactIndex:
    run_id: str
    step_payloads: Mapping[str, Mapping[str, Any]]

    @classmethod
    def from_run(cls, run: DraftRun) -> DraftRunArtifactIndex:
        return cls(
            run_id=run.id,
            step_payloads={
                step.key.value: deepcopy(step.artifact_payload)
                for step in run.steps
                if isinstance(step.artifact_payload, dict)
            },
        )

    @classmethod
    def from_snapshot(cls, snapshot: Mapping[str, Any]) -> DraftRunArtifactIndex:
        raw_steps = snapshot.get("steps")
        if not isinstance(raw_steps, Mapping):
            raw_steps = {}
        step_payloads = {
            str(key): deepcopy(value)
            for key, value in raw_steps.items()
            if isinstance(value, Mapping)
        }
        return cls(run_id=str(snapshot.get("runId") or "snapshot"), step_payloads=step_payloads)

    def step_payload(self, step_key: str) -> Mapping[str, Any] | None:
        value = self.step_payloads.get(step_key)
        return value if isinstance(value, Mapping) else None

    def value_at(self, step_key: str, path: tuple[str | int, ...]) -> Any:
        current: Any = self.step_payload(step_key)
        for part in path:
            if isinstance(part, int) and isinstance(current, list) and 0 <= part < len(current):
                current = current[part]
            elif isinstance(part, str) and isinstance(current, Mapping) and part in current:
                current = current[part]
            else:
                return None
        return current


__all__ = ("DraftRunArtifactIndex",)
