from __future__ import annotations

import json
import sys
from argparse import ArgumentParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.infrastructure.sqlite_runtime import SqliteConnectionFactory
from backend.app.settings import BackendSettings


def main() -> None:
    args = _parse_args()
    settings = BackendSettings()
    draft_path = Path(args.draft_run_db or settings.draft_run_db_path)
    ai_path = Path(args.ai_run_db or settings.ai_run_audit_db_path)
    checker = SqliteConnectionFactory()
    results = [
        checker.integrity_check(draft_path, storage="draftRuns"),
        checker.integrity_check(ai_path, storage="aiRuns"),
    ]
    payload = {
        "ok": all(result.ok for result in results),
        "databases": [result.to_payload() for result in results],
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for result in results:
            status = "ok" if result.ok else "failed"
            print(f"{result.storage}: {status} ({result.result}) {result.path}")
            if result.error:
                print(f"  {result.error['code']}: {result.error['message']}")
    if args.fail_on_error and not payload["ok"]:
        raise SystemExit(1)


def _parse_args():
    parser = ArgumentParser(description="Check local Glavred SQLite runtime databases.")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--draft-run-db", default="")
    parser.add_argument("--ai-run-db", default="")
    parser.add_argument("--fail-on-error", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
