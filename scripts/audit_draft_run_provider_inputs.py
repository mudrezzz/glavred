from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.drafting.application.operations.provider_input_audit import ProviderInputAudit
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.app.settings import get_settings


class DraftRunProviderInputAuditCli:
    def run(self, argv: list[str] | None = None) -> int:
        args = self._parser().parse_args(argv)
        settings = get_settings()
        draft_repository = SqliteDraftRunRepository(Path(args.draft_run_db or settings.draft_run_db_path))
        ai_repository = SqliteAiRunRepository(Path(args.ai_run_db or settings.ai_run_audit_db_path))
        ai_runs = []
        for run_id in args.run_id:
            run = draft_repository.get(run_id)
            if run is None:
                raise SystemExit(f"DraftRun not found: {run_id}")
            for ai_run_id in self._ai_run_ids(run):
                ai_run = ai_repository.get(ai_run_id)
                if ai_run is not None:
                    ai_runs.append(ai_run)
        report = ProviderInputAudit().audit_ai_runs(ai_runs)
        if args.format == "json":
            print(json.dumps(report.to_payload(), ensure_ascii=False, indent=2))
        else:
            print(report.to_markdown())
        if args.fail_on_unclean and not report.to_payload()["summary"]["clean"]:
            return 1
        return 0

    def _parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Audit DraftRun child AiRun provider input budget proof.")
        parser.add_argument("--run-id", action="append", required=True, help="DraftRun id. Repeat for multi-run audit.")
        parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
        parser.add_argument("--draft-run-db", default=None)
        parser.add_argument("--ai-run-db", default=None)
        parser.add_argument("--fail-on-unclean", action="store_true")
        return parser

    def _ai_run_ids(self, run: Any) -> list[str]:
        ids = list(getattr(run, "ai_run_ids", []) or [])
        for step in getattr(run, "steps", []) or []:
            ids.extend(self._ids_from_payload(getattr(step, "artifact_payload", None)))
        seen: set[str] = set()
        result: list[str] = []
        for item in ids:
            value = str(item)
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result

    def _ids_from_payload(self, value: Any) -> list[str]:
        ids: list[str] = []
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "aiRunId" and child:
                    ids.append(str(child))
                elif key == "aiRunIds" and isinstance(child, list):
                    ids.extend(str(item) for item in child if item)
                else:
                    ids.extend(self._ids_from_payload(child))
        elif isinstance(value, list):
            for child in value:
                ids.extend(self._ids_from_payload(child))
        return ids


if __name__ == "__main__":
    raise SystemExit(DraftRunProviderInputAuditCli().run())
