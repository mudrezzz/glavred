"""Owner: drafting.application.context

Used by: DraftRunContextAccessService for compact planning, candidate, and issue reads.
Does not own: dossier policy, validation decisions, provider calls, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.app.drafting.application.context.draft_run_artifact_index import DraftRunArtifactIndex
from backend.app.drafting.domain.provider_dossier import ArtifactHandle, ContextSelection


class EditorialContextReader:
    def __init__(self, index: DraftRunArtifactIndex) -> None:
        self._index = index

    def planning(self) -> ContextSelection:
        material = self._mapping(self._mapping(self._index.step_payload("materialPlan")).get("materialPlan"))
        strategy = self._mapping(self._mapping(self._index.step_payload("strategy")).get("draftStrategy"))
        if not material and not strategy:
            return self._missing("planning")
        compact_material, material_trimmed = self._select_bounded_fields(
            material,
            (
                ("groundingPlan", 4),
                ("availableEvidence", 4),
                ("qualifiedClaims", 4),
                ("riskyClaims", 2),
                ("missingEvidence", 2),
                ("claimsRequiringAttribution", 4),
            ),
            text_limit=180,
        )
        compact_strategy, strategy_trimmed = self._select_bounded_fields(
            strategy,
            (
                ("thesisAngle", 1),
                ("openingMove", 1),
                ("argumentSequence", 4),
                ("ctaPlan", 1),
                ("forbiddenMoves", 4),
                ("toneNotes", 3),
            ),
            text_limit=240,
        )
        value = {"material": compact_material, "strategy": compact_strategy}
        handles = tuple(
            handle
            for handle in (
                self._whole_handle("materialPlan", ("materialPlan",), "materialPlan") if material else None,
                self._whole_handle("strategy", ("draftStrategy",), "draftStrategy") if strategy else None,
            )
            if handle is not None
        )
        return ContextSelection("planning", value, handles, total_count=len(handles), selected_count=len(handles), trimmed_count=material_trimmed + strategy_trimmed)

    def material_plan(self) -> ContextSelection:
        payload = self._mapping(self._index.step_payload("materialPlan"))
        material = self._mapping(payload.get("materialPlan"))
        if not material:
            return self._missing("materialPlan")
        compact, trimmed = self._select_bounded_fields(
            material,
            (
                ("groundingPlan", 4),
                ("availableEvidence", 8),
                ("rejectedEvidence", 4),
                ("rejectionReasons", 4),
                ("qualifiedClaims", 6),
                ("riskyClaims", 4),
                ("missingEvidence", 4),
                ("claimsRequiringAttribution", 6),
            ),
            text_limit=200,
        )
        handle = self._whole_handle("materialPlan", ("materialPlan",), "materialPlan")
        return ContextSelection(
            "materialPlan",
            compact,
            (handle,),
            total_count=1,
            selected_count=1,
            trimmed_count=trimmed,
        )

    def draft_strategy(self) -> ContextSelection:
        payload = self._mapping(self._index.step_payload("strategy"))
        strategy = self._mapping(payload.get("draftStrategy"))
        if not strategy:
            return self._missing("draftStrategy")
        compact, trimmed = self._select_bounded(
            strategy,
            (
                "thesisAngle",
                "openingMove",
                "argumentSequence",
                "fabulaUsage",
                "ctaPlan",
                "forbiddenMoves",
                "toneNotes",
            ),
        )
        handle = self._whole_handle("strategy", ("draftStrategy",), "draftStrategy")
        return ContextSelection(
            "draftStrategy",
            compact,
            (handle,),
            total_count=1,
            selected_count=1,
            trimmed_count=trimmed,
        )

    def rhetorical_plan(self, plan_id: str | None) -> ContextSelection:
        payload = self._mapping(self._index.step_payload("rhetoricalPlans"))
        plans = self._records(self._mapping(payload.get("rhetoricalPlanSet")).get("plans"))
        selected_index = next((index for index, plan in enumerate(plans) if str(plan.get("id")) == str(plan_id)), None)
        if selected_index is None:
            return self._missing("rhetoricalPlan")
        plan = plans[selected_index]
        compact, trimmed = self._select_bounded(plan, ("id", "title", "angle", "openingMove", "moves", "claimsToUse", "claimIdsToAvoid", "requiredRuleIds", "ctaRoute", "risks", "sizeIntent"))
        handle = self._handle("rhetoricalPlans", ("rhetoricalPlanSet", "plans", selected_index), "rhetoricalPlan", str(plan.get("id") or "artifact"))
        return ContextSelection("rhetoricalPlan", compact, (handle,), total_count=1, selected_count=1, trimmed_count=trimmed)

    def candidate_summaries(self, limit: int = 4) -> ContextSelection:
        payload = self._mapping(self._index.step_payload("draft"))
        candidates = self._records(payload.get("candidates"))
        selected = candidates[: max(0, limit)]
        values = [self._candidate_summary(candidate) for candidate in selected]
        handles = tuple(
            self._handle("draft", ("candidates", index), "candidate", str(candidate.get("id") or "artifact"))
            for index, candidate in enumerate(selected)
        )
        return ContextSelection(
            "candidates", values, handles, available=bool(candidates), total_count=len(candidates),
            selected_count=len(selected), trimmed_count=max(0, len(candidates) - len(selected)),
        )

    def selected_candidate(self, candidate_id: str | None) -> ContextSelection:
        payload = self._mapping(self._index.step_payload("draft"))
        candidates = self._records(payload.get("candidates"))
        selected_index = next((index for index, item in enumerate(candidates) if str(item.get("id")) == str(candidate_id)), None)
        if selected_index is not None:
            candidate = candidates[selected_index]
            path: tuple[str | int, ...] = ("candidates", selected_index)
            step_key = "draft"
        else:
            validation = self._mapping(self._index.step_payload("validation"))
            ranking = self._mapping(validation.get("rankingRevision"))
            candidate = self._mapping(ranking.get("revisedCandidate"))
            if not candidate or str(candidate.get("id")) != str(candidate_id):
                return self._missing("candidate")
            path = ("rankingRevision", "revisedCandidate")
            step_key = "validation"
        value = self._select(candidate, ("id", "title", "body", "rhetoricalPlanId", "usedEvidence", "ruleCoverage", "risks", "weaknesses"))
        handle = self._handle(step_key, path, "candidate", str(candidate.get("id") or "artifact"))
        return ContextSelection("candidate", value, (handle,), total_count=1, selected_count=1)

    def validation_issues(self, candidate_id: str | None = None, limit: int = 20) -> ContextSelection:
        payload = self._mapping(self._index.step_payload("validation"))
        reports = self._records(payload.get("candidateReports"))
        records: list[tuple[dict[str, Any], ArtifactHandle]] = []
        for report_index, report in enumerate(reports):
            if candidate_id and str(report.get("candidateId")) != str(candidate_id):
                continue
            for finding_index, finding in enumerate(self._records(report.get("findings"))):
                compact = self._select(finding, ("validatorId", "severity", "message", "repairGuidance", "status", "source"))
                compact["candidateId"] = report.get("candidateId")
                artifact_id = str(
                    finding.get("id")
                    or (
                        f"{finding.get('candidateId')}:{finding.get('validatorId')}"
                        if finding.get("candidateId") and finding.get("validatorId")
                        else finding.get("validatorId")
                    )
                    or f"finding-{finding_index}"
                )
                records.append((compact, self._handle("validation", ("candidateReports", report_index, "findings", finding_index), "validationIssue", artifact_id)))
        records.sort(key=lambda item: (str(item[0].get("severity") or ""), str(item[0].get("validatorId") or "")))
        return self._limited("validationIssues", records, limit, source_available=bool(reports))

    def final_quality_lifecycle(self, limit: int = 20) -> ContextSelection:
        complete = self._mapping(self._index.step_payload("complete"))
        quality = self._mapping(complete.get("qualityFidelity"))
        lifecycle = self._mapping(quality.get("issueLifecycle"))
        items = self._records(lifecycle.get("items"))
        selected = items[: max(0, limit)]
        handles = tuple(
            self._handle("complete", ("qualityFidelity", "issueLifecycle", "items", index), "finalQualityIssue", str(item.get("id") or item.get("validatorId") or f"issue-{index}"))
            for index, item in enumerate(selected)
        )
        value = {
            "status": quality.get("editorialStatus"),
            "overallVerdict": quality.get("overallVerdict"),
            "items": [self._select(item, ("id", "validatorId", "severity", "status", "source", "message", "reason")) for item in selected],
        }
        return ContextSelection(
            "finalQualityIssues", value, handles, available=bool(quality), total_count=len(items),
            selected_count=len(selected), trimmed_count=max(0, len(items) - len(selected)),
        )

    def repair_history(self) -> ContextSelection:
        validation = self._mapping(self._index.step_payload("validation"))
        ranking = self._mapping(validation.get("rankingRevision"))
        loop = self._mapping(ranking.get("revisionLoop"))
        cycles = self._records(loop.get("cycles"))
        value = {
            "status": loop.get("status"),
            "stopReason": loop.get("stopReason"),
            "cycles": [self._select(item, ("cycle", "status", "accepted", "reason", "candidateId")) for item in cycles[:6]],
        }
        handle = self._whole_handle("validation", ("rankingRevision", "revisionLoop"), "revisionLoop") if loop else None
        return ContextSelection("repairHistory", value if loop else None, (handle,) if handle else (), available=bool(loop), total_count=len(cycles), selected_count=min(len(cycles), 6), trimmed_count=max(0, len(cycles) - 6))

    def _candidate_summary(self, candidate: Mapping[str, Any]) -> dict[str, Any]:
        body = str(candidate.get("body") or "")
        return {
            **self._select(candidate, ("id", "title", "rhetoricalPlanId")),
            "risks": [self._bounded_value_to(item, 240) for item in self._records_or_values(candidate.get("risks"))[:2]],
            "weaknesses": [self._bounded_value_to(item, 240) for item in self._records_or_values(candidate.get("weaknesses"))[:2]],
            "usedEvidence": [self._bounded_value_to(item, 160) for item in self._records_or_values(candidate.get("usedEvidence"))[:6]],
            "bodyExcerpt": body[:360],
            "bodyChars": len(body),
        }

    def _records_or_values(self, value: Any) -> list[Any]:
        return list(value) if isinstance(value, list) else []

    def _limited(self, key: str, records: list[tuple[dict[str, Any], ArtifactHandle]], limit: int, *, source_available: bool) -> ContextSelection:
        selected = records[: max(0, limit)]
        return ContextSelection(key, [item for item, _ in selected], tuple(handle for _, handle in selected), source_available, len(records), len(selected), max(0, len(records) - len(selected)))

    def _whole_handle(self, step_key: str, path: tuple[str | int, ...], artifact_type: str) -> ArtifactHandle:
        return self._handle(step_key, path, artifact_type, "artifact")

    def _handle(self, step_key: str, path: tuple[str | int, ...], artifact_type: str, artifact_id: str) -> ArtifactHandle:
        return ArtifactHandle.create(run_id=self._index.run_id, step_key=step_key, artifact_type=artifact_type, artifact_id=artifact_id, path=path)

    def _missing(self, key: str) -> ContextSelection:
        return ContextSelection(key, None, available=False)

    def _select(self, value: Mapping[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
        return {key: value.get(key) for key in keys if value.get(key) not in (None, [], {})}

    def _select_bounded(self, value: Mapping[str, Any], keys: tuple[str, ...]) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        trimmed = 0
        for key in keys:
            item = value.get(key)
            if item in (None, [], {}):
                continue
            if isinstance(item, str):
                result[key] = item[:600]
            elif isinstance(item, list):
                result[key] = [self._bounded_value(child) for child in item[:6]]
                trimmed += max(0, len(item) - 6)
            else:
                result[key] = self._bounded_value(item)
        return result, trimmed

    def _select_bounded_fields(
        self,
        value: Mapping[str, Any],
        fields: tuple[tuple[str, int], ...],
        *,
        text_limit: int,
    ) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        trimmed = 0
        for key, list_limit in fields:
            item = value.get(key)
            if item in (None, [], {}):
                continue
            if isinstance(item, str):
                result[key] = item[:text_limit]
                trimmed += int(len(item) > text_limit)
            elif isinstance(item, list):
                result[key] = [self._bounded_value_to(child, text_limit) for child in item[:list_limit]]
                trimmed += max(0, len(item) - list_limit)
            else:
                result[key] = self._bounded_value_to(item, text_limit)
        return result, trimmed

    def _bounded_value_to(self, value: Any, text_limit: int) -> Any:
        if isinstance(value, str):
            return value[:text_limit]
        if isinstance(value, Mapping):
            return {
                str(key): self._bounded_value_to(child, text_limit)
                for key, child in list(value.items())[:12]
            }
        if isinstance(value, list):
            return [self._bounded_value_to(child, text_limit) for child in value[:6]]
        return value

    def _bounded_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return value[:600]
        if isinstance(value, Mapping):
            return {str(key): self._bounded_value(child) for key, child in list(value.items())[:12]}
        if isinstance(value, list):
            return [self._bounded_value(child) for child in value[:6]]
        return value

    def _mapping(self, value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    def _records(self, value: Any) -> list[dict[str, Any]]:
        return [dict(item) for item in value if isinstance(item, Mapping)] if isinstance(value, list) else []


__all__ = ("EditorialContextReader",)
