from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.portfolio.application.workspace_recovery import WorkspaceRecoveryService


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild local portfolio SQLite without corrupt workspace snapshots.")
    parser.add_argument("--db", type=Path, default=Path("var/glavred-portfolio.sqlite3"))
    parser.add_argument("--project-id", default="project-ai-design-patterns")
    parser.add_argument("--backup-dir", type=Path, default=Path("var/recovery"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    result = WorkspaceRecoveryService().recover_demo_project(
        args.db,
        project_id=args.project_id,
        backup_dir=args.backup_dir,
        apply=args.apply,
    )
    print(json.dumps(result.to_payload(), ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
