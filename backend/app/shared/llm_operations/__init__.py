"""Owner: shared.llm_operations

Used by: DraftRun, HITL, future upstream radar/search/signal provider-heavy operations.
Does not own: prompt text, provider adapters, persistence schemas, API response contracts.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.shared.llm_operations.contracts import (
    JsonLlmOperation,
    JsonOperationAttempt,
    JsonOperationAttemptStatus,
    JsonOperationEnvelope,
    JsonOperationResult,
    JsonOperationResultStatus,
    LlmOperationAttempt,
    LlmOperationAttemptStatus,
    LlmOperationEnvelope,
    LlmOperationEnvelopeFactory,
    LlmOperationIncident,
    LlmOperationIncidentSeverity,
    LlmOperationIncidentType,
    LlmOperationInputStats,
    LlmOperationResult,
    LlmOperationResultStatus,
    LlmOperationRetryPolicy,
    LlmOperationTimeoutProfile,
    build_operation_envelope,
    incident_from_safe_error,
)
from backend.app.shared.llm_operations.inventory import (
    CURRENT_LLM_OPERATION_INVENTORY,
    LlmOperationInventoryEntry,
    operation_inventory_payload,
)

__all__ = [
    "JsonLlmOperation",
    "JsonOperationAttempt",
    "JsonOperationAttemptStatus",
    "JsonOperationEnvelope",
    "JsonOperationResult",
    "JsonOperationResultStatus",
    "LlmOperationAttempt",
    "LlmOperationAttemptStatus",
    "LlmOperationEnvelope",
    "LlmOperationEnvelopeFactory",
    "LlmOperationIncident",
    "LlmOperationIncidentSeverity",
    "LlmOperationIncidentType",
    "LlmOperationInputStats",
    "LlmOperationResult",
    "LlmOperationResultStatus",
    "LlmOperationRetryPolicy",
    "LlmOperationTimeoutProfile",
    "build_operation_envelope",
    "incident_from_safe_error",
    "CURRENT_LLM_OPERATION_INVENTORY",
    "LlmOperationInventoryEntry",
    "operation_inventory_payload",
]
