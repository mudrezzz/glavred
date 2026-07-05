"""Owner: shared.llm_operations

Used by: Shared LLM operation input, timeout, and retry metadata.
Does not own: Domain-specific payload budgets, prompt text, provider adapters, or persistence.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class LlmOperationInputStats:
    prompt_char_estimate: int | None = None
    approx_token_estimate: int | None = None
    rule_count: int | None = None
    evidence_count: int | None = None
    claim_count: int | None = None
    source_count: int | None = None
    candidate_count: int | None = None
    model: str | None = None
    model_role: str | None = None
    generation_params: Mapping[str, Any] | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> "LlmOperationInputStats":
        source = dict(payload or {})
        return cls(
            prompt_char_estimate=_optional_int(source.pop("promptCharEstimate", None)),
            approx_token_estimate=_optional_int(source.pop("approxTokenEstimate", None)),
            rule_count=_optional_int(source.pop("ruleCount", source.get("compactRuleCount"))),
            evidence_count=_optional_int(source.pop("evidenceCount", None)),
            claim_count=_optional_int(source.pop("claimCount", source.get("externalClaimCount"))),
            source_count=_optional_int(source.pop("sourceCount", None)),
            candidate_count=_optional_int(source.pop("candidateCount", None)),
            model=_optional_str(source.pop("model", source.get("selectedModel"))),
            model_role=_optional_str(source.pop("modelRole", None)),
            generation_params=_optional_mapping(source.pop("generationParams", None)),
            extra={key: value for key, value in source.items() if value is not None},
        )

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "promptCharEstimate": self.prompt_char_estimate,
            "approxTokenEstimate": self.approx_token_estimate,
            "ruleCount": self.rule_count,
            "evidenceCount": self.evidence_count,
            "claimCount": self.claim_count,
            "sourceCount": self.source_count,
            "candidateCount": self.candidate_count,
            "model": self.model,
            "modelRole": self.model_role,
            "generationParams": dict(self.generation_params or {}),
        }
        payload.update(dict(self.extra))
        return payload


@dataclass(frozen=True)
class LlmOperationTimeoutProfile:
    profile: str
    attempt_timeout_seconds: float | None = None
    provider_http_timeout_seconds: float | None = None
    step_budget_seconds: float | None = None
    run_budget_seconds: float | None = None
    stale_watchdog_seconds: float | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "attemptTimeoutSeconds": self.attempt_timeout_seconds,
            "providerHttpTimeoutSeconds": self.provider_http_timeout_seconds,
            "stepBudgetSeconds": self.step_budget_seconds,
            "runBudgetSeconds": self.run_budget_seconds,
            "staleWatchdogSeconds": self.stale_watchdog_seconds,
        }


@dataclass(frozen=True)
class LlmOperationRetryPolicy:
    policy: str = "json-primary-repair-backup"
    sequence: tuple[str, ...] = ("primary", "primary-repair", "backup")
    max_attempts: int | None = 3

    def to_payload(self) -> dict[str, Any]:
        return {
            "policy": self.policy,
            "sequence": list(self.sequence),
            "maxAttempts": self.max_attempts,
        }


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_mapping(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None
