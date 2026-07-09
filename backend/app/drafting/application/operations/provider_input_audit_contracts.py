"""Owner: drafting.application.operations

Used by: Provider-input budget audit policy, CLI, and tests.
Does not own: audit decisions, provider calls, prompt construction, or persistence.
Architecture doc: docs/architecture/DRAFT_RUN_PIPELINE_TO_BE_2_17_4_6_1_3_5.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

TARGET_PROVIDER_INPUT_OPERATIONS: tuple[str, ...] = (
    "pairwiseRanking",
    "materialPlan",
    "draftCandidate",
    "alternativeAngleRoute",
    "alternativeAngleCandidate",
    "strategy",
    "llmValidation",
    "rhetoricalPlans",
    "finalQualityGateReview",
)

PROFILE_ALIASES = {
    "strategy": "draftStrategy",
    "finalQualityGateReview": "finalQualityReviewRepair",
}

TRACE_ALIASES = {value: key for key, value in PROFILE_ALIASES.items()}


@dataclass(frozen=True)
class ProviderInputBudgetDebt:
    operation_id: str
    owner: str
    reason: str
    risk: str
    repair_slice: str

    def to_payload(self) -> dict[str, str]:
        return {
            "operationId": self.operation_id,
            "owner": self.owner,
            "reason": self.reason,
            "risk": self.risk,
            "repairSlice": self.repair_slice,
        }


@dataclass(frozen=True)
class ProviderInputAuditFinding:
    operation_id: str
    status: str
    ai_run_id: str | None
    draft_run_step: str | None
    profile_id: str | None
    reason: str
    prompt_char_estimate: int | None = None
    approx_token_estimate: int | None = None
    max_prompt_chars: int | None = None
    debt: ProviderInputBudgetDebt | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "operationId": self.operation_id,
            "status": self.status,
            "aiRunId": self.ai_run_id,
            "draftRunStep": self.draft_run_step,
            "profileId": self.profile_id,
            "reason": self.reason,
        }
        for key, value in (
            ("promptCharEstimate", self.prompt_char_estimate),
            ("approxTokenEstimate", self.approx_token_estimate),
            ("maxPromptChars", self.max_prompt_chars),
        ):
            if value is not None:
                payload[key] = value
        if self.debt is not None:
            payload["debt"] = self.debt.to_payload()
        return payload


@dataclass(frozen=True)
class ProviderInputAuditReport:
    findings: tuple[ProviderInputAuditFinding, ...]

    def to_payload(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for finding in self.findings:
            counts[finding.status] = counts.get(finding.status, 0) + 1
        clean = all(
            counts.get(status, 0) == 0
            for status in ("missingDirectBudget", "nestedBudgetFalsePositive", "overBudget", "explicitDebt")
        )
        return {
            "version": "draft-run-provider-input-audit-v1",
            "summary": {
                "targetOperations": list(TARGET_PROVIDER_INPUT_OPERATIONS),
                "findingCount": len(self.findings),
                "statusCounts": counts,
                "clean": clean,
            },
            "findings": [finding.to_payload() for finding in self.findings],
        }

    def to_markdown(self) -> str:
        payload = self.to_payload()
        lines = ["# DraftRun Provider Input Audit", ""]
        lines.append(f"- clean: `{str(payload['summary']['clean']).lower()}`")
        for status, count in sorted(payload["summary"]["statusCounts"].items()):
            lines.append(f"- {status}: {count}")
        lines.append("")
        lines.append("| operation | status | aiRun | reason |")
        lines.append("| --- | --- | --- | --- |")
        for item in payload["findings"]:
            lines.append(
                f"| `{item['operationId']}` | `{item['status']}` | `{item.get('aiRunId') or '-'}` | {item['reason']} |"
            )
        return "\n".join(lines)


__all__ = (
    "PROFILE_ALIASES",
    "TARGET_PROVIDER_INPUT_OPERATIONS",
    "TRACE_ALIASES",
    "ProviderInputAuditFinding",
    "ProviderInputAuditReport",
    "ProviderInputBudgetDebt",
)
