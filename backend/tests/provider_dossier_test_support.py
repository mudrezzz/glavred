import json
from pathlib import Path

from backend.app.drafting.application.context.draft_run_context_access import DraftRunContextAccessService
from backend.app.drafting.application.dossiers.provider_dossier_factories import PlanningDossierFactory, WriterDossierFactory
from backend.app.drafting.domain.provider_dossier import ProviderDossier


class ProviderDossierTestFixture:
    PATH = Path(__file__).parent / "fixtures" / "draft_run_provider_dossier_snapshot.json"

    @classmethod
    def snapshot(cls) -> dict:
        return json.loads(cls.PATH.read_text(encoding="utf-8"))

    @classmethod
    def access(cls) -> DraftRunContextAccessService:
        snapshot = cls.snapshot()
        steps = snapshot["steps"]
        validation = steps["validation"]
        candidates = steps["draft"]["candidates"]
        validation["reviewContext"] = {
            "stage": "provider-dossier-test",
            "candidates": candidates,
            "currentCandidate": candidates[0],
            "validationReport": {"candidateReports": validation["candidateReports"]},
            "revisionInstruction": {
                "status": "created",
                "candidateId": candidates[0]["id"],
                "repairGoals": ["Qualify the workflow integration claim."],
            },
            "finalQualityContract": {
                "version": "final-quality-contract-v1",
                "postContract": steps["postContract"],
            },
            "deterministicGate": {"status": "warning", "candidateId": candidates[0]["id"]},
            "repairHistory": validation["rankingRevision"]["revisionLoop"],
        }
        return DraftRunContextAccessService.from_snapshot(snapshot)

    @classmethod
    def planning_dossier(cls, operation_id: str = "materialPlan") -> ProviderDossier:
        return PlanningDossierFactory(cls.access()).build(operation_id)

    @classmethod
    def writer_factory(cls) -> WriterDossierFactory:
        return WriterDossierFactory(cls.access())
