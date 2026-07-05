"""Owner: shared.llm_operations

Used by: Compatibility imports for shared LLM operation contracts.
Does not own: Prompt text, provider adapters, persistence schemas, or API response contracts.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.shared.llm_operations.envelope_factory import LlmOperationEnvelopeFactory, build_operation_envelope
from backend.app.shared.llm_operations.incidents import LlmOperationIncident, incident_from_safe_error, redact_safe_error
from backend.app.shared.llm_operations.results import (
    JsonLlmOperation,
    JsonOperationAttempt,
    JsonOperationEnvelope,
    JsonOperationResult,
    LlmOperationAttempt,
    LlmOperationEnvelope,
    LlmOperationResult,
)
from backend.app.shared.llm_operations.stats import (
    LlmOperationInputStats,
    LlmOperationRetryPolicy,
    LlmOperationTimeoutProfile,
)
from backend.app.shared.llm_operations.statuses import (
    JsonOperationAttemptStatus,
    JsonOperationResultStatus,
    LlmOperationAttemptStatus,
    LlmOperationIncidentSeverity,
    LlmOperationIncidentType,
    LlmOperationResultStatus,
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
    "redact_safe_error",
]
