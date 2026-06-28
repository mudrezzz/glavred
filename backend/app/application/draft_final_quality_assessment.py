import re
from typing import Any

from backend.app.application.draft_final_quality_attribution import attribution_finding_split, effective_finding_counts, is_actionable_finding


INTERNAL_TERMS = ("SourceLedger", "publicEvidence", "validators", "PostContract", "RuleRegistry")
SOURCE_MARKERS = ("по данным", "исслед", "отчет", "report", "survey", "http", ".com", ".org", "gartner", "mckinsey", "bcg")
INTERPRETATION_MARKERS = ("значит", "поэтому", "вывод", "это означает", "на практике", "главное", "мой тезис", "я считаю", "мы видим")
VALUE_MARKERS = ("если вы", "проверь", "начните", "стоит", "вывод", "что делать", "почему это важно", "на практике")


def gate_payload(candidate: dict[str, Any] | None, validation_report: dict[str, Any], context_artifact: dict[str, Any], stop_reason: str) -> dict[str, Any]:
    body = str((candidate or {}).get("body") or "")
    report = candidate_report(validation_report, str((candidate or {}).get("id") or ""))
    effective = effective_finding_counts(report)
    attribution = attribution_finding_split(report)
    leaks = internal_jargon_leaks(body)
    source_dump = source_dump_risk(body, context_artifact)
    voice = "passed" if _has_any(body.lower(), ("я ", "мы ", "мой тезис", "я считаю", "важно", "ошибка", "не ", "а ")) else "warning"
    value = "passed" if _has_any(body.lower(), VALUE_MARKERS) else "warning"
    deterministic = "critical" if effective["criticalCount"] > 0 else "warning" if effective["warningCount"] > 0 else "passed"
    public_prose = "critical" if leaks else "warning" if source_dump["status"] != "passed" else "passed"
    source_status = "warning" if attribution["actionableAttributionFindings"] or source_dump["status"] != "passed" else "passed"
    status = worst([deterministic, public_prose, source_status, voice, value])
    return {
        "status": status,
        "finalDraftStatus": deterministic,
        "publicProseStatus": public_prose,
        "sourceIntegrationStatus": source_status,
        "internalJargonLeaks": leaks,
        "sourceDumpRisk": source_dump,
        "authorVoiceStrength": voice,
        "readerValueClarity": value,
        "finalRepairGoals": repair_goals(leaks, source_dump, voice, value, report),
        "actionableAttributionFindings": attribution["actionableAttributionFindings"],
        "diagnosticAttributionNoise": attribution["diagnosticAttributionNoise"],
        "revisionLoopStopReason": stop_reason,
        "candidateId": (candidate or {}).get("id"),
    }


def repair_instruction(candidate: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "created",
        "candidateId": candidate.get("id"),
        "repairGoals": gate.get("finalRepairGoals") or [],
        "sourceFindings": [],
        "constraints": [
            "Do not mention internal pipeline names such as SourceLedger, publicEvidence, validators, PostContract, or RuleRegistry.",
            "Do not turn the post into a list or inventory of sources.",
            "Keep source markers required for public factual claims.",
            "Do not strengthen claims beyond approved ledger/public evidence.",
        ],
        "reason": "final-quality-gate-requested-public-prose-repair",
    }


def repair_rejection_reasons(initial: dict[str, Any], repaired: dict[str, Any] | None, regression: dict[str, Any]) -> list[str]:
    if not repaired:
        return ["final-repair-not-created"]
    reasons: list[str] = []
    if not regression.get("accepted"):
        reasons.extend(_strings(regression.get("reasons")))
    if severity(repaired.get("status")) > severity(initial.get("status")):
        reasons.append("final-gate-status-regressed")
    if len(_list(repaired.get("internalJargonLeaks"))) >= len(_list(initial.get("internalJargonLeaks"))) and _list(initial.get("internalJargonLeaks")):
        reasons.append("internal-jargon-not-improved")
    if severity(_dict(repaired.get("sourceDumpRisk")).get("status")) > severity(_dict(initial.get("sourceDumpRisk")).get("status")):
        reasons.append("source-dump-risk-regressed")
    return reasons


def repair_goals(leaks: list[dict[str, Any]], source_dump: dict[str, Any], voice: str, value: str, report: dict[str, Any]) -> list[str]:
    goals: list[str] = []
    if leaks:
        goals.append("Remove or translate internal pipeline jargon into reader-facing prose.")
    if source_dump.get("status") != "passed":
        goals.append("Turn source inventory into an author argument with interpretation.")
    if voice != "passed":
        goals.append("Strengthen author stance without inventing unsupported claims.")
    if value != "passed":
        goals.append("Make reader value and practical takeaway explicit.")
    goals.extend(str(item.get("repairGuidance")) for item in _list(report.get("findings"))[:4] if isinstance(item, dict) and item.get("repairGuidance") and is_actionable_finding(item))
    return goals[:8]


def internal_jargon_leaks(body: str) -> list[dict[str, Any]]:
    return [{"term": term, "excerpt": _excerpt(body, term)} for term in INTERNAL_TERMS if term.lower() in body.lower()]


def source_dump_risk(body: str, context_artifact: dict[str, Any]) -> dict[str, Any]:
    sentences = [item.strip() for item in re.split(r"[.!?\n]+", body) if item.strip()]
    source_count = sum(1 for item in sentences if _has_any(item.lower(), SOURCE_MARKERS) or re.search(r"\b20\d{2}\b", item))
    interpretation_count = sum(1 for item in sentences if _has_any(item.lower(), INTERPRETATION_MARKERS))
    depth = str(_dict(_dict(context_artifact.get("draftContext")).get("fabula")).get("researchDepth") or _dict(context_artifact.get("fabula")).get("researchDepth") or "standard")
    threshold = {"light": 3, "standard": 5, "deep": 8, "marketResearch": 12}.get(depth, 5)
    risky = source_count >= threshold and interpretation_count < max(2, source_count // 4)
    return {"status": "warning" if risky else "passed", "sourceSentenceCount": source_count, "interpretationSentenceCount": interpretation_count, "threshold": threshold, "researchDepth": depth}


def candidate_report(report: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    reports = _list(report.get("candidateReports"))
    return next((_dict(item) for item in reports if _dict(item).get("candidateId") == candidate_id), _dict(reports[0]) if reports else {})


def worst(statuses: list[Any]) -> str:
    return max((str(item or "passed") for item in statuses), key=severity)


def severity(status: Any) -> int:
    return {"passed": 0, "clean": 0, "warning": 1, "critical": 2}.get(str(status or "passed"), 0)


def _has_any(value: str, markers: tuple[str, ...]) -> bool:
    return any(marker in value for marker in markers)


def _excerpt(body: str, needle: str) -> str:
    index = body.lower().find(needle.lower())
    return body[max(0, index - 80): index + len(needle) + 120] if index >= 0 else body[:180]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [str(item) for item in _list(value) if str(item).strip()]


def _int(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) else 0
