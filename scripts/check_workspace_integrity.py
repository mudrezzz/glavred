from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.portfolio.application.workspace_integrity import WorkspaceTextIntegrityInspector


def main() -> int:
    parser = argparse.ArgumentParser(description="Check semantic text integrity of stored workspaces.")
    parser.add_argument("--db", type=Path, default=Path("var/glavred-portfolio.sqlite3"))
    parser.add_argument("--project-id")
    parser.add_argument("--all-snapshots", action="store_true")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--fail-on-error", action="store_true")
    args = parser.parse_args()

    reports = inspect_database(args.db, project_id=args.project_id, all_snapshots=args.all_snapshots)
    payload = {"databasePath": str(args.db), "reports": [report.to_payload() for report in reports]}
    print(json.dumps(payload, ensure_ascii=True, indent=2) if args.format == "json" else markdown(payload))
    has_blocking = any(not report.is_clean for report in reports)
    return 1 if args.fail_on_error and has_blocking else 0


def inspect_database(database_path: Path, *, project_id: str | None, all_snapshots: bool):
    inspector = WorkspaceTextIntegrityInspector()
    uri = f"file:{Path(database_path).resolve().as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        connection.row_factory = sqlite3.Row
        where = "WHERE project_id = ?" if project_id else ""
        params = (project_id,) if project_id else ()
        rows = connection.execute(
            f"SELECT * FROM workspace_snapshots {where} ORDER BY project_id, created_at DESC, id DESC",
            params,
        ).fetchall()
    if not all_snapshots:
        latest: dict[str, sqlite3.Row] = {}
        for row in rows:
            latest.setdefault(row["project_id"], row)
        rows = list(latest.values())
    return [
        inspector.inspect(
            json.loads(row["payload"]),
            project_id=row["project_id"],
            snapshot_id=row["id"],
        )
        for row in rows
    ]


def markdown(payload: dict[str, Any]) -> str:
    lines = ["# Workspace integrity report", "", f"Database: `{payload['databasePath']}`", ""]
    for report in payload["reports"]:
        lines.extend(
            (
                f"## {report['projectId']}",
                f"- snapshot: `{report['snapshotId']}`",
                f"- payload bytes: {report['payloadBytes']}",
                f"- blocking issues: {report['blockingIssueCount']}",
            )
        )
        for issue in report["issues"]:
            lines.append(
                f"- `{issue['code']}` at `{issue['path']}`; chars={issue['charCount']}; hash=`{issue['valueHash']}`"
            )
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
