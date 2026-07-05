"""Owner: shared.llm_operations

Used by: Shared provider-neutral LLM operation contracts.
Does not own: Prompt text, provider adapters, persistence schemas, or API responses.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from enum import Enum


class LlmOperationAttemptStatus(str, Enum):
    PLANNED = "planned"
    ACCEPTED = "accepted"
    REPAIRED = "repaired"
    BACKUP_ACCEPTED = "backupAccepted"
    FALLBACK = "fallback"
    NOT_RUN = "notRun"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    STALE = "stale"


class LlmOperationResultStatus(str, Enum):
    ACCEPTED = "accepted"
    REPAIRED = "repaired"
    BACKUP_ACCEPTED = "backupAccepted"
    FALLBACK = "fallback"
    NOT_RUN = "notRun"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    STALE = "stale"


class LlmOperationIncidentType(str, Enum):
    PROVIDER_TIMEOUT = "providerTimeout"
    NETWORK_ERROR = "networkError"
    PROVIDER_4XX = "provider4xx"
    PROVIDER_5XX = "provider5xx"
    MALFORMED_JSON = "malformedJson"
    SCHEMA_FAILURE = "schemaFailure"
    PAYLOAD_TOO_LARGE = "payloadTooLarge"
    CONTEXT_OVER_BUDGET = "contextOverBudget"
    DETERMINISTIC_FALLBACK = "deterministicFallback"
    BACKUP_ACCEPTED = "backupAccepted"
    NOT_CONFIGURED = "notConfigured"
    STALE_OPERATION = "staleOperation"
    CANCELLED = "cancelled"
    WORKER_FAILURE = "workerFailure"
    UNKNOWN_PROVIDER_FAILURE = "unknownProviderFailure"


class LlmOperationIncidentSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


JsonOperationAttemptStatus = LlmOperationAttemptStatus
JsonOperationResultStatus = LlmOperationResultStatus
