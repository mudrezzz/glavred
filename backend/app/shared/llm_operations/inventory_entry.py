"""Owner: shared.llm_operations

Used by: Provider-heavy operation inventory data and architecture smoke.
Does not own: Provider execution, prompt text, operation routing, or roadmap status changes.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LlmOperationInventoryEntry:
    operation_id: str
    owner: str
    current_module: str
    operation_kind: str
    status: str
    reason_not_migrated: str
    removal_slice: str
    expected_incident_coverage: tuple[str, ...]
    payload_budget_status: str = "debtAllowlisted"
    budget_policy_id: str = ""
    reason_not_budgeted: str = ""
    payload_budget_removal_slice: str = ""

    def to_payload(self) -> dict[str, object]:
        return {
            "operationId": self.operation_id,
            "owner": self.owner,
            "currentModule": self.current_module,
            "operationKind": self.operation_kind,
            "status": self.status,
            "reasonNotMigrated": self.reason_not_migrated,
            "removalSlice": self.removal_slice,
            "expectedIncidentCoverage": list(self.expected_incident_coverage),
            "payloadBudgetStatus": self.payload_budget_status,
            "budgetPolicyId": self.budget_policy_id or self.operation_id,
            "reasonNotBudgeted": self.reason_not_budgeted or self.reason_not_migrated,
            "payloadBudgetRemovalSlice": self.payload_budget_removal_slice or self.removal_slice,
        }