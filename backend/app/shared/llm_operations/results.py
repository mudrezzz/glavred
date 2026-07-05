"""Owner: shared.llm_operations

Used by: Compatibility imports for provider-neutral LLM attempt/result DTOs.
Does not own: Attempt/result behavior, prompt text, provider adapters, or persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.shared.llm_operations.attempts import (
    JsonOperationAttempt,
    LlmOperationAttempt,
    attempt_ai_run_ids as _attempt_ai_run_ids,
    attempt_incident as _incident_for_attempt,
    attempt_status as _attempt_status,
)
from backend.app.shared.llm_operations.operation_results import (
    JsonLlmOperation,
    JsonOperationEnvelope,
    JsonOperationResult,
    LlmOperationEnvelope,
    LlmOperationResult,
)
from backend.app.shared.llm_operations.operation_result_incidents import result_incident as _result_incident
from backend.app.shared.llm_operations.operation_result_policy import (
    accepted_backup as _accepted_backup,
    backup_incident as _backup_incident,
    last_input_stats as _last_input_stats,
    require_incident as _require_incident,
    result_status as _result_status,
)

__all__ = (
    "JsonLlmOperation",
    "JsonOperationAttempt",
    "JsonOperationEnvelope",
    "JsonOperationResult",
    "LlmOperationAttempt",
    "LlmOperationEnvelope",
    "LlmOperationResult",
    "_accepted_backup",
    "_attempt_ai_run_ids",
    "_attempt_status",
    "_backup_incident",
    "_incident_for_attempt",
    "_last_input_stats",
    "_require_incident",
    "_result_incident",
    "_result_status",
)
