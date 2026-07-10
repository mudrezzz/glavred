"""Owner: drafting.application.dossiers

Used by: role-owned dossier factories to build one typed provider projection.
Does not own: artifact extraction, budget compaction, prompt construction, or provider calls.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from typing import Mapping

from backend.app.drafting.application.dossiers.provider_dossier_policy import ProviderDossierPolicy
from backend.app.drafting.domain.provider_dossier import (
    ContextSelection,
    DossierQualityRisk,
    DossierReadinessStatus,
    ProviderDossier,
)


class ProviderDossierAssembler:
    def assemble(
        self,
        policy: ProviderDossierPolicy,
        selections: Mapping[str, ContextSelection],
        *,
        runtime_migrated: bool = False,
    ) -> ProviderDossier:
        contract = policy.semantic_contract
        required = set(contract.must_have)
        optional = set(contract.should_have)
        provider_keys = required | optional
        missing_required = tuple(sorted(key for key in required if not self._available(selections.get(key))))
        missing_optional = tuple(sorted(key for key in optional if not self._available(selections.get(key))))

        sent = {
            key: selection.copied_value()
            for key, selection in sorted(selections.items())
            if key in provider_keys and self._available(selection)
        }
        handles = {
            key: selection.handles
            for key, selection in sorted(selections.items())
            if selection.handles
        }
        sent_counts = {
            key: selection.selected_count
            for key, selection in sorted(selections.items())
            if key in sent
        }
        trimmed_counts = {
            key: selection.trimmed_count
            for key, selection in sorted(selections.items())
            if selection.trimmed_count > 0
        }
        risk = self._quality_risk(missing_required, missing_optional, trimmed_counts, required)
        readiness = self._readiness(risk, missing_required)
        suppressed = tuple(sorted(set(contract.never_send_to_provider) | set(contract.diagnostic_only)))

        return ProviderDossier(
            profile_id=policy.profile_id,
            operation_id=policy.operation_id,
            model_role=policy.model_role,
            readiness_status=readiness,
            semantic_contract=contract,
            sent=sent,
            handles=handles,
            sent_counts=sent_counts,
            trimmed_counts=trimmed_counts,
            suppressed_fields=suppressed,
            quality_risk=risk,
            missing_required_inputs=missing_required,
            runtime_migrated=runtime_migrated,
            metadata={
                "missingOptionalInputs": list(missing_optional),
                "runtimeMigrationStatus": "migrated" if runtime_migrated else "notMigrated",
            },
        )

    def _available(self, selection: ContextSelection | None) -> bool:
        return bool(selection and selection.available)

    def _quality_risk(
        self,
        missing_required: tuple[str, ...],
        missing_optional: tuple[str, ...],
        trimmed_counts: Mapping[str, int],
        required: set[str],
    ) -> DossierQualityRisk:
        if missing_required:
            return DossierQualityRisk.HIGH
        if any(key in required for key in trimmed_counts):
            return DossierQualityRisk.MEDIUM
        if missing_optional or trimmed_counts:
            return DossierQualityRisk.LOW
        return DossierQualityRisk.NONE

    def _readiness(
        self,
        risk: DossierQualityRisk,
        missing_required: tuple[str, ...],
    ) -> DossierReadinessStatus:
        if missing_required:
            return DossierReadinessStatus.BLOCKED
        if risk != DossierQualityRisk.NONE:
            return DossierReadinessStatus.DEGRADED
        return DossierReadinessStatus.READY


__all__ = ("ProviderDossierAssembler",)
