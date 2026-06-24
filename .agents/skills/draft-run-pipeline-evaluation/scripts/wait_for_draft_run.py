#!/usr/bin/env python3
"""Poll a Glavred DraftRun read-model until completion or diagnostic timeout."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from typing import Any


TERMINAL_STATUSES = {"succeeded", "failed"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Wait for a Glavred DraftRun.")
    parser.add_argument("run_id", help="DraftRun id")
    parser.add_argument("--api-base", default="http://localhost:8000")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    started = time.monotonic()
    last_payload: dict[str, Any] | None = None
    last_error: str | None = None
    while time.monotonic() - started <= args.timeout:
        try:
            payload = fetch_run(args.api_base, args.run_id)
            last_payload = payload
            last_error = None
            status = str(payload.get("status") or "")
            if status in TERMINAL_STATUSES:
                return emit(args, payload, elapsed=time.monotonic() - started)
            if payload.get("isStale"):
                return emit(args, payload, elapsed=time.monotonic() - started, diagnostic="stale")
        except Exception as exc:  # noqa: BLE001 - command-line diagnostic helper
            last_error = f"{exc.__class__.__name__}: {exc}"
        time.sleep(args.interval)

    if last_payload is not None:
        return emit(args, last_payload, elapsed=time.monotonic() - started, diagnostic="timeout-running")
    result = {
        "runId": args.run_id,
        "status": "unavailable",
        "diagnostic": "timeout-no-payload",
        "error": last_error,
        "elapsedSeconds": round(time.monotonic() - started, 1),
    }
    print_result(result, as_json=args.json)
    return 2


def fetch_run(api_base: str, run_id: str) -> dict[str, Any]:
    url = f"{api_base.rstrip('/')}/api/draft-runs/{run_id}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc


def emit(args: argparse.Namespace, payload: dict[str, Any], *, elapsed: float, diagnostic: str | None = None) -> int:
    result = {
        "runId": payload.get("id") or args.run_id,
        "status": payload.get("status"),
        "diagnostic": diagnostic,
        "isStale": payload.get("isStale"),
        "staleReason": payload.get("staleReason"),
        "lastProgressAt": payload.get("lastProgressAt"),
        "elapsedSeconds": round(elapsed, 1),
        "hasFinalDraft": bool(payload.get("finalDraft")),
        "currentStep": current_step(payload),
        "completedAt": datetime.now(UTC).isoformat(),
    }
    print_result(result, as_json=args.json)
    if result["status"] == "failed":
        return 1
    if diagnostic:
        return 2
    return 0


def current_step(payload: dict[str, Any]) -> str | None:
    steps = payload.get("steps") if isinstance(payload.get("steps"), list) else []
    running = [step for step in steps if isinstance(step, dict) and step.get("status") == "running"]
    if running:
        return str(running[-1].get("key") or running[-1].get("stepKey") or running[-1].get("title"))
    completed = [step for step in steps if isinstance(step, dict) and step.get("status") == "succeeded"]
    if completed:
        return str(completed[-1].get("key") or completed[-1].get("stepKey") or completed[-1].get("title"))
    pending = [step for step in steps if isinstance(step, dict)]
    if pending:
        return str(pending[0].get("key") or pending[0].get("stepKey") or pending[0].get("title"))
    return None


def print_result(result: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"DraftRun {result['runId']}")
    print(f"- status: {result.get('status')}")
    if result.get("diagnostic"):
        print(f"- diagnostic: {result['diagnostic']}")
    print(f"- current step: {result.get('currentStep')}")
    print(f"- final draft: {'yes' if result.get('hasFinalDraft') else 'no'}")
    print(f"- elapsed: {result.get('elapsedSeconds')}s")
    if result.get("isStale"):
        print(f"- stale: {result.get('staleReason')}")


if __name__ == "__main__":
    raise SystemExit(main())
