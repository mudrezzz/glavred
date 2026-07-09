from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.drafting.application.reliability import DraftRunProviderReliabilityReporter
from backend.app.drafting.application.workflow.draft_run_runtime_diagnostics import DraftRunRuntimeDiagnostics
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.app.settings import get_settings


class DraftRunReliabilityCli:
    def run(self, argv: list[str] | None = None) -> int:
        args = self._parser().parse_args(argv)
        settings = get_settings()
        draft_repository = SqliteDraftRunRepository(Path(args.draft_run_db or settings.draft_run_db_path))
        ai_repository = SqliteAiRunRepository(Path(args.ai_run_db or settings.ai_run_audit_db_path))

        runs = []
        ai_runs_by_draft_run_id = {}
        for run_id in args.run_id:
            run = draft_repository.get(run_id)
            if run is None:
                raise SystemExit(f"DraftRun not found: {run_id}")
            runs.append(run)
            ai_runs_by_draft_run_id[run.id] = [
                ai_run
                for ai_run_id in self._ai_run_ids(run)
                if (ai_run := ai_repository.get(ai_run_id)) is not None
            ]

        report = DraftRunProviderReliabilityReporter().build(
            runs,
            ai_runs_by_draft_run_id=ai_runs_by_draft_run_id,
        )
        runtime_diagnostics = [DraftRunRuntimeDiagnostics().to_payload(run) for run in runs]
        if args.format == "json":
            payload = report.to_payload()
            payload["runtimeDiagnostics"] = runtime_diagnostics
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(self._runtime_markdown(runtime_diagnostics))
            print(report.to_markdown())
        return 0

    def _parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Analyze DraftRun provider reliability across one or more runs.")
        parser.add_argument("--run-id", action="append", required=True, help="DraftRun id. Repeat for cross-run analytics.")
        parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
        parser.add_argument("--draft-run-db", default=None)
        parser.add_argument("--ai-run-db", default=None)
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
                if key in {"aiRunId"} and child:
                    ids.append(str(child))
                elif key in {"aiRunIds"} and isinstance(child, list):
                    ids.extend(str(item) for item in child if item)
                else:
                    ids.extend(self._ids_from_payload(child))
        elif isinstance(value, list):
            for child in value:
                ids.extend(self._ids_from_payload(child))
        return ids

    def _runtime_markdown(self, diagnostics: list[dict[str, Any]]) -> str:
        lines = ["# DraftRun Runtime Diagnostics", ""]
        for item in diagnostics:
            state = item.get("state") or "unknown"
            if state == "queued":
                detail = f"технически ждет очередь; ожидание {item.get('queueWaitSeconds') or 0}s"
            elif state == "provider-operation-running":
                detail = (
                    f"идет вызов провайдера `{item.get('currentOperationId')}`"
                    f" на модели `{item.get('selectedModel') or 'unknown'}`;"
                    f" ожидание {item.get('providerWaitSeconds') or 0}s из {item.get('staleAfterSeconds') or 'unknown'}s"
                )
            elif state == "provider-operation-stale":
                detail = (
                    f"операция превысила бюджет ожидания: `{item.get('currentOperationId')}`"
                    f" на модели `{item.get('selectedModel') or 'unknown'}`;"
                    f" ожидание {item.get('providerWaitSeconds') or 0}s"
                )
            elif state == "validation-runtime":
                detail = (
                    "validation медленный, но в бюджете"
                    if item.get("slowButHealthy")
                    else "validation превысил бюджет ожидания"
                )
            else:
                detail = str(item.get("staleReason") or state)
            lines.append(f"- `{item['runId']}`: {detail}")
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(DraftRunReliabilityCli().run())
