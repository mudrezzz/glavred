"""Owner: drafting.application.operations

Used by: DraftRun payload budget policy to classify provider input fields.
Does not own: compacting implementation, prompt wording, trace persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Mapping

from backend.app.drafting.application.operations.payload_budget_contracts import SemanticInputContract


class SemanticInputContractRegistry:
    def __init__(self, contracts: Mapping[str, SemanticInputContract] | None = None) -> None:
        self._contracts = dict(contracts or SEMANTIC_CONTRACTS)

    def contract_for(self, operation_id: str) -> SemanticInputContract:
        return self._contracts[operation_id]


SEMANTIC_CONTRACTS: dict[str, SemanticInputContract] = {
    "sourceIntentAndResearchPlan": SemanticInputContract(
        must_have=("context_artifact", "source_intent"),
        should_have=("draftRunBudget",),
        diagnostic_only=("rawWorkspace",),
        never_send_to_provider=("workspaceSnapshot", "fullWorkspace"),
    ),
    "evidenceSynthesis": SemanticInputContract(
        must_have=("context_artifact", "public_evidence"),
        should_have=("sourceLedger",),
        never_send_to_provider=("fullWorkspace",),
    ),
    "evidenceInterpretation": SemanticInputContract(
        must_have=("context_artifact", "rule_pack"),
        should_have=("context_pack",),
        diagnostic_only=("rawRuleRegistry",),
        never_send_to_provider=("fullWorkspace",),
    ),
    "materialPlan": SemanticInputContract(
        must_have=("context_artifact", "rule_pack"),
        should_have=("material_plan",),
        never_send_to_provider=("sourceLedgerFull", "ruleRegistryFull"),
    ),
    "draftStrategy": SemanticInputContract(must_have=("context_artifact", "material_plan", "rule_pack")),
    "rhetoricalPlans": SemanticInputContract(must_have=("draft_strategy", "material_plan", "rule_pack")),
    "draftCandidate": SemanticInputContract(must_have=("direction", "context_summary", "rule_pack", "material_plan", "draft_strategy")),
    "llmValidation": SemanticInputContract(must_have=("candidate", "context_artifact", "rule_pack"), diagnostic_only=("fullValidationTrace",)),
    "editorialCritique": SemanticInputContract(
        must_have=("candidate", "context_artifact", "rule_pack"),
        diagnostic_only=("draft_artifact",),
        never_send_to_provider=("fullCandidatePool",),
    ),
    "pairwiseRanking": SemanticInputContract(must_have=("candidates", "validation_report", "context_artifact", "rule_pack")),
    "directedRevision": SemanticInputContract(
        must_have=("candidate", "instruction", "context_artifact", "rule_pack", "material_plan"),
        diagnostic_only=("fullRevisionTrace",),
    ),
    "finalQualityReviewRepair": SemanticInputContract(must_have=("candidate", "validation_report", "context_artifact", "rule_pack", "material_plan")),
    "humanCommentRevision": SemanticInputContract(
        must_have=("current_version", "editor_comment", "trace_context"),
        diagnostic_only=("fullDraftRun",),
        never_send_to_provider=("rawDraftRun",),
    ),
    "humanCommentRevisionQualityCheck": SemanticInputContract(
        must_have=("base_version", "revised_version", "editor_comment", "trace_context"),
        diagnostic_only=("fullDraftRun",),
        never_send_to_provider=("rawDraftRun",),
    ),
    "alternativeAngleRoute": SemanticInputContract(must_have=("validation_report", "context_artifact")),
    "alternativeAngleCandidate": SemanticInputContract(must_have=("direction", "context_artifact", "rule_pack", "material_plan")),
    "publicEvidenceSearch": SemanticInputContract(must_have=("research_task",), never_send_to_provider=("fullWorkspace",)),
    "publicEvidenceRead": SemanticInputContract(must_have=("url",), never_send_to_provider=("fullWorkspace",)),
}
