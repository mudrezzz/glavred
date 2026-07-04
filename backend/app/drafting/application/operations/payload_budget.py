"""Owner: drafting.application.operations

Used by: legacy imports while DraftRun payload budget modules are role-owned.
Does not own: compacting rules, profile definitions, semantic contracts, incidents.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md

Compatibility surface for PayloadBudgetProfile, SemanticInputContract,
PayloadBudgetResult, DraftRunPayloadBudgetPolicy, contextOverBudget,
payloadTooLarge, promptCharEstimate, and approxTokenEstimate trace governance.
"""

from backend.app.drafting.application.operations.payload_budget_contracts import (
    PayloadBudgetProfile,
    PayloadBudgetResult,
    PayloadCompactionResult,
    SemanticInputContract,
)
from backend.app.drafting.application.operations.payload_budget_policy import (
    CONTEXT_OVER_BUDGET_INCIDENT,
    HARD_PAYLOAD_CHAR_CAP_MULTIPLIER,
    PAYLOAD_TOO_LARGE_INCIDENT,
    DraftRunPayloadBudgetPolicy,
)
from backend.app.drafting.application.operations.payload_budget_profiles import (
    DEFAULT_PROFILES,
    EXECUTION_MODES,
    OPERATION_FAMILIES,
    PayloadBudgetProfileRegistry,
    build_profile,
)
from backend.app.drafting.application.operations.payload_semantic_contracts import (
    SEMANTIC_CONTRACTS,
    SemanticInputContractRegistry,
)

__all__ = [
    "CONTEXT_OVER_BUDGET_INCIDENT",
    "DEFAULT_PROFILES",
    "EXECUTION_MODES",
    "HARD_PAYLOAD_CHAR_CAP_MULTIPLIER",
    "OPERATION_FAMILIES",
    "PAYLOAD_TOO_LARGE_INCIDENT",
    "DraftRunPayloadBudgetPolicy",
    "PayloadBudgetProfile",
    "PayloadBudgetProfileRegistry",
    "PayloadBudgetResult",
    "PayloadCompactionResult",
    "SEMANTIC_CONTRACTS",
    "SemanticInputContract",
    "SemanticInputContractRegistry",
    "build_profile",
]
