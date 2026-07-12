"""Owner: drafting.application.dossiers

Used by: provider-free dossier audit CLI and deterministic replay tests.
Does not own: provider calls, prompt construction, live runtime migration, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from backend.app.drafting.application.context.draft_run_context_access import DraftRunContextAccessService
from backend.app.drafting.application.dossiers.provider_dossier_factories import (
    AlternativeAngleDossierFactory,
    FinalQualityDossierFactory,
    PlanningDossierFactory,
    RankingDossierFactory,
    ReviewDossierFactory,
    RevisionDossierFactory,
    WriterDossierFactory,
)
from backend.app.drafting.domain.provider_dossier import HandleResolutionStatus, ProviderDossier


@dataclass(frozen=True)
class ProviderDossierReplayReport:
    run_id: str
    dossiers: tuple[ProviderDossier, ...]
    unresolved_handle_ids: tuple[str, ...]
    forbidden_field_violations: tuple[str, ...]

    @property
    def ready_for_migration(self) -> bool:
        return not self.unresolved_handle_ids and not self.forbidden_field_violations and all(
            dossier.readiness_status.value != "blocked" for dossier in self.dossiers
        )

    def to_payload(self) -> dict[str, Any]:
        migrated = sum(1 for dossier in self.dossiers if dossier.runtime_migrated)
        migration_status = (
            "migrated"
            if migrated == len(self.dossiers)
            else "partiallyMigrated"
            if migrated
            else "notMigrated"
        )
        return {
            "runId": self.run_id,
            "runtimeMigrationStatus": migration_status,
            "verdict": "readyForMigration" if self.ready_for_migration else "foundationNeedsAttention",
            "dossiers": [self._summary(dossier) for dossier in self.dossiers],
            "unresolvedHandleIds": list(self.unresolved_handle_ids),
            "forbiddenFieldViolations": list(self.forbidden_field_violations),
            "note": (
                "All planned dossier families are runtime-migrated."
                if migrated == len(self.dossiers)
                else "Planning and writer call sites are migrated; remaining dossier families still require their roadmap slices."
                if migrated
                else "Factory proof only; provider operation call sites are not migrated."
            ),
        }

    def to_markdown(self) -> str:
        payload = self.to_payload()
        lines = [
            f"# DraftRun provider dossier replay: {self.run_id}",
            "",
            f"- verdict: `{payload['verdict']}`",
            f"- runtime migration: `{payload['runtimeMigrationStatus']}`",
            f"- unresolved handles: {len(self.unresolved_handle_ids)}",
            f"- forbidden field violations: {len(self.forbidden_field_violations)}",
            "",
            "## Dossiers",
        ]
        for dossier in payload["dossiers"]:
            lines.append(
                f"- `{dossier['operationId']}`: {dossier['readinessStatus']}; "
                f"{dossier['promptCharEstimate']} chars; risk `{dossier['qualityRisk']}`"
            )
        lines.extend(("", payload["note"]))
        return "\n".join(lines)

    def _summary(self, dossier: ProviderDossier) -> dict[str, Any]:
        provider_input = dossier.provider_input()
        prompt_chars = len(json.dumps(provider_input, ensure_ascii=False, sort_keys=True))
        return {
            "profileId": dossier.profile_id,
            "operationId": dossier.operation_id,
            "modelRole": dossier.model_role,
            "readinessStatus": dossier.readiness_status.value,
            "qualityRisk": dossier.quality_risk.value,
            "missingRequiredInputs": list(dossier.missing_required_inputs),
            "sentFields": sorted(dossier.sent.keys()),
            "sentCounts": dict(dossier.sent_counts),
            "trimmedCounts": dict(dossier.trimmed_counts),
            "suppressedFields": list(dossier.suppressed_fields),
            "handleCount": sum(len(items) for items in dossier.handles.values()),
            "promptCharEstimate": prompt_chars,
            "approxTokenEstimate": (prompt_chars + 3) // 4,
            "runtimeMigrated": dossier.runtime_migrated,
        }


class ProviderDossierReplayService:
    def run(self, access: DraftRunContextAccessService) -> ProviderDossierReplayReport:
        candidate_summary = self._first_candidate(access)
        candidate_id = str(candidate_summary.get("id") or "") or None
        plan_id = str(candidate_summary.get("rhetoricalPlanId") or "") or None
        dossiers = (
            PlanningDossierFactory(access).build("materialPlan"),
            PlanningDossierFactory(access).build("strategy"),
            PlanningDossierFactory(access).build("rhetoricalPlans"),
            WriterDossierFactory(access).build(plan_id=plan_id),
            AlternativeAngleDossierFactory(access).build(),
            WriterDossierFactory(access).build(plan_id=None, operation_id="alternativeAngleCandidate"),
            ReviewDossierFactory(access).build(candidate_id=candidate_id),
            RankingDossierFactory(access).build(),
            RevisionDossierFactory(access).build(candidate_id=candidate_id),
            FinalQualityDossierFactory(access).build(candidate_id=candidate_id),
        )
        unresolved = tuple(sorted({
            handle.id
            for dossier in dossiers
            for handles in dossier.handles.values()
            for handle in handles
            if access.resolve(handle).status != HandleResolutionStatus.RESOLVED
        }))
        forbidden = tuple(sorted({
            f"{dossier.operation_id}:{field}"
            for dossier in dossiers
            for field in dossier.semantic_contract.never_send_to_provider
            if self._contains_key(dossier.provider_input(), field)
        }))
        return ProviderDossierReplayReport(access.run_id, dossiers, unresolved, forbidden)

    def _first_candidate(self, access: DraftRunContextAccessService) -> dict[str, Any]:
        selection = access.candidate_summaries(limit=1)
        if not selection.available or not isinstance(selection.value, list) or not selection.value:
            return {}
        item = selection.value[0]
        return dict(item) if isinstance(item, dict) else {}

    def _contains_key(self, value: Any, forbidden: str) -> bool:
        if isinstance(value, dict):
            return forbidden in value or any(self._contains_key(child, forbidden) for child in value.values())
        if isinstance(value, list):
            return any(self._contains_key(child, forbidden) for child in value)
        return False


__all__ = ("ProviderDossierReplayReport", "ProviderDossierReplayService")
