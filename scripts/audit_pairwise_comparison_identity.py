from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.drafting.application.revision.pairwise_comparison_identity import PairwiseComparisonIdentityPolicy
from backend.app.infrastructure.sqlite_ai_run_repository import SqliteAiRunRepository
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.app.settings import get_settings


class PairwiseComparisonIdentityAuditCli:
    def run(self, argv: list[str] | None = None) -> int:
        args = self._parser().parse_args(argv)
        settings = get_settings()
        draft_repository = SqliteDraftRunRepository(Path(args.draft_run_db or settings.draft_run_db_path))
        ai_repository = SqliteAiRunRepository(Path(args.ai_run_db or settings.ai_run_audit_db_path))
        rows: list[dict[str, Any]] = []
        for run_id in args.run_id:
            draft_run = draft_repository.get(run_id)
            if draft_run is None:
                raise SystemExit(f"DraftRun not found: {run_id}")
            for ai_run_id in self._ai_run_ids(draft_run):
                ai_run = ai_repository.get(ai_run_id)
                if ai_run is None or ai_run.request_payload.get("operationId") != "pairwiseRanking":
                    continue
                provider_input = ai_run.request_payload.get("providerInput") or {}
                candidates = provider_input.get("candidates") if isinstance(provider_input, dict) else []
                candidate_ids = [str(item.get("id")) for item in candidates if isinstance(item, dict) and item.get("id")]
                result = ai_run.result_payload.get("result") if isinstance(ai_run.result_payload, dict) else {}
                trace = PairwiseComparisonIdentityPolicy().evaluate(result if isinstance(result, dict) else {}, candidate_ids)
                rows.append({"draftRunId": run_id, "aiRunId": ai_run_id, **trace.to_payload()})
        payload = {"runs": list(dict.fromkeys(args.run_id)), "pairwiseAttempts": rows, "complete": bool(rows) and all(row["comparisonIdentityComplete"] for row in rows)}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["complete"] or not args.fail_on_incomplete else 1

    def _parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Audit exact pair identity in stored DraftRun pairwise AiRuns.")
        parser.add_argument("--run-id", action="append", required=True)
        parser.add_argument("--draft-run-db", default=None)
        parser.add_argument("--ai-run-db", default=None)
        parser.add_argument("--fail-on-incomplete", action="store_true")
        return parser

    def _ai_run_ids(self, run: Any) -> list[str]:
        result = list(getattr(run, "ai_run_ids", []) or [])
        for step in getattr(run, "steps", []) or []:
            result.extend(self._nested_ids(getattr(step, "artifact_payload", None)))
        return list(dict.fromkeys(str(item) for item in result if item))

    def _nested_ids(self, value: Any) -> list[str]:
        if isinstance(value, dict):
            result: list[str] = []
            for key, child in value.items():
                if key == "aiRunId" and child:
                    result.append(str(child))
                elif key == "aiRunIds" and isinstance(child, list):
                    result.extend(str(item) for item in child if item)
                else:
                    result.extend(self._nested_ids(child))
            return result
        if isinstance(value, list):
            return [item for child in value for item in self._nested_ids(child)]
        return []


if __name__ == "__main__":
    raise SystemExit(PairwiseComparisonIdentityAuditCli().run())
