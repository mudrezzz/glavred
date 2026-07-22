"""Owner: upstream.application

Used by: governed openWebQuery operation before provider budget checks and transport.
Does not own: provider execution, query planning, run budgets, retries, or result triage.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from __future__ import annotations

from typing import Any


class OpenWebQueryInputBuilder:
    def provider_input(self, *, run_id: str, query: dict[str, Any]) -> dict[str, Any]:
        return {
            "operationId": "openWebQuery",
            "radarRunId": run_id,
            "queryId": query["id"],
            "sourceHandleId": query["sourceHandleId"],
            "intentId": query.get("intentId"),
            "family": query.get("family"),
            "evidenceType": query.get("evidenceType"),
            "query": str(query.get("query") or ""),
        }

    def messages(self, provider_input: dict[str, Any]) -> list[dict[str, str]]:
        return [
            {
                "role": "system",
                "content": "Use web search to find public source material. Return citations. Do not invent sources.",
            },
            {"role": "user", "content": str(provider_input["query"])},
        ]


__all__ = ("OpenWebQueryInputBuilder",)
