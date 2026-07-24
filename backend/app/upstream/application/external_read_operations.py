"""Owner: upstream.application

Used by: UpstreamRadarExternalRunService for direct and triage-selected URL reads.
Does not own: read allocation, provider search, run status, persistence, or downstream signals.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any

from backend.app.application.public_evidence_ports import PublicUrlReader
from backend.app.upstream.application.external_run_payloads import UpstreamRadarPayloadFactory
from backend.app.upstream.domain.search_read_contracts import SearchReadOutcome


class RadarUrlReadOperationRunner:
    def __init__(self, *, url_reader: PublicUrlReader) -> None:
        self._url_reader = url_reader
        self._payloads = UpstreamRadarPayloadFactory()

    def read_direct_handle(
        self,
        *,
        run_id: str,
        handle: dict[str, Any],
        started_at: str,
    ) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        operation_id = f"{run_id}-read-{handle.get('id')}"
        title = str(handle.get("title") or handle.get("locator") or "URL")
        target = str(handle.get("locator") or "")
        try:
            read = self._url_reader.read(target)
            material_id = f"{run_id}-material-{self._payloads.stable_slug(str(handle.get('id') or 'url'))}"
            material = self._payloads.material_from_read(
                material_id=material_id,
                run_id=run_id,
                source_handle_id=str(handle["id"]),
                title=title,
                read=read,
                provenance=title,
            )
            return material, self._operation(
                run_id=run_id,
                operation_id=operation_id,
                source_handle_id=str(handle["id"]),
                label=title,
                status="succeeded",
                started_at=started_at,
                target=target,
                found_material_ids=[material_id],
            )
        except Exception as exc:
            error = self._payloads.safe_error(exc)
            return None, self._operation(
                run_id=run_id,
                operation_id=operation_id,
                source_handle_id=str(handle["id"]),
                label=title,
                status="failed",
                started_at=started_at,
                target=target,
                error=error,
            )

    def read_selection(
        self,
        *,
        run_id: str,
        selection: dict[str, Any],
        raw_results: list[dict[str, Any]],
        started_at: str,
    ) -> tuple[dict[str, Any], dict[str, Any], SearchReadOutcome]:
        raw = next(item for item in raw_results if item["id"] == selection["rawResultId"])
        slug_source = str(selection.get("duplicateGroupId") or raw["duplicateKey"])
        material_id = f"{run_id}-material-{self._payloads.stable_slug(slug_source)}"
        operation_id = f"{run_id}-read-{material_id}"
        discovery_trace = self._discovery_trace(selection=selection, raw=raw)
        try:
            read = self._url_reader.read(raw["url"])
            material = self._payloads.material_from_read(
                material_id=material_id,
                run_id=run_id,
                source_handle_id=raw["sourceHandleId"],
                title=raw["title"],
                read=read,
                provenance=f"{raw['provider']} / {raw['domain']}",
                discovery_trace=discovery_trace,
                focus_text=str(raw.get("snippet") or ""),
            )
            read_operation = self._operation(
                run_id=run_id,
                operation_id=operation_id,
                source_handle_id=raw["sourceHandleId"],
                label=raw["title"],
                status="succeeded",
                started_at=started_at,
                target=raw["url"],
                found_material_ids=[material_id],
            )
            outcome = self._outcome(selection, raw, material_id, status="succeeded", readable=True)
        except Exception as exc:
            error = self._payloads.safe_error(exc)
            material = self._payloads.material_from_raw(
                material_id=material_id,
                run_id=run_id,
                raw=raw,
                warning=f"url-read-failed:{error}",
                discovery_trace=discovery_trace,
            )
            read_operation = self._operation(
                run_id=run_id,
                operation_id=operation_id,
                source_handle_id=raw["sourceHandleId"],
                label=raw["title"],
                status="failed",
                started_at=started_at,
                target=raw["url"],
                found_material_ids=[material_id],
                error=error,
            )
            outcome = self._outcome(
                selection,
                raw,
                material_id,
                status="failed",
                readable=False,
                reason="url-read-failed",
            )
        return material, read_operation, outcome

    def _operation(self, **values: Any) -> dict[str, Any]:
        return self._payloads.operation(kind="readUrl", **values)

    def _outcome(
        self,
        selection: dict[str, Any],
        raw: dict[str, Any],
        material_id: str,
        *,
        status: str,
        readable: bool,
        reason: str | None = None,
    ) -> SearchReadOutcome:
        return SearchReadOutcome(
            raw_result_id=str(raw["id"]),
            candidate_id=str(selection.get("candidateId") or raw.get("candidateId") or ""),
            duplicate_group_id=selection.get("duplicateGroupId"),
            status=status,
            material_id=material_id,
            readable=readable,
            reason=reason,
        )

    def _discovery_trace(self, *, selection: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
        return {
            "rawResultIds": list(selection.get("duplicateRawResultIds") or [raw["id"]]),
            "queryIds": list(selection.get("queryIds") or ([raw.get("queryId")] if raw.get("queryId") else [])),
            "intentIds": list(selection.get("intentIds") or ([raw.get("intentId")] if raw.get("intentId") else [])),
            "families": list(selection.get("families") or ([raw.get("family")] if raw.get("family") else [])),
            "evidenceTypes": list(selection.get("evidenceTypes") or ([raw.get("evidenceType")] if raw.get("evidenceType") else [])),
            "requirementIds": list(selection.get("requirementIds") or raw.get("requirementIds") or []),
            "discoveredRequirementIds": list(
                selection.get("discoveredRequirementIds")
                or selection.get("requirementIds")
                or raw.get("discoveredRequirementIds")
                or raw.get("requirementIds")
                or []
            ),
            "supportedRequirementIds": list(
                selection.get("supportedRequirementIds")
                or raw.get("supportedRequirementIds")
                or []
            ),
            "duplicateGroupId": selection.get("duplicateGroupId"),
            "decisionReason": selection.get("reason"),
            "queryLanguage": raw.get("queryLanguage"),
            "sourceLanguage": selection.get("sourceLanguage") or raw.get("sourceLanguage"),
        }


__all__ = ("RadarUrlReadOperationRunner",)
