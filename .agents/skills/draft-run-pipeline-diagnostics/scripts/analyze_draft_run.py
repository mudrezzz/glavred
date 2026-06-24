#!/usr/bin/env python3
"""Summarize a Glavred DraftRun from local SQLite trace stores."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any


STEP_ORDER = [
    "context",
    "sourceIntent",
    "publicEvidence",
    "feasibility",
    "postContract",
    "rulePack",
    "materialPlan",
    "strategy",
    "rhetoricalPlans",
    "draft",
    "validation",
    "complete",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize one Glavred DraftRun trace.")
    parser.add_argument("run_id", help="DraftRun id")
    parser.add_argument("--draft-db", default="var/glavred-draft-runs.sqlite3")
    parser.add_argument("--ai-db", default="var/glavred-ai-runs.sqlite3")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    args = parser.parse_args()

    summary = build_summary(args.run_id, Path(args.draft_db), Path(args.ai_db))
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_markdown(summary)
    return 0 if summary.get("found") else 1


def build_summary(run_id: str, draft_db: Path, ai_db: Path) -> dict[str, Any]:
    if not draft_db.exists():
        return {"found": False, "runId": run_id, "error": f"DraftRun DB not found: {draft_db}"}
    with sqlite3.connect(draft_db) as con:
        con.row_factory = sqlite3.Row
        run = con.execute("select * from draft_runs where id=?", (run_id,)).fetchone()
        if not run:
            return {"found": False, "runId": run_id, "error": "DraftRun not found"}
        steps = [
            row_to_step(row)
            for row in con.execute(
                "select * from draft_run_steps where run_id=? order by sort_order, step_key",
                (run_id,),
            )
        ]
    ai_run_ids = safe_json(run["ai_run_ids"], [])
    ai_runs = load_ai_runs(ai_db, ai_run_ids)
    final_draft = safe_json(run["final_draft"], None)
    draft_step = next((step for step in steps if step["key"] == "draft"), None)
    public_evidence_step = next((step for step in steps if step["key"] == "publicEvidence"), None)
    source_intent_step = next((step for step in steps if step["key"] == "sourceIntent"), None)
    findings = build_findings(steps, ai_runs, draft_step, public_evidence_step, final_draft)
    return {
        "found": True,
        "runId": run["id"],
        "status": run["status"],
        "createdAt": run["created_at"],
        "updatedAt": run["updated_at"],
        "hasFinalDraft": bool(final_draft),
        "finalDraft": draft_brief(final_draft),
        "steps": steps,
        "sourceIntent": source_intent_summary(source_intent_step),
        "publicEvidence": public_evidence_summary(public_evidence_step),
        "draft": draft_summary(draft_step),
        "aiRuns": ai_runs,
        "findings": findings,
    }


def row_to_step(row: sqlite3.Row) -> dict[str, Any]:
    artifact = safe_json(row["artifact_payload"], {})
    return {
        "key": row["step_key"],
        "title": row["title"],
        "status": row["status"],
        "error": row["error"],
        "startedAt": row["started_at"],
        "completedAt": row["completed_at"],
        "artifact": artifact,
    }


def load_ai_runs(ai_db: Path, ids: list[str]) -> list[dict[str, Any]]:
    if not ids or not ai_db.exists():
        return []
    placeholders = ",".join("?" for _ in ids)
    with sqlite3.connect(ai_db) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(f"select * from ai_runs where id in ({placeholders})", ids).fetchall()
    by_id = {row["id"]: row for row in rows}
    return [row_to_ai_run(by_id[run_id]) if run_id in by_id else {"id": run_id, "missing": True} for run_id in ids]


def row_to_ai_run(row: sqlite3.Row) -> dict[str, Any]:
    request = safe_json(row["request_payload"], {})
    result = safe_json(row["result_payload"], {})
    return {
        "id": row["id"],
        "step": request.get("draftRunStep") or result.get("draftRunStep") or "unknown",
        "status": row["status"],
        "provider": row["provider"],
        "model": row["model"],
        "fallbackUsed": bool(row["fallback_used"]),
        "error": row["error"],
        "request": compact_request(request),
        "result": compact_result(result),
    }


def compact_request(payload: dict[str, Any]) -> dict[str, Any]:
    original_task = payload.get("originalTask") if isinstance(payload.get("originalTask"), dict) else {}
    return {
        "builtQuery": payload.get("builtQuery"),
        "taskInstruction": original_task.get("instruction"),
        "target": original_task.get("target") or payload.get("target"),
    }


def compact_result(payload: dict[str, Any]) -> dict[str, Any]:
    candidate = payload.get("candidate") if isinstance(payload.get("candidate"), dict) else {}
    return {
        "keys": list(payload.keys()),
        "acceptedCitations": len(payload.get("acceptedCitations") or []),
        "rejectedCitations": len(payload.get("rejectedCitations") or []),
        "candidateId": candidate.get("id"),
        "candidateSource": candidate.get("source"),
        "candidateTitle": candidate.get("title"),
    }


def source_intent_summary(step: dict[str, Any] | None) -> dict[str, Any]:
    artifact = (step or {}).get("artifact") or {}
    source_intent = artifact.get("sourceIntent") if isinstance(artifact.get("sourceIntent"), dict) else {}
    research_plan = artifact.get("researchPlan") if isinstance(artifact.get("researchPlan"), dict) else {}
    return {
        "sourcesOrigin": artifact.get("sourcesOrigin"),
        "items": [
            {"kind": item.get("kind"), "value": one_line(item.get("value") or item.get("raw") or item.get("instruction"))}
            for item in source_intent.get("items", [])
            if isinstance(item, dict)
        ],
        "taskCount": len(research_plan.get("verificationTasks") or []),
        "queryCount": len(research_plan.get("queryCandidates") or []),
        "exclusionCount": len(research_plan.get("exclusions") or []),
    }


def public_evidence_summary(step: dict[str, Any] | None) -> dict[str, Any]:
    artifact = (step or {}).get("artifact") or {}
    attempts = artifact.get("attempts") or []
    items = artifact.get("items") or []
    warnings = artifact.get("warnings") or []
    return {
        "attemptCount": len(attempts),
        "itemCount": len(items),
        "warningCount": len(warnings),
        "attempts": [
            {
                "id": attempt.get("id"),
                "taskId": attempt.get("taskId"),
                "status": attempt.get("status"),
                "target": attempt.get("target"),
                "builtQuery": one_line((attempt.get("metadata") or {}).get("builtQuery"), 180),
                "rejected": len((attempt.get("metadata") or {}).get("rejectedCitations") or []),
            }
            for attempt in attempts
            if isinstance(attempt, dict)
        ],
        "warnings": [{"code": warning.get("code"), "message": one_line(warning.get("message"), 160)} for warning in warnings if isinstance(warning, dict)],
        "sampleItems": [
            {"title": item.get("sourceTitle"), "url": item.get("sourceUrl"), "snippet": one_line(item.get("snippet"), 180)}
            for item in items[:5]
            if isinstance(item, dict)
        ],
    }


def draft_summary(step: dict[str, Any] | None) -> dict[str, Any]:
    artifact = (step or {}).get("artifact") or {}
    candidates = artifact.get("candidates") or []
    selection = artifact.get("selection") or {}
    return {
        "source": artifact.get("source"),
        "fallbackUsed": artifact.get("fallbackUsed"),
        "candidateCount": len(candidates),
        "selectedCandidateId": selection.get("selectedCandidateId"),
        "scorecard": selection.get("scorecard"),
        "candidates": [
            {
                "id": candidate.get("id"),
                "source": candidate.get("source"),
                "fallbackUsed": candidate.get("fallbackUsed"),
                "aiRunId": candidate.get("aiRunId"),
                "title": candidate.get("title"),
                "weaknesses": candidate.get("weaknesses"),
                "bodyHead": one_line(candidate.get("body"), 240),
            }
            for candidate in candidates
            if isinstance(candidate, dict)
        ],
    }


def draft_brief(final_draft: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(final_draft, dict):
        return None
    body = str(final_draft.get("body") or "")
    return {"title": final_draft.get("title"), "chars": len(body), "bodyHead": one_line(body, 400)}


def build_findings(
    steps: list[dict[str, Any]],
    ai_runs: list[dict[str, Any]],
    draft_step: dict[str, Any] | None,
    public_evidence_step: dict[str, Any] | None,
    final_draft: dict[str, Any] | None,
) -> list[str]:
    findings: list[str] = []
    failed_steps = [step["key"] for step in steps if step["status"] == "failed"]
    pending_steps = [step["key"] for step in steps if step["status"] == "pending"]
    if failed_steps:
        findings.append(f"Failed steps: {', '.join(failed_steps)}")
    if pending_steps:
        findings.append(f"Pending steps remain: {', '.join(pending_steps)}")
    fallback_runs = [run for run in ai_runs if run.get("fallbackUsed")]
    if fallback_runs:
        findings.append(f"Child AiRuns used fallback: {', '.join(run['id'] for run in fallback_runs)}")
    public_artifact = (public_evidence_step or {}).get("artifact") or {}
    if public_artifact.get("warnings"):
        findings.append(f"Public evidence warnings: {len(public_artifact.get('warnings') or [])}")
    draft = draft_summary(draft_step)
    selected = draft.get("selectedCandidateId")
    selected_candidate = next((candidate for candidate in draft.get("candidates", []) if candidate.get("id") == selected), None)
    provider_candidates = [candidate for candidate in draft.get("candidates", []) if candidate.get("source") == "openrouter"]
    if selected_candidate and selected_candidate.get("source") == "deterministicFallback" and provider_candidates:
        findings.append("Selected candidate is deterministic fallback while provider candidates exist.")
    body = str((final_draft or {}).get("body") or "")
    if contains_raw_artifact(body):
        findings.append("Final draft appears to contain raw artifact/object dump.")
    return findings


def contains_raw_artifact(text: str) -> bool:
    needles = ["{'id':", '"id":', "'type':", '"type":', "deterministicFallback", "Needs provider rewrite"]
    return any(needle in text for needle in needles)


def print_markdown(summary: dict[str, Any]) -> None:
    if not summary.get("found"):
        print(f"# DraftRun {summary.get('runId')}\n\n{summary.get('error')}")
        return
    print(f"# DraftRun {summary['runId']}")
    print(f"\n- status: {summary['status']}")
    print(f"- created: {summary['createdAt']}")
    print(f"- updated: {summary['updatedAt']}")
    print(f"- final draft: {'yes' if summary['hasFinalDraft'] else 'no'}")
    print("\n## Findings")
    findings = summary.get("findings") or ["No obvious failure signals detected by helper."]
    for finding in findings:
        print(f"- {finding}")
    print("\n## Steps")
    for step in summary["steps"]:
        print(f"- {step['key']}: {step['status']}" + (f" ({step['error']})" if step.get("error") else ""))
    print("\n## Public Evidence")
    pe = summary["publicEvidence"]
    print(f"- attempts: {pe['attemptCount']}; items: {pe['itemCount']}; warnings: {pe['warningCount']}")
    for attempt in pe["attempts"]:
        print(f"- {attempt['id']}: {attempt['status']}; rejected={attempt['rejected']}; query={attempt['builtQuery']}")
    print("\n## Draft Selection")
    draft = summary["draft"]
    print(f"- selected: {draft.get('selectedCandidateId')}")
    for candidate in draft.get("candidates", []):
        print(f"- {candidate['id']}: source={candidate.get('source')}; fallback={candidate.get('fallbackUsed')}; title={candidate.get('title')}")
    if summary.get("finalDraft"):
        print("\n## Final Draft")
        print(f"- title: {summary['finalDraft']['title']}")
        print(f"- chars: {summary['finalDraft']['chars']}")
        print(f"- head: {summary['finalDraft']['bodyHead']}")


def safe_json(value: Any, fallback: Any) -> Any:
    if value in (None, ""):
        return fallback
    try:
        return json.loads(value)
    except Exception:
        return fallback


def one_line(value: Any, limit: int = 140) -> str | None:
    if value is None:
        return None
    text = str(value).replace("\n", " ").strip()
    return text[:limit]


if __name__ == "__main__":
    raise SystemExit(main())
