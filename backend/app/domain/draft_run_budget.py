from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class DraftRunExecutionMode(StrEnum):
    SMOKE = "smoke"
    STANDARD = "standard"
    FULL = "full"


class DraftRunResearchDepth(StrEnum):
    LIGHT = "light"
    STANDARD = "standard"
    DEEP = "deep"
    MARKET_RESEARCH = "marketResearch"


@dataclass(frozen=True)
class DraftRunBudgetCaps:
    max_research_tasks: int
    max_search_tasks: int
    max_url_reads: int
    max_search_results_per_task: int
    max_accepted_evidence_items: int
    max_external_claims: int
    max_usable_evidence_candidates: int
    max_draft_candidates: int
    max_revision_iterations: int

    def to_payload(self) -> dict[str, int]:
        return {
            "maxResearchTasks": self.max_research_tasks,
            "maxSearchTasks": self.max_search_tasks,
            "maxUrlReads": self.max_url_reads,
            "maxSearchResultsPerTask": self.max_search_results_per_task,
            "maxAcceptedEvidenceItems": self.max_accepted_evidence_items,
            "maxExternalClaims": self.max_external_claims,
            "maxUsableEvidenceCandidates": self.max_usable_evidence_candidates,
            "maxDraftCandidates": self.max_draft_candidates,
            "maxRevisionIterations": self.max_revision_iterations,
        }


@dataclass(frozen=True)
class DraftRunBudget:
    research_depth: DraftRunResearchDepth
    execution_mode: DraftRunExecutionMode
    caps: DraftRunBudgetCaps
    source: str = "default"

    def to_payload(self) -> dict[str, Any]:
        return {
            "researchDepth": self.research_depth.value,
            "executionMode": self.execution_mode.value,
            "caps": self.caps.to_payload(),
            "source": self.source,
        }
