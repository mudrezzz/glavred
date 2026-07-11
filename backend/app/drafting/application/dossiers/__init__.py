"""Owner: drafting.application.dossiers

Used by: future provider-heavy DraftRun operation migrations and replay diagnostics.
Does not own: rich artifact persistence, prompt wording, budgets, or provider calls.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from backend.app.drafting.application.dossiers.provider_dossier_factories import (
    AlternativeAngleDossierFactory,
    FinalQualityDossierFactory,
    PlanningDossierFactory,
    RankingDossierFactory,
    ReviewDossierFactory,
    RevisionDossierFactory,
    WriterDossierFactory,
)

__all__ = (
    "AlternativeAngleDossierFactory",
    "FinalQualityDossierFactory",
    "PlanningDossierFactory",
    "RankingDossierFactory",
    "ReviewDossierFactory",
    "RevisionDossierFactory",
    "WriterDossierFactory",
)
