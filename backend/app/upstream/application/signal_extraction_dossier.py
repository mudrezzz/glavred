"""Owner: upstream.application

Used by: signal extraction dossier construction, attempts, validation, and reporting.
Does not own: dossier assembly, provider calls, grounding policy, or persistence.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SignalExtractionDossier:
    provider_input: dict[str, Any]
    fragment_index: dict[tuple[str, str], dict[str, Any]]
    eligible_material_ids: tuple[str, ...]
    deferred_material_ids: tuple[str, ...]
    legacy_material_ids: tuple[str, ...]
    language_excluded_material_ids: tuple[str, ...]
    readiness: str
    suppressed_fields: tuple[str, ...]
    trimmed_fragment_count: int = 0
    trimmed_context_count: int = 0

    def trace_payload(self) -> dict[str, Any]:
        return {
            "profileId": "upstream-signal-extraction-dossier-v1",
            "readiness": self.readiness,
            "eligibleMaterialIds": list(self.eligible_material_ids),
            "deferredMaterialIds": list(self.deferred_material_ids),
            "legacyMaterialIds": list(self.legacy_material_ids),
            "languageExcludedMaterialIds": list(self.language_excluded_material_ids),
            "fragmentCount": len(self.fragment_index),
            "trimmedFragmentCount": self.trimmed_fragment_count,
            "trimmedContextCount": self.trimmed_context_count,
            "suppressedFields": list(self.suppressed_fields),
            "neverSendToProvider": list(self.suppressed_fields),
            "runtimeMigrated": True,
        }


__all__ = ("SignalExtractionDossier",)
