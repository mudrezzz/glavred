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
        must_have=("dossierId", "postContract", "evidence"),
        should_have=("rules", "repairContext"),
        never_send_to_provider=("sourceLedger", "rulePack", "articleDossier", "contextPacks", "operationEnvelope", "payloadBudget", "runtimeBudget"),
    ),
    "draftStrategy": SemanticInputContract(
        must_have=("dossierId", "postContract", "materialPlan"),
        should_have=("evidence", "rules"),
        never_send_to_provider=("sourceLedger", "rulePack", "articleDossier", "contextPacks", "operationEnvelope", "payloadBudget", "runtimeBudget"),
    ),
    "rhetoricalPlans": SemanticInputContract(
        must_have=("dossierId", "postContract", "materialPlan", "draftStrategy"),
        should_have=("evidence", "rules", "repairContext"),
        never_send_to_provider=("sourceLedger", "rulePack", "articleDossier", "contextPacks", "operationEnvelope", "payloadBudget", "runtimeBudget"),
    ),
    "draftCandidate": SemanticInputContract(
        must_have=("dossierId", "postContract", "planning", "rhetoricalPlan", "evidence"),
        should_have=("claims", "rules", "repairContext"),
        never_send_to_provider=("sourceLedger", "rulePack", "articleDossier", "contextPacks", "candidatePool", "validationReport", "operationEnvelope", "payloadBudget", "runtimeBudget"),
    ),
    "llmValidation": SemanticInputContract(
        must_have=("dossierId", "candidate", "postContract", "validationIssues"),
        should_have=("evidence", "rules", "repairContext"),
        diagnostic_only=("fullValidationTrace",),
        never_send_to_provider=("sourceLedger", "rulePack", "materialPlan", "candidatePool", "validationReport", "contextPacks", "operationEnvelope", "payloadBudget", "runtimeBudget"),
    ),
    "editorialCritique": SemanticInputContract(
        must_have=("candidate", "context_artifact", "rule_pack"),
        diagnostic_only=("draft_artifact",),
        never_send_to_provider=("fullCandidatePool",),
    ),
    "pairwiseRanking": SemanticInputContract(
        must_have=("dossierId", "candidates", "validationIssues", "editorialDimensions"),
        should_have=("postContract", "evidence", "selectionConstraints", "repairContext"),
        never_send_to_provider=("sourceLedger", "rulePack", "materialPlan", "candidatePool", "validationReport", "contextPacks", "operationEnvelope", "payloadBudget", "runtimeBudget"),
    ),
    "directedRevision": SemanticInputContract(
        must_have=("dossierId", "candidate", "revisionInstruction", "postContract"),
        should_have=("validationIssues", "evidence", "rules", "antiRegressionConstraints", "repairContext"),
        diagnostic_only=("fullRevisionTrace",),
        never_send_to_provider=("sourceLedger", "rulePack", "materialPlan", "candidatePool", "validationReport", "contextPacks", "operationEnvelope", "payloadBudget", "runtimeBudget"),
    ),
    "finalQualityReviewRepair": SemanticInputContract(
        must_have=("dossierId", "candidate", "finalQualityContract", "deterministicGate"),
        should_have=("postContract", "validationIssues", "evidence", "repairHistory", "finalQualityIssues", "repairContext"),
        never_send_to_provider=("sourceLedger", "rulePack", "materialPlan", "candidatePool", "validationReport", "finalQualityTrace", "contextPacks", "operationEnvelope", "payloadBudget", "runtimeBudget"),
    ),
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
    "alternativeAngleRoute": SemanticInputContract(
        must_have=("dossierId", "candidates", "critiqueSignals", "postContract"),
        should_have=("validationIssues", "rejectedMoves", "evidence", "claims", "rules", "repairContext"),
        never_send_to_provider=("sourceLedger", "rulePack", "articleDossier", "contextPacks", "candidatePool", "validationReport", "operationEnvelope", "payloadBudget", "runtimeBudget"),
    ),
    "alternativeAngleCandidate": SemanticInputContract(
        must_have=("dossierId", "postContract", "planning", "alternativeRoute", "evidence"),
        should_have=("claims", "rules", "critiqueSignals", "repairContext"),
        never_send_to_provider=("sourceLedger", "rulePack", "articleDossier", "contextPacks", "candidatePool", "validationReport", "operationEnvelope", "payloadBudget", "runtimeBudget"),
    ),
    "publicEvidenceSearch": SemanticInputContract(must_have=("research_task",), never_send_to_provider=("fullWorkspace",)),
    "publicEvidenceRead": SemanticInputContract(must_have=("url",), never_send_to_provider=("fullWorkspace",)),
}
