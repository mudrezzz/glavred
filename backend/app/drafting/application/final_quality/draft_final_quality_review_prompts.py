"""Owner: drafting.application.final_quality

Used by: DraftRun final_quality package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any


FINAL_QUALITY_REVIEW_KEYS = {
    "status",
    "summary",
    "findings",
    "observations",
    "repairGoals",
    "publicProseStatus",
    "sourceIntegrationStatus",
    "authorVoiceStrength",
    "readerValueClarity",
}

FINAL_QUALITY_REVIEW_TEMPERATURE = 0.2


def build_final_quality_review_messages(
    *,
    candidate: dict[str, Any],
    contract: dict[str, Any],
    deterministic_gate: dict[str, Any],
    validation_report: dict[str, Any],
    repair_context: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    system = (
        "You are Glavred's independent final editor. Review only the delivered public post. "
        "Use the FinalQualityContract as the source of criteria. Do not impose generic taste: "
        "research-heavy fabulas may cite more sources, opinion posts should foreground author voice. "
        "Return strict JSON only."
    )
    user = {
        "task": "Review final public prose against the contract.",
        "requiredJsonShape": {
            "status": "passed|warning|critical",
            "summary": "short explanation",
            "publicProseStatus": "passed|warning|critical",
            "sourceIntegrationStatus": "passed|warning|critical",
            "authorVoiceStrength": "passed|warning|critical",
            "readerValueClarity": "passed|warning|critical",
            "findings": [
                {
                    "id": "stable-id",
                    "severity": "warning|critical",
                    "message": "actionable issue",
                    "evidenceExcerpt": "short quote from the post",
                    "repairGuidance": "specific repair instruction",
                    "contractCriterion": "criterion from FinalQualityContract",
                }
            ],
            "observations": [{"message": "positive or neutral observation"}],
            "repairGoals": ["goal for writer if repair is needed"],
        },
        "candidate": {
            "id": candidate.get("id"),
            "title": candidate.get("title"),
            "body": candidate.get("body"),
        },
        "finalQualityContract": contract,
        "deterministicGate": deterministic_gate,
        "validationReport": validation_report,
        "repairContext": repair_context,
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": _jsonish(user)},
    ]


def _jsonish(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, indent=2)
