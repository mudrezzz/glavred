"""Owner: shared.llm_operations

Used by: architecture smoke, DraftRun diagnostics, and migration planning for provider-heavy operations.
Does not own: provider execution, prompt text, operation routing, or roadmap status changes.
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


CURRENT_LLM_OPERATION_INVENTORY: tuple[LlmOperationInventoryEntry, ...] = (
    LlmOperationInventoryEntry(
        operation_id="sourceIntentAndResearchPlan",
        owner="backend.app.drafting.application.evidence.source_research_plan_service",
        current_module="backend/app/drafting/application/evidence/source_research_plan_service.py",
        operation_kind="sourceResearchPlanning",
        status="legacyAllowlisted",
        reason_not_migrated="bounded package migration is complete but the operation still uses legacy fallback trace shape",
        removal_slice="2.17.4.6.0.6",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "unknownProviderFailure"),
    ),
    LlmOperationInventoryEntry(
        operation_id="publicEvidenceSearch",
        owner="backend.app.drafting.application.evidence.openrouter_public_search_service",
        current_module="backend/app/drafting/application/evidence/openrouter_public_search_service.py",
        operation_kind="publicEvidenceSearch",
        status="legacyAllowlisted",
        reason_not_migrated="upstream provider context is scheduled after DraftRun envelope baseline",
        removal_slice="2.17.4.6.0.3.5",
        expected_incident_coverage=("providerTimeout", "networkError", "provider4xx", "provider5xx", "notConfigured"),
    ),
    LlmOperationInventoryEntry(
        operation_id="publicEvidenceRead",
        owner="backend.app.infrastructure.public_url_reader",
        current_module="backend/app/infrastructure/public_url_reader.py",
        operation_kind="publicEvidenceRead",
        status="legacyAllowlisted",
        reason_not_migrated="URL read errors are infrastructure-shaped and need upstream context envelope",
        removal_slice="2.17.4.6.0.3.5",
        expected_incident_coverage=("networkError", "providerTimeout", "payloadTooLarge", "workerFailure"),
    ),
    LlmOperationInventoryEntry(
        operation_id="evidenceSynthesis",
        owner="backend.app.drafting.application.evidence.external_evidence_synthesis_service",
        current_module="backend/app/drafting/application/evidence/external_evidence_synthesis_service.py",
        operation_kind="evidenceSynthesis",
        status="legacyAllowlisted",
        reason_not_migrated="bounded package migration is complete but synthesis still needs full shared envelope migration",
        removal_slice="2.17.4.6.0.6",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "unknownProviderFailure"),
    ),
    LlmOperationInventoryEntry(
        operation_id="evidenceInterpretation",
        owner="backend.app.drafting.application.evidence.evidence_interpretation_service",
        current_module="backend/app/drafting/application/evidence/evidence_interpretation_service.py",
        operation_kind="evidenceInterpretation",
        status="migrated",
        reason_not_migrated="",
        removal_slice="",
        expected_incident_coverage=("providerTimeout", "deterministicFallback", "backupAccepted", "schemaFailure", "notConfigured"),
        payload_budget_status="enforced",
        budget_policy_id="evidenceInterpretation",
    ),
    LlmOperationInventoryEntry(
        operation_id="materialPlan",
        owner="backend.app.drafting.application.planning.material_plan_retry_orchestrator",
        current_module="backend/app/drafting/application/planning/material_plan_retry_orchestrator.py",
        operation_kind="materialPlanning",
        status="legacyAllowlisted",
        reason_not_migrated="bounded package migration is complete but material plan still needs full shared envelope migration",
        removal_slice="2.17.4.6.0.6",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="draftStrategy",
        owner="backend.app.drafting.application.planning.draft_strategy_service",
        current_module="backend/app/drafting/application/planning/draft_strategy_service.py",
        operation_kind="draftStrategy",
        status="legacyAllowlisted",
        reason_not_migrated="bounded package migration is complete but strategy still needs full shared envelope migration",
        removal_slice="2.17.4.6.0.6",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="rhetoricalPlans",
        owner="backend.app.drafting.application.planning.draft_rhetorical_plan_retry",
        current_module="backend/app/drafting/application/planning/draft_rhetorical_plan_retry.py",
        operation_kind="rhetoricalPlanning",
        status="legacyAllowlisted",
        reason_not_migrated="bounded package migration is complete but rhetorical plans still need full shared envelope migration",
        removal_slice="2.17.4.6.0.6",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="draftCandidate",
        owner="backend.app.drafting.application.generation.draft_candidate_provider_service",
        current_module="backend/app/drafting/application/generation/draft_candidate_provider_service.py",
        operation_kind="draftCandidateGeneration",
        status="legacyAllowlisted",
        reason_not_migrated="bounded package migration is complete but candidate generation still needs full shared envelope migration",
        removal_slice="2.17.4.6.0.6",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="llmValidation",
        owner="backend.app.drafting.application.validation.draft_llm_validation_service",
        current_module="backend/app/drafting/application/validation/draft_llm_validation_service.py",
        operation_kind="llmValidation",
        status="legacyAllowlisted",
        reason_not_migrated="bounded package migration is complete but LLM validation still needs full shared envelope migration",
        removal_slice="2.17.4.6.0.6",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="editorialCritique",
        owner="backend.app.drafting.application.validation.draft_editorial_critique_service",
        current_module="backend/app/drafting/application/validation/draft_editorial_critique_service.py",
        operation_kind="reportOnlyValidator",
        status="migrated",
        reason_not_migrated="",
        removal_slice="",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
        payload_budget_status="enforced",
        budget_policy_id="editorialCritique",
    ),
    LlmOperationInventoryEntry(
        operation_id="alternativeAngleRoute",
        owner="backend.app.drafting.application.validation.draft_alternative_angle_route_service",
        current_module="backend/app/drafting/application/validation/draft_alternative_angle_route_service.py",
        operation_kind="alternativeAngleRoute",
        status="legacyAllowlisted",
        reason_not_migrated="bounded package migration is complete but alternative-angle operation envelope migration remains follow-up",
        removal_slice="2.17.4.6.0.6",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="alternativeAngleCandidate",
        owner="backend.app.drafting.application.generation.draft_alternative_angle_candidate_service",
        current_module="backend/app/drafting/application/generation/draft_alternative_angle_candidate_service.py",
        operation_kind="alternativeAngleCandidate",
        status="legacyAllowlisted",
        reason_not_migrated="bounded package migration is complete but alternative-angle operation envelope migration remains follow-up",
        removal_slice="2.17.4.6.0.6",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="pairwiseRanking",
        owner="backend.app.drafting.application.revision.draft_pairwise_ranking_service",
        current_module="backend/app/drafting/application/revision/draft_pairwise_ranking_service.py",
        operation_kind="pairwiseRanking",
        status="legacyAllowlisted",
        reason_not_migrated="bounded package migration is complete but pairwise ranking still needs full shared envelope migration",
        removal_slice="2.17.4.6.0.6",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="directedRevision",
        owner="backend.app.drafting.application.revision.draft_directed_revision_service",
        current_module="backend/app/drafting/application/revision/draft_directed_revision_service.py",
        operation_kind="writerRevision",
        status="migrated",
        reason_not_migrated="",
        removal_slice="",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
        payload_budget_status="enforced",
        budget_policy_id="directedRevision",
    ),
    LlmOperationInventoryEntry(
        operation_id="finalQualityReviewRepair",
        owner="backend.app.drafting.application.final_quality.draft_final_quality_review_service",
        current_module="backend/app/drafting/application/final_quality/draft_final_quality_review_service.py",
        operation_kind="finalQualityReviewRepair",
        status="legacyAllowlisted",
        reason_not_migrated="bounded package migration is complete but final-quality repair still needs full shared envelope migration",
        removal_slice="2.17.4.6.0.6",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="humanCommentRevision",
        owner="backend.app.drafting.application.hitl.draft_human_comment_revision_service",
        current_module="backend/app/drafting/application/hitl/draft_human_comment_revision_service.py",
        operation_kind="hitlWriterRevision",
        status="migrated",
        reason_not_migrated="",
        removal_slice="",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
        payload_budget_status="enforced",
        budget_policy_id="humanCommentRevision",
    ),
    LlmOperationInventoryEntry(
        operation_id="humanCommentRevisionQualityCheck",
        owner="backend.app.drafting.application.hitl.draft_human_comment_quality_service",
        current_module="backend/app/drafting/application/hitl/draft_human_comment_quality_service.py",
        operation_kind="hitlQualityCheck",
        status="migrated",
        reason_not_migrated="",
        removal_slice="",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
        payload_budget_status="enforced",
        budget_policy_id="humanCommentRevisionQualityCheck",
    ),
)


def operation_inventory_payload() -> list[dict[str, object]]:
    return [entry.to_payload() for entry in CURRENT_LLM_OPERATION_INVENTORY]
