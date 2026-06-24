from dataclasses import dataclass, field
from typing import Any


EXCLUDED_PENALTY = 999
FALLBACK_PROVIDER_ALTERNATIVE_PENALTY = 500
FALLBACK_ONLY_PENALTY = 120


@dataclass(frozen=True)
class DraftCandidatePublishability:
    publishable: bool
    selection_status: str
    selection_penalty: int
    selection_reasons: list[str] = field(default_factory=list)


class DraftCandidatePublishabilityPolicy:
    def has_publishable_provider_candidate(self, candidates: list[dict[str, Any]]) -> bool:
        return any(
            not _is_fallback(candidate) and self.evaluate(candidate, provider_alternative_exists=False).publishable
            for candidate in candidates
        )

    def evaluate(self, candidate: dict[str, Any], *, provider_alternative_exists: bool) -> DraftCandidatePublishability:
        title = str(candidate.get("title") or "")
        body = str(candidate.get("body") or "")
        weaknesses = _strings(candidate.get("weaknesses"))
        reasons: list[str] = []

        if not title.strip():
            reasons.append("empty-title")
        if not body.strip():
            reasons.append("empty-body")
        if _contains_raw_artifact_dump(title) or _contains_raw_artifact_dump(body):
            reasons.append("raw-artifact-dump")
        if _contains_mojibake(title) or _contains_mojibake(body):
            reasons.append("mojibake-text")
        if any("needs provider rewrite before publication" in weakness.lower() for weakness in weaknesses):
            reasons.append("needs-provider-rewrite")

        if reasons:
            return DraftCandidatePublishability(
                publishable=False,
                selection_status="excluded",
                selection_penalty=EXCLUDED_PENALTY,
                selection_reasons=reasons,
            )

        if _is_fallback(candidate) and provider_alternative_exists:
            return DraftCandidatePublishability(
                publishable=False,
                selection_status="excluded",
                selection_penalty=FALLBACK_PROVIDER_ALTERNATIVE_PENALTY,
                selection_reasons=["fallback-candidate-provider-alternative"],
            )

        if _is_fallback(candidate):
            return DraftCandidatePublishability(
                publishable=True,
                selection_status="penalized",
                selection_penalty=FALLBACK_ONLY_PENALTY,
                selection_reasons=["fallback-candidate"],
            )

        return DraftCandidatePublishability(
            publishable=True,
            selection_status="eligible",
            selection_penalty=0,
            selection_reasons=[],
        )


def _is_fallback(candidate: dict[str, Any]) -> bool:
    return candidate.get("fallbackUsed") is True or str(candidate.get("source") or "") == "deterministicFallback"


def _contains_raw_artifact_dump(text: str) -> bool:
    needles = ["{'id':", '"id":', "'type':", '"type":', "[{'", '[{"', "OrderedDict("]
    return any(needle in text for needle in needles)


def _contains_mojibake(text: str) -> bool:
    markers = ["СЃ", "С‚", "Рє", "Рѕ", "Рё", "Р°", "Рґ", "Р»"]
    return sum(1 for marker in markers if marker in text) >= 3


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
