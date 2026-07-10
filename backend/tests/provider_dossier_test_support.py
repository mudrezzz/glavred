import json
from pathlib import Path

from backend.app.drafting.application.context.draft_run_context_access import DraftRunContextAccessService


class ProviderDossierTestFixture:
    PATH = Path(__file__).parent / "fixtures" / "draft_run_provider_dossier_snapshot.json"

    @classmethod
    def snapshot(cls) -> dict:
        return json.loads(cls.PATH.read_text(encoding="utf-8"))

    @classmethod
    def access(cls) -> DraftRunContextAccessService:
        return DraftRunContextAccessService.from_snapshot(cls.snapshot())
