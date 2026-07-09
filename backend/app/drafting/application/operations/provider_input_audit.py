"""Owner: drafting.application.operations

Used by: DraftRun provider-input budget audit CLI and architecture tests.
Does not own: provider calls, prompt construction, DraftRun persistence, or roadmap policy.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from backend.app.domain.ai_run import AiRun
from backend.app.drafting.application.operations.provider_input_audit_contracts import (
    TARGET_PROVIDER_INPUT_OPERATIONS,
    TRACE_ALIASES,
    ProviderInputAuditFinding,
    ProviderInputAuditReport,
    ProviderInputBudgetDebt,
)
from backend.app.drafting.application.operations.provider_input_audit_debt import (
    DEFAULT_PROVIDER_INPUT_BUDGET_DEBTS,
)


class ProviderInputAudit:
    def __init__(
        self,
        *,
        debts: Mapping[str, ProviderInputBudgetDebt] | None = None,
        target_operations: Iterable[str] = TARGET_PROVIDER_INPUT_OPERATIONS,
    ) -> None:
        self._debts = dict(debts or DEFAULT_PROVIDER_INPUT_BUDGET_DEBTS)
        self._targets = tuple(target_operations)

    def audit_ai_runs(self, ai_runs: Iterable[AiRun]) -> ProviderInputAuditReport:
        findings: list[ProviderInputAuditFinding] = []
        seen: set[str] = set()
        for ai_run in ai_runs:
            operation_id = self._operation_id(ai_run.request_payload)
            if operation_id not in self._targets:
                continue
            seen.add(operation_id)
            findings.append(self._finding_for_ai_run(ai_run, operation_id))
        for operation_id in self._targets:
            if operation_id in seen:
                continue
            if debt := self._debts.get(operation_id):
                findings.append(_debt_finding(operation_id, debt, ai_run_id=None, draft_run_step=None))
        return ProviderInputAuditReport(tuple(findings))

    def _finding_for_ai_run(self, ai_run: AiRun, operation_id: str) -> ProviderInputAuditFinding:
        request_payload = ai_run.request_payload
        direct_budget = _dict(request_payload.get("payloadBudget"))
        nested_budget = _find_nested_payload_budget(request_payload)
        draft_run_step = _optional_str(request_payload.get("draftRunStep"))
        if not direct_budget:
            if debt := self._debts.get(operation_id):
                return _debt_finding(operation_id, debt, ai_run_id=ai_run.id, draft_run_step=draft_run_step)
            if nested_budget:
                return ProviderInputAuditFinding(
                    operation_id=operation_id,
                    status="nestedBudgetFalsePositive",
                    ai_run_id=ai_run.id,
                    draft_run_step=draft_run_step,
                    profile_id=_optional_str(nested_budget.get("profileId")),
                    reason="nested payloadBudget exists, but current child AiRun has no direct payloadBudget proof",
                )
            return ProviderInputAuditFinding(
                operation_id=operation_id,
                status="missingDirectBudget",
                ai_run_id=ai_run.id,
                draft_run_step=draft_run_step,
                profile_id=None,
                reason="current child AiRun requestPayload has no direct payloadBudget",
            )
        return _budgeted_finding(ai_run.id, operation_id, draft_run_step, direct_budget)

    def _operation_id(self, request_payload: Mapping[str, Any]) -> str:
        raw = _optional_str(request_payload.get("operationId")) or _optional_str(request_payload.get("draftRunStep")) or ""
        return TRACE_ALIASES.get(raw, raw)


def _budgeted_finding(
    ai_run_id: str,
    operation_id: str,
    draft_run_step: str | None,
    direct_budget: Mapping[str, Any],
) -> ProviderInputAuditFinding:
    profile_id = _optional_str(direct_budget.get("profileId"))
    prompt_chars = _optional_int(direct_budget.get("promptCharEstimate"))
    approx_tokens = _optional_int(direct_budget.get("approxTokenEstimate"))
    max_prompt_chars = _optional_int(_dict(direct_budget.get("limits")).get("maxPromptChars"))
    incident_type = _optional_str(_dict(direct_budget.get("incident")).get("incidentType"))
    over_limit = prompt_chars is not None and max_prompt_chars is not None and prompt_chars > max_prompt_chars
    if incident_type or over_limit:
        return ProviderInputAuditFinding(
            operation_id=operation_id,
            status="overBudget",
            ai_run_id=ai_run_id,
            draft_run_step=draft_run_step,
            profile_id=profile_id,
            reason=incident_type or "promptCharEstimate exceeds maxPromptChars",
            prompt_char_estimate=prompt_chars,
            approx_token_estimate=approx_tokens,
            max_prompt_chars=max_prompt_chars,
        )
    return ProviderInputAuditFinding(
        operation_id=operation_id,
        status="directlyBudgeted",
        ai_run_id=ai_run_id,
        draft_run_step=draft_run_step,
        profile_id=profile_id,
        reason="current child AiRun requestPayload has direct payloadBudget proof",
        prompt_char_estimate=prompt_chars,
        approx_token_estimate=approx_tokens,
        max_prompt_chars=max_prompt_chars,
    )


def _debt_finding(
    operation_id: str,
    debt: ProviderInputBudgetDebt,
    *,
    ai_run_id: str | None,
    draft_run_step: str | None,
) -> ProviderInputAuditFinding:
    return ProviderInputAuditFinding(
        operation_id=operation_id,
        status="explicitDebt",
        ai_run_id=ai_run_id,
        draft_run_step=draft_run_step,
        profile_id=None,
        reason=debt.reason,
        debt=debt,
    )


def _find_nested_payload_budget(value: Any, *, top_level: bool = True) -> dict[str, Any] | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "payloadBudget" and not top_level and isinstance(child, dict):
                return child
            if found := _find_nested_payload_budget(child, top_level=False):
                return found
    if isinstance(value, list):
        for child in value:
            if found := _find_nested_payload_budget(child, top_level=False):
                return found
    return None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    result = str(value).strip()
    return result or None


__all__ = (
    "DEFAULT_PROVIDER_INPUT_BUDGET_DEBTS",
    "TARGET_PROVIDER_INPUT_OPERATIONS",
    "ProviderInputAudit",
    "ProviderInputAuditFinding",
    "ProviderInputAuditReport",
    "ProviderInputBudgetDebt",
)
