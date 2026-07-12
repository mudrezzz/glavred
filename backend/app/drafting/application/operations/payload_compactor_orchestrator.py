"""Owner: drafting.application.operations

Used by: Payload budget runtime to apply operation semantic contracts before provider calls.
Does not own: Payload budget profile definitions, provider adapters, or prompt text.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

from typing import Any, Mapping

from backend.app.drafting.application.operations.payload_artifact_compactors import (
    ContextArtifactCompactor,
    DraftArtifactCompactor,
    MaterialPlanCompactor,
    TraceContextCompactor,
    ValidationReportCompactor,
)
from backend.app.drafting.application.operations.payload_alternative_angle_route_compactor import (
    AlternativeAngleRoutePayloadCompactor,
)
from backend.app.drafting.application.operations.payload_budget_contracts import PayloadBudgetProfile, PayloadCompactionResult, SemanticInputContract
from backend.app.drafting.application.operations.payload_compactor_common import CountAccumulator, _record, _records
from backend.app.drafting.application.operations.payload_evidence_compactors import RulePackCompactor
from backend.app.drafting.application.operations.payload_record_compactors import CandidatePayloadCompactor
from backend.app.drafting.application.operations.payload_review_dossier_compactor import ReviewDossierPayloadCompactor
from backend.app.drafting.application.operations.payload_pairwise_ranking_compactor import PairwiseRankingPayloadCompactor


class DraftRunPayloadCompactor:
    def __init__(self) -> None:
        self._context = ContextArtifactCompactor()
        self._rules = RulePackCompactor()
        self._material = MaterialPlanCompactor()
        self._draft = DraftArtifactCompactor()
        self._trace = TraceContextCompactor()
        self._validation = ValidationReportCompactor()
        self._alternative_angle_route = AlternativeAngleRoutePayloadCompactor()
        self._review_dossiers = ReviewDossierPayloadCompactor()
        self._pairwise_ranking = PairwiseRankingPayloadCompactor()

    def compact(self, payload: Mapping[str, Any], *, profile: PayloadBudgetProfile, contract: SemanticInputContract) -> PayloadCompactionResult:
        suppressed = [field_name for field_name in contract.never_send_to_provider if field_name in payload]
        compact = {
            key: value
            for key, value in dict(payload).items()
            if key not in set(contract.never_send_to_provider).union(contract.diagnostic_only)
        }
        suppressed.extend([field_name for field_name in contract.diagnostic_only if field_name in payload])
        trimmed: dict[str, int] = {}

        self._compact_key(compact, trimmed, "context_artifact", self._context.compact, profile)
        self._compact_key(compact, trimmed, "contextArtifact", self._context.compact, profile)
        self._compact_key(compact, trimmed, "rule_pack", self._rules.compact, profile)
        self._compact_key(compact, trimmed, "rulePack", self._rules.compact, profile)
        self._compact_key(compact, trimmed, "material_plan", self._material.compact, profile)
        self._compact_key(compact, trimmed, "materialPlan", self._material.compact, profile)
        if "dossierId" in compact:
            if profile.operation_id == "alternativeAngleRoute":
                compact, dossier_counts = self._alternative_angle_route.compact(compact, profile)
            else:
                compact, dossier_counts = self._review_dossiers.compact(compact, profile)
            CountAccumulator.merge(trimmed, dossier_counts)
            if profile.operation_id == "pairwiseRanking":
                compact, ranking_counts = self._pairwise_ranking.compact(compact)
                CountAccumulator.merge(trimmed, ranking_counts)
        else:
            self._compact_candidates(compact, trimmed, profile)
        self._compact_key(compact, trimmed, "draft_artifact", self._draft.compact, profile)
        self._compact_key(compact, trimmed, "trace_context", self._trace.compact, profile)
        self._compact_key(compact, trimmed, "traceContext", self._trace.compact, profile)
        self._compact_key(compact, trimmed, "deterministic_report", self._validation.compact, profile)
        self._compact_key(compact, trimmed, "llm_validation_report", self._validation.compact, profile)
        self._compact_key(compact, trimmed, "validation_report", self._validation.compact, profile)
        return PayloadCompactionResult(payload=compact, trimmed_counts=trimmed, suppressed_fields=tuple(sorted(set(suppressed))))

    def _compact_key(self, payload: dict[str, Any], trimmed: dict[str, int], key: str, compact: Any, profile: PayloadBudgetProfile) -> None:
        if key not in payload:
            return
        payload[key], counts = compact(_record(payload[key]), profile)
        CountAccumulator.merge(trimmed, counts)

    def _compact_candidates(self, payload: dict[str, Any], trimmed: dict[str, int], profile: PayloadBudgetProfile) -> None:
        if "candidate" in payload:
            payload["candidate"] = CandidatePayloadCompactor.compact(_record(payload["candidate"]))
        if "candidates" not in payload:
            return
        candidates = _records(payload["candidates"])
        payload["candidates"] = [CandidatePayloadCompactor.compact(candidate) for candidate in candidates[: profile.max_candidates]]
        CountAccumulator.trimmed(trimmed, "candidates", len(candidates), len(payload["candidates"]))
