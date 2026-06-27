from dataclasses import dataclass
from typing import Any

from backend.app.application.deterministic_external_evidence_synthesis_step_service import (
    DeterministicExternalEvidenceSynthesisStepService,
)
from backend.app.application.draft_run_step_progress import DraftRunStepOperationSink
from backend.app.application.public_evidence_retrieval_service import PublicEvidenceRetrievalService
from backend.app.application.source_ledger_budgeting import apply_external_claim_budget
from backend.app.application.source_ledger_external_evidence_merger import SourceLedgerExternalEvidenceMerger


@dataclass(frozen=True)
class PublicEvidenceStepResult:
    artifact_payload: dict[str, Any]
    context_artifact: dict[str, Any]
    ai_run_ids: list[str]


class PublicEvidenceStepService:
    def __init__(
        self,
        public_evidence_service: PublicEvidenceRetrievalService | None = None,
        external_evidence_synthesis_service: Any = None,
        source_ledger_external_evidence_merger: SourceLedgerExternalEvidenceMerger | None = None,
    ) -> None:
        self._public_evidence_service = public_evidence_service or PublicEvidenceRetrievalService()
        self._synthesis_service = external_evidence_synthesis_service or DeterministicExternalEvidenceSynthesisStepService()
        self._ledger_merger = source_ledger_external_evidence_merger or SourceLedgerExternalEvidenceMerger()

    def run(
        self,
        *,
        source_intent_artifact: dict[str, Any],
        context_artifact: dict[str, Any],
        progress: DraftRunStepOperationSink | None = None,
    ) -> PublicEvidenceStepResult:
        public_evidence_batch = self._public_evidence_service.retrieve(
            source_intent_artifact=source_intent_artifact,
            context_artifact=context_artifact,
            progress=progress,
        )
        ai_run_ids = list(public_evidence_batch.ai_run_ids)
        public_evidence = public_evidence_batch.to_payload()
        synthesis_context = {**context_artifact, "publicEvidence": public_evidence}
        if progress:
            progress.start_operation(
                "external-evidence-synthesis",
                kind="externalEvidenceSynthesis",
                label="Synthesize accepted public evidence",
                target=f"{len(public_evidence.get('items', []))} evidence items",
            )
        synthesis_result = self._synthesis_service.synthesize(
            context_artifact=synthesis_context,
            public_evidence=public_evidence,
        )
        if synthesis_result.ai_run_id:
            ai_run_ids.append(synthesis_result.ai_run_id)
        if progress:
            progress.complete_operation("external-evidence-synthesis", ai_run_id=synthesis_result.ai_run_id)
        evidence_synthesis = _payload(synthesis_result.artifact_payload, "evidenceSynthesis")
        enriched_ledger = self._ledger_merger.merge(
            source_ledger=_payload(context_artifact, "sourceLedger"),
            public_evidence=public_evidence,
            evidence_synthesis=evidence_synthesis,
        )
        enriched_ledger = apply_external_claim_budget(source_ledger=enriched_ledger, context_artifact=context_artifact)
        artifact_payload = {
            **public_evidence,
            **synthesis_result.artifact_payload,
            "enrichedSourceLedger": enriched_ledger,
            "draftRunBudget": context_artifact.get("draftRunBudget"),
        }
        return PublicEvidenceStepResult(
            artifact_payload=artifact_payload,
            context_artifact={
                **context_artifact,
                "publicEvidence": artifact_payload,
                "evidenceSynthesis": evidence_synthesis,
                "sourceLedger": enriched_ledger,
            },
            ai_run_ids=ai_run_ids,
        )


def _payload(artifact: dict[str, Any], key: str) -> dict[str, Any]:
    value = artifact.get(key)
    return value if isinstance(value, dict) else {}
