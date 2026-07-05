"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from collections.abc import Callable
from typing import Any, TypeVar

from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink

T = TypeVar("T")


class ValidationOperationFailureMapper:
    def safe_call(
        self,
        *,
        progress: DraftRunStepOperationSink | None,
        operation_id: str,
        fallback: Callable[[str], T],
        call: Callable[[], T],
    ) -> T:
        try:
            return call()
        except Exception as exc:
            error = _safe_error(exc)
            if progress:
                progress.fail_operation(operation_id, error)
            return fallback(error)

    def failed_revision_result(self, error: str) -> dict[str, Any]:
        return {"status": "failed", "reason": "operation-failed", "error": error, "attempts": [], "aiRunIds": []}

    def failed_pairwise_result(self, error: str) -> dict[str, Any]:
        return {
            "status": "failed",
            "decision": {"winnerCandidateId": None, "reason": error, "source": "operationFailed"},
            "comparisons": [],
            "attempts": [],
            "aiRunIds": [],
            "error": error,
        }


def _safe_error(error: Exception) -> str:
    return f"{error.__class__.__name__}: {' '.join(str(error).split())[:240]}"
