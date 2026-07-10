"""Owner: drafting.domain

Used by: deterministic DraftRun context access and provider dossier factories.
Does not own: artifact lookup, prompt construction, provider calls, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from typing import Any, Mapping

from backend.app.drafting.domain.provider_input_semantics import SemanticInputContract


class DossierReadinessStatus(StrEnum):
    READY = "ready"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class DossierQualityRisk(StrEnum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HandleResolutionStatus(StrEnum):
    RESOLVED = "resolved"
    NOT_FOUND = "notFound"
    RUN_MISMATCH = "runMismatch"
    STALE = "stale"


@dataclass(frozen=True)
class ArtifactHandle:
    id: str
    run_id: str
    step_key: str
    artifact_type: str
    artifact_id: str
    path: tuple[str | int, ...]

    @classmethod
    def create(
        cls,
        *,
        run_id: str,
        step_key: str,
        artifact_type: str,
        artifact_id: str,
        path: tuple[str | int, ...],
    ) -> ArtifactHandle:
        identity = "|".join((run_id, step_key, artifact_type, artifact_id, *(str(item) for item in path)))
        return cls(
            id=f"artifact:{sha256(identity.encode('utf-8')).hexdigest()[:20]}",
            run_id=run_id,
            step_key=step_key,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            path=path,
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "runId": self.run_id,
            "stepKey": self.step_key,
            "artifactType": self.artifact_type,
            "artifactId": self.artifact_id,
            "path": list(self.path),
        }


@dataclass(frozen=True)
class HandleResolution:
    status: HandleResolutionStatus
    handle: ArtifactHandle
    value: Any = None
    reason: str | None = None

    def to_trace_payload(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "handle": self.handle.to_payload(),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ContextSelection:
    key: str
    value: Any
    handles: tuple[ArtifactHandle, ...] = ()
    available: bool = True
    total_count: int = 0
    selected_count: int = 0
    trimmed_count: int = 0

    def copied_value(self) -> Any:
        return deepcopy(self.value)


@dataclass(frozen=True)
class ProviderDossier:
    profile_id: str
    operation_id: str
    model_role: str
    readiness_status: DossierReadinessStatus
    semantic_contract: SemanticInputContract
    sent: Mapping[str, Any]
    handles: Mapping[str, tuple[ArtifactHandle, ...]]
    sent_counts: Mapping[str, int]
    trimmed_counts: Mapping[str, int]
    suppressed_fields: tuple[str, ...]
    quality_risk: DossierQualityRisk
    missing_required_inputs: tuple[str, ...] = ()
    runtime_migrated: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def provider_input(self) -> dict[str, Any]:
        return {"dossierId": self.profile_id, **deepcopy(dict(self.sent))}

    def to_payload(self) -> dict[str, Any]:
        return {
            "profileId": self.profile_id,
            "operationId": self.operation_id,
            "modelRole": self.model_role,
            "readinessStatus": self.readiness_status.value,
            **self.semantic_contract.to_payload(),
            "sent": deepcopy(dict(self.sent)),
            "handles": {
                key: [handle.to_payload() for handle in values]
                for key, values in sorted(self.handles.items())
            },
            "sentCounts": dict(self.sent_counts),
            "trimmedCounts": dict(self.trimmed_counts),
            "suppressedFields": list(self.suppressed_fields),
            "qualityRisk": self.quality_risk.value,
            "missingRequiredInputs": list(self.missing_required_inputs),
            "runtimeMigrated": self.runtime_migrated,
            "metadata": deepcopy(dict(self.metadata)),
        }


__all__ = (
    "ArtifactHandle",
    "ContextSelection",
    "DossierQualityRisk",
    "DossierReadinessStatus",
    "HandleResolution",
    "HandleResolutionStatus",
    "ProviderDossier",
)
