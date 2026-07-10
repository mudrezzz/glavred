"""Owner: drafting.application.dossiers

Used by: future planning, writing, review, ranking, revision, and final-quality calls.
Does not own: rich artifact persistence, prompt wording, budgets, or provider calls.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from backend.app.drafting.application.context.draft_run_context_access import DraftRunContextAccessService
from backend.app.drafting.application.dossiers.provider_dossier_assembler import ProviderDossierAssembler
from backend.app.drafting.application.dossiers.provider_dossier_policy import ProviderDossierPolicyRegistry
from backend.app.drafting.domain.provider_dossier import ProviderDossier


class PlanningDossierFactory:
    def __init__(self, access: DraftRunContextAccessService) -> None:
        self._access = access

    def build(self, operation_id: str = "materialPlan") -> ProviderDossier:
        evidence_limit = {
            "materialPlan": 12,
            "strategy": 6,
            "rhetoricalPlans": 2,
        }.get(operation_id, 12)
        rule_limit = {
            "materialPlan": 8,
            "strategy": 8,
            "rhetoricalPlans": 4,
        }.get(operation_id, 8)
        selections = {
            "postContract": self._access.post_contract(),
            "evidence": self._access.evidence(limit=evidence_limit),
            "rules": self._access.rules(limit=rule_limit),
        }
        if operation_id in {"strategy", "rhetoricalPlans"}:
            selections["materialPlan"] = self._access.material_plan()
        if operation_id == "rhetoricalPlans":
            selections["draftStrategy"] = self._access.draft_strategy()
        return ProviderDossierAssembler().assemble(
            ProviderDossierPolicyRegistry().planning(operation_id),
            selections,
            runtime_migrated=True,
        )


class WriterDossierFactory:
    def __init__(self, access: DraftRunContextAccessService) -> None:
        self._access = access

    def build(self, *, plan_id: str | None, operation_id: str = "draftCandidate") -> ProviderDossier:
        return ProviderDossierAssembler().assemble(
            ProviderDossierPolicyRegistry().writer(operation_id),
            {
                "postContract": self._access.post_contract(),
                "planning": self._access.planning(),
                "rhetoricalPlan": self._access.rhetorical_plan(plan_id),
                "evidence": self._access.evidence(),
                "rules": self._access.rules(),
            },
        )


class ReviewDossierFactory:
    def __init__(self, access: DraftRunContextAccessService) -> None:
        self._access = access

    def build(
        self,
        *,
        candidate_id: str | None,
        operation_id: str = "llmValidation",
        model_role: str | None = None,
    ) -> ProviderDossier:
        resolved_role = model_role or self._model_role(operation_id)
        return ProviderDossierAssembler().assemble(
            ProviderDossierPolicyRegistry().review(operation_id, resolved_role),
            {
                "candidate": self._access.selected_candidate(candidate_id),
                "postContract": self._access.post_contract(),
                "evidence": self._access.evidence(),
                "rules": self._access.rules(),
                "validationIssues": self._access.validation_issues(candidate_id),
            },
        )

    def _model_role(self, operation_id: str) -> str:
        if operation_id == "editorialCritique":
            return "critic"
        if operation_id == "alternativeAngleRoute":
            return "anotherAngle"
        return "review"


class RankingDossierFactory:
    def __init__(self, access: DraftRunContextAccessService) -> None:
        self._access = access

    def build(self, operation_id: str = "pairwiseRanking") -> ProviderDossier:
        return ProviderDossierAssembler().assemble(
            ProviderDossierPolicyRegistry().ranking(operation_id),
            {
                "candidates": self._access.candidate_summaries(),
                "validationIssues": self._access.validation_issues(),
                "postContract": self._access.post_contract(),
                "evidence": self._access.evidence(),
            },
        )


class RevisionDossierFactory:
    def __init__(self, access: DraftRunContextAccessService) -> None:
        self._access = access

    def build(self, *, candidate_id: str | None, operation_id: str = "directedRevision") -> ProviderDossier:
        return ProviderDossierAssembler().assemble(
            ProviderDossierPolicyRegistry().revision(operation_id),
            {
                "candidate": self._access.selected_candidate(candidate_id),
                "validationIssues": self._access.validation_issues(candidate_id),
                "postContract": self._access.post_contract(),
                "evidence": self._access.evidence(),
                "rules": self._access.rules(),
            },
        )


class FinalQualityDossierFactory:
    def __init__(self, access: DraftRunContextAccessService) -> None:
        self._access = access

    def build(self, *, candidate_id: str | None, operation_id: str = "finalQualityGateReview") -> ProviderDossier:
        return ProviderDossierAssembler().assemble(
            ProviderDossierPolicyRegistry().final_quality(operation_id),
            {
                "candidate": self._access.selected_candidate(candidate_id),
                "postContract": self._access.post_contract(),
                "finalQualityIssues": self._access.final_quality_lifecycle(),
                "validationIssues": self._access.validation_issues(candidate_id),
                "evidence": self._access.evidence(),
                "repairHistory": self._access.repair_history(),
            },
        )


__all__ = (
    "FinalQualityDossierFactory",
    "PlanningDossierFactory",
    "RankingDossierFactory",
    "ReviewDossierFactory",
    "RevisionDossierFactory",
    "WriterDossierFactory",
)
