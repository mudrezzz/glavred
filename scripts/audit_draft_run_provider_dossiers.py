from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.drafting.application.context.draft_run_context_access import DraftRunContextAccessService
from backend.app.drafting.application.dossiers.provider_dossier_replay import ProviderDossierReplayService
from backend.app.infrastructure.sqlite_draft_run_repository import SqliteDraftRunRepository
from backend.app.settings import get_settings


class DraftRunProviderDossierAuditCli:
    def run(self, argv: list[str] | None = None) -> int:
        args = self._parser().parse_args(argv)
        db_path = Path(args.draft_run_db or get_settings().draft_run_db_path)
        run = SqliteDraftRunRepository(db_path).get(args.run_id)
        if run is None:
            raise SystemExit(f"DraftRun not found: {args.run_id}")
        report = ProviderDossierReplayService().run(DraftRunContextAccessService.from_run(run))
        if args.format == "json":
            print(json.dumps(report.to_payload(), ensure_ascii=False, indent=2))
        else:
            print(report.to_markdown())
        return 0 if report.ready_for_migration or not args.fail_on_unready else 1

    def _parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Build and audit provider-free DraftRun dossier projections.")
        parser.add_argument("--run-id", required=True)
        parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
        parser.add_argument("--draft-run-db", default=None)
        parser.add_argument("--fail-on-unready", action="store_true")
        return parser


if __name__ == "__main__":
    raise SystemExit(DraftRunProviderDossierAuditCli().run())
