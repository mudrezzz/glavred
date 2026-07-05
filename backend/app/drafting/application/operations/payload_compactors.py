"""Owner: drafting.application.operations

Used by: Compatibility imports for payload budget compactor components.
Does not own: Compaction behavior, payload budget profiles, provider adapters, or prompt text.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from backend.app.drafting.application.operations.payload_artifact_compactors import (
    ContextArtifactCompactor,
    DraftArtifactCompactor,
    MaterialPlanCompactor,
    TraceContextCompactor,
    ValidationReportCompactor,
)
from backend.app.drafting.application.operations.payload_compactor_common import CountAccumulator, PayloadBudgetCounters
from backend.app.drafting.application.operations.payload_compactor_orchestrator import DraftRunPayloadCompactor
from backend.app.drafting.application.operations.payload_evidence_compactors import (
    EvidenceSynthesisCompactor,
    PublicEvidenceCompactor,
    RulePackCompactor,
    SourceLedgerCompactor,
)
from backend.app.drafting.application.operations.payload_record_compactors import (
    CandidatePayloadCompactor,
    EvidenceRecordCompactor,
    SummaryRecordCompactor,
)

__all__ = (
    "CandidatePayloadCompactor",
    "ContextArtifactCompactor",
    "CountAccumulator",
    "DraftArtifactCompactor",
    "DraftRunPayloadCompactor",
    "EvidenceRecordCompactor",
    "EvidenceSynthesisCompactor",
    "MaterialPlanCompactor",
    "PayloadBudgetCounters",
    "PublicEvidenceCompactor",
    "RulePackCompactor",
    "SourceLedgerCompactor",
    "SummaryRecordCompactor",
    "TraceContextCompactor",
    "ValidationReportCompactor",
)
