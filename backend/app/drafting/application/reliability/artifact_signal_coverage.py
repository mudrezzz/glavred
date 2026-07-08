"""Owner: drafting.application.reliability

Used by: DraftRun reliability signal coverage reports.
Does not own: child AiRun coverage, operation-envelope rules, budget rules, or remediation policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_AS_IS.md
"""

from __future__ import annotations

from typing import Any

from backend.app.drafting.application.reliability.budget_signal_coverage import BudgetSignalCoverageComponent
from backend.app.drafting.application.reliability.contracts import ReliabilitySignalCoverageRecord
from backend.app.drafting.application.reliability.operation_signal_coverage import OperationSignalCoverageComponent
from backend.app.drafting.application.reliability.signal_coverage_utils import _dedupe_records, _dict, _walk_dicts


class ArtifactSignalCoverageComponent:
    """Audits structured signals stored inside DraftRun step artifacts."""

    def __init__(
        self,
        *,
        operation_signals: OperationSignalCoverageComponent | None = None,
        budget_signals: BudgetSignalCoverageComponent | None = None,
    ) -> None:
        self._operation_signals = operation_signals or OperationSignalCoverageComponent()
        self._budget_signals = budget_signals or BudgetSignalCoverageComponent()

    def records(
        self,
        *,
        run_id: str,
        step_key: str,
        artifact: dict[str, Any],
        operation_ids: set[str],
    ) -> list[ReliabilitySignalCoverageRecord]:
        records: list[ReliabilitySignalCoverageRecord] = []
        for path, payload in _walk_dicts(artifact):
            operation_id = self._operation_id(step_key, path, payload)
            records.extend(
                self._operation_signals.records(
                    run_id=run_id,
                    step_key=step_key,
                    path=path,
                    payload=payload,
                    operation_id=operation_id,
                    operation_ids=operation_ids,
                )
            )
            records.extend(
                self._budget_signals.records(
                    run_id=run_id,
                    step_key=step_key,
                    path=path,
                    payload=payload,
                    operation_id=operation_id,
                    operation_ids=operation_ids,
                )
            )
        return _dedupe_records(records)

    def _operation_id(self, step_key: str, path: str, payload: dict[str, Any]) -> str:
        envelope = _dict(payload.get("operationEnvelope"))
        return str(envelope.get("operationId") or payload.get("operationId") or path or step_key)
