from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.settings import BackendSettings


def main() -> int:
    parser = argparse.ArgumentParser(description="UTF-8-safe workspace load/save client with semantic hash proof.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--email", default="founder@example.test")
    parser.add_argument("--cycles", type=int, default=1)
    args = parser.parse_args()

    password = BackendSettings().glavred_dev_auth_password.get_secret_value()
    with httpx.Client(base_url=args.base_url, timeout=30.0) as client:
        login = client.post("/api/auth/login", json={"email": args.email, "password": password})
        login.raise_for_status()
        loaded = client.get(f"/api/projects/{args.project_id}/workspace")
        loaded.raise_for_status()
        workspace = loaded.json()["workspace"]
        initial_hash = semantic_hash(workspace)
        cycle_hashes: list[str] = []
        for _ in range(args.cycles):
            saved = client.put(f"/api/projects/{args.project_id}/workspace", json={"workspace": workspace})
            saved.raise_for_status()
            loaded = client.get(f"/api/projects/{args.project_id}/workspace")
            loaded.raise_for_status()
            workspace = loaded.json()["workspace"]
            cycle_hashes.append(semantic_hash(workspace))
    if any(value != initial_hash for value in cycle_hashes):
        raise RuntimeError("workspace-semantic-hash-changed")
    print(
        json.dumps(
            {
                "projectId": args.project_id,
                "cycles": args.cycles,
                "semanticHash": initial_hash,
                "stable": True,
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


def semantic_hash(workspace: dict[str, object]) -> str:
    serialized = json.dumps(workspace, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
