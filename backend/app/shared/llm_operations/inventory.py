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
        owner="backend.app.application.source_research_plan_service",
        current_module="backend/app/application/source_research_plan_service.py",
        operation_kind="sourceResearchPlanning",
        status="legacyAllowlisted",
        reason_not_migrated="legacy planning operation keeps local fallback trace until planning-provider split",
        removal_slice="2.17.4.6.0.3.4",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "unknownProviderFailure"),
    ),
    LlmOperationInventoryEntry(
        operation_id="publicEvidenceSearch",
        owner="backend.app.application.openrouter_public_search_service",
        current_module="backend/app/application/openrouter_public_search_service.py",
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
        owner="backend.app.application.external_evidence_synthesis_service",
        current_module="backend/app/application/external_evidence_synthesis_service.py",
        operation_kind="evidenceSynthesis",
        status="legacyAllowlisted",
        reason_not_migrated="kept for follow-up migration after interpretation envelope proves trace shape",
        removal_slice="2.17.4.6.0.3.4",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "unknownProviderFailure"),
    ),
    LlmOperationInventoryEntry(
        operation_id="evidenceInterpretation",
        owner="backend.app.application.evidence_interpretation_service",
        current_module="backend/app/application/evidence_interpretation_service.py",
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
        owner="backend.app.application.material_plan_retry_orchestrator",
        current_module="backend/app/application/material_plan_retry_orchestrator.py",
        operation_kind="materialPlanning",
        status="legacyAllowlisted",
        reason_not_migrated="large legacy retry orchestrator requires a dedicated adapter-backed migration",
        removal_slice="2.17.4.6.0.3.4",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="draftStrategy",
        owner="backend.app.application.draft_strategy_service",
        current_module="backend/app/application/draft_strategy_service.py",
        operation_kind="draftStrategy",
        status="legacyAllowlisted",
        reason_not_migrated="planning provider migration stays outside representative slice",
        removal_slice="2.17.4.6.0.3.4",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="rhetoricalPlans",
        owner="backend.app.application.draft_rhetorical_plan_retry",
        current_module="backend/app/application/draft_rhetorical_plan_retry.py",
        operation_kind="rhetoricalPlanning",
        status="legacyAllowlisted",
        reason_not_migrated="legacy retry object remains until planning-family migration",
        removal_slice="2.17.4.6.0.3.4",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="draftCandidate",
        owner="backend.app.application.draft_candidate_provider_service",
        current_module="backend/app/application/draft_candidate_provider_service.py",
        operation_kind="draftCandidateGeneration",
        status="legacyAllowlisted",
        reason_not_migrated="candidate generation has candidate-selection coupling and needs a separate adapter migration",
        removal_slice="2.17.4.6.0.3.6",
        expected_incident_coverage=("deterministicFallback", "malformedJson", "schemaFailure", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="llmValidation",
        owner="backend.app.application.draft_llm_validation_service",
        current_module="backend/app/application/draft_llm_validation_service.py",
        operation_kind="llmValidation",
        status="legacyAllowlisted",
        reason_not_migrated="validation-family migration follows report-only editorial critique representative",
        removal_slice="2.17.4.6.0.3.6",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="editorialCritique",
        owner="backend.app.application.draft_editorial_critique_service",
        current_module="backend/app/application/draft_editorial_critique_service.py",
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
        owner="backend.app.application.draft_alternative_angle_route_service",
        current_module="backend/app/application/draft_alternative_angle_route_service.py",
        operation_kind="alternativeAngleRoute",
        status="legacyAllowlisted",
        reason_not_migrated="alternative-angle tournament gets migrated after representative validator/writer pair",
        removal_slice="2.17.4.6.0.3.7",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="alternativeAngleCandidate",
        owner="backend.app.application.draft_alternative_angle_candidate_service",
        current_module="backend/app/application/draft_alternative_angle_candidate_service.py",
        operation_kind="alternativeAngleCandidate",
        status="legacyAllowlisted",
        reason_not_migrated="alternative-angle tournament gets migrated after representative validator/writer pair",
        removal_slice="2.17.4.6.0.3.7",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="pairwiseRanking",
        owner="backend.app.application.draft_pairwise_ranking_service",
        current_module="backend/app/application/draft_pairwise_ranking_service.py",
        operation_kind="pairwiseRanking",
        status="legacyAllowlisted",
        reason_not_migrated="ranking trace migration follows directed revision representative",
        removal_slice="2.17.4.6.0.3.7",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="directedRevision",
        owner="backend.app.application.draft_directed_revision_service",
        current_module="backend/app/application/draft_directed_revision_service.py",
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
        owner="backend.app.application.draft_final_quality_review_service",
        current_module="backend/app/application/draft_final_quality_review_service.py",
        operation_kind="finalQualityReviewRepair",
        status="legacyAllowlisted",
        reason_not_migrated="final-quality repair loop requires dedicated result contract alignment",
        removal_slice="2.17.4.6.0.3.8",
        expected_incident_coverage=("malformedJson", "schemaFailure", "notConfigured", "backupAccepted"),
    ),
    LlmOperationInventoryEntry(
        operation_id="humanCommentRevision",
        owner="backend.app.application.draft_human_comment_revision_service",
        current_module="backend/app/application/draft_human_comment_revision_service.py",
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
        owner="backend.app.application.draft_human_comment_quality_service",
        current_module="backend/app/application/draft_human_comment_quality_service.py",
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
