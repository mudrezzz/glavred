"""Owner: drafting.application.dossiers

Used by: provider dossier factories to classify provider-visible context.
Does not own: artifact lookup, budget limits, prompt construction, or provider calls.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.app.drafting.domain.provider_input_semantics import SemanticInputContract


NEVER_SEND_FULL_ARTIFACTS = (
    "sourceLedger",
    "rulePack",
    "candidatePool",
    "validationReport",
    "finalQualityTrace",
    "operationEnvelope",
    "payloadBudget",
    "runtimeBudget",
    "articleDossier",
    "contextPacks",
)


@dataclass(frozen=True)
class ProviderDossierPolicy:
    profile_id: str
    operation_id: str
    model_role: str
    semantic_contract: SemanticInputContract


class ProviderDossierPolicyRegistry:
    def planning(self, operation_id: str) -> ProviderDossierPolicy:
        contracts = {
            "materialPlan": (
                ("postContract", "evidence"),
                ("rules",),
            ),
            "strategy": (
                ("postContract", "materialPlan"),
                ("evidence", "rules"),
            ),
            "rhetoricalPlans": (
                ("postContract", "materialPlan", "draftStrategy"),
                ("evidence", "rules"),
            ),
        }
        if operation_id not in contracts:
            raise ValueError(f"Unsupported planning dossier operation: {operation_id}")
        must, should = contracts[operation_id]
        return self._policy(
            "planningDossier", operation_id, "strategy",
            must=must, should=should,
        )

    def writer(self, operation_id: str) -> ProviderDossierPolicy:
        if operation_id == "alternativeAngleCandidate":
            return self._policy(
                "writerDossier", operation_id, "writer",
                must=("postContract", "planning", "alternativeRoute", "evidence"),
                should=("claims", "rules", "critiqueSignals"),
            )
        return self._policy(
            "writerDossier", operation_id, "writer",
            must=("postContract", "planning", "rhetoricalPlan", "evidence"),
            should=("claims", "rules"),
        )

    def alternative_angle(self, operation_id: str) -> ProviderDossierPolicy:
        if operation_id != "alternativeAngleRoute":
            raise ValueError(f"Unsupported alternative-angle dossier operation: {operation_id}")
        return self._policy(
            "alternativeAngleDossier",
            operation_id,
            "anotherAngle",
            must=("candidates", "critiqueSignals", "postContract"),
            should=("validationIssues", "rejectedMoves", "evidence", "claims", "rules"),
        )

    def review(self, operation_id: str, model_role: str) -> ProviderDossierPolicy:
        return self._policy(
            "reviewDossier", operation_id, model_role,
            must=("candidate", "postContract", "validationIssues"), should=("evidence", "rules"),
        )

    def ranking(self, operation_id: str) -> ProviderDossierPolicy:
        return self._policy(
            "rankingDossier", operation_id, "review",
            must=("candidates", "validationIssues", "editorialDimensions"),
            should=("postContract", "evidence", "selectionConstraints"),
        )

    def revision(self, operation_id: str) -> ProviderDossierPolicy:
        return self._policy(
            "revisionDossier", operation_id, "writer",
            must=("candidate", "revisionInstruction", "postContract"),
            should=("validationIssues", "evidence", "rules", "antiRegressionConstraints"),
        )

    def final_quality(self, operation_id: str) -> ProviderDossierPolicy:
        return self._policy(
            "finalQualityDossier", operation_id, "finalGate",
            must=("candidate", "finalQualityContract", "deterministicGate"),
            should=("postContract", "validationIssues", "evidence", "repairHistory", "finalQualityIssues"),
        )

    def _policy(
        self,
        prefix: str,
        operation_id: str,
        model_role: str,
        *,
        must: tuple[str, ...],
        should: tuple[str, ...],
    ) -> ProviderDossierPolicy:
        return ProviderDossierPolicy(
            profile_id=f"{prefix}:{operation_id}",
            operation_id=operation_id,
            model_role=model_role,
            semantic_contract=SemanticInputContract(
                must_have=must,
                should_have=should,
                diagnostic_only=("sourceDiagnostics", "providerTrace"),
                never_send_to_provider=NEVER_SEND_FULL_ARTIFACTS,
            ),
        )


__all__ = ("ProviderDossierPolicy", "ProviderDossierPolicyRegistry")
