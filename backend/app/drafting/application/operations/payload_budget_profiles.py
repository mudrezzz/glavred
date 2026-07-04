"""Owner: drafting.application.operations

Used by: DraftRun payload budget policy to resolve per-operation execution caps.
Does not own: compacting rules, semantic input contracts, provider adapters.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from __future__ import annotations

import math
from typing import Mapping

from backend.app.drafting.application.operations.payload_budget_contracts import PayloadBudgetProfile

EXECUTION_MODES = ("smoke", "standard", "full")

OPERATION_FAMILIES: dict[str, tuple[str, str]] = {
    "sourceIntentAndResearchPlan": ("sourceResearchPlanning", "research"),
    "evidenceSynthesis": ("evidenceSynthesis", "research"),
    "evidenceInterpretation": ("evidenceInterpretation", "evidence"),
    "materialPlan": ("materialPlanning", "evidence"),
    "draftStrategy": ("draftStrategy", "evidence"),
    "rhetoricalPlans": ("rhetoricalPlanning", "evidence"),
    "draftCandidate": ("draftCandidateGeneration", "writer"),
    "llmValidation": ("llmValidation", "validator"),
    "editorialCritique": ("reportOnlyValidator", "validator"),
    "pairwiseRanking": ("pairwiseRanking", "validator"),
    "directedRevision": ("writerRevision", "writer"),
    "finalQualityReviewRepair": ("finalQualityReviewRepair", "validator"),
    "humanCommentRevision": ("hitlWriterRevision", "writer"),
    "humanCommentRevisionQualityCheck": ("hitlQualityCheck", "validator"),
    "alternativeAngleRoute": ("alternativeAngleRoute", "validator"),
    "alternativeAngleCandidate": ("alternativeAngleCandidate", "writer"),
    "publicEvidenceSearch": ("publicEvidenceSearch", "research"),
    "publicEvidenceRead": ("publicEvidenceRead", "research"),
}


class PayloadBudgetProfileRegistry:
    def __init__(self, profiles: Mapping[tuple[str, str], PayloadBudgetProfile] | None = None) -> None:
        self._profiles = dict(profiles or DEFAULT_PROFILES)

    def profile_for(self, operation_id: str, execution_mode: str | None = None) -> PayloadBudgetProfile:
        return self._profiles[(operation_id, self.execution_mode(execution_mode))]

    def execution_mode(self, value: str | None) -> str:
        normalized = str(value or "standard").strip().lower()
        return normalized if normalized in EXECUTION_MODES else "standard"


def build_profile(operation_id: str, operation_kind: str, family: str, mode: str) -> PayloadBudgetProfile:
    caps = {
        "research": (6000, 12000, 22000),
        "evidence": (10000, 18000, 30000),
        "writer": (12000, 24000, 40000),
        "validator": (12000, 22000, 36000),
    }[family]
    index = EXECUTION_MODES.index(mode)
    max_prompt_chars = caps[index]
    scale = (1, 2, 3)[index]
    return PayloadBudgetProfile(
        operation_id=operation_id,
        operation_kind=operation_kind,
        execution_mode=mode,
        max_prompt_chars=max_prompt_chars,
        # This is deliberately approximate and trace-facing only; provider tokenizers
        # stay outside the application policy layer.
        approx_token_budget=math.ceil(max_prompt_chars / 4),
        max_rules=20 * scale,
        max_claims=12 * scale,
        max_evidence_items=12 * scale,
        max_candidates=2 * scale,
        max_source_snippets=12 * scale,
        max_prior_drafts=1 * scale,
    )


DEFAULT_PROFILES: dict[tuple[str, str], PayloadBudgetProfile] = {
    (operation_id, mode): build_profile(operation_id, operation_kind, family, mode)
    for operation_id, (operation_kind, family) in OPERATION_FAMILIES.items()
    for mode in EXECUTION_MODES
}
