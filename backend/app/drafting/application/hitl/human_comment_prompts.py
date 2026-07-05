"""Owner: drafting.application.hitl

Used by: Human-comment revision and quality-check services.
Does not own: Provider execution, API request parsing, SQLite persistence, or trace storage.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import json
from typing import Any

from backend.app.drafting.application.hitl.human_comment_context import HumanCommentVersionCompactor


class HumanCommentRevisionPromptBuilder:
    def __init__(self, version_compactor: HumanCommentVersionCompactor | None = None) -> None:
        self._version_compactor = version_compactor or HumanCommentVersionCompactor()

    def build_messages(
        self,
        *,
        current_version: dict[str, Any],
        editor_comment: str,
        trace_context: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> list[dict[str, str]]:
        system = (
            "You are Glavred's post-run human editor revision writer. Return strict JSON only. "
            "Revise the current public post according to the human editor comment. Preserve useful source markers, "
            "do not invent new claims, do not expose internal pipeline jargon such as SourceLedger, publicEvidence, "
            "validators, RuleRegistry, or PostContract, and keep the text publishable."
        )
        payload = {
            "task": "Create one improved draft version from a human editor comment.",
            "requiredJson": {"title": "string", "body": "string", "revisionSummary": "string"},
            "currentVersion": self._version_compactor.compact(current_version),
            "editorComment": editor_comment,
            "machineTraceContext": trace_context,
            "repairContext": repair_context,
        }
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]


class HumanCommentQualityPromptBuilder:
    def __init__(self, version_compactor: HumanCommentVersionCompactor | None = None) -> None:
        self._version_compactor = version_compactor or HumanCommentVersionCompactor()

    def build_messages(
        self,
        *,
        base_version: dict[str, Any],
        revised_version: dict[str, Any],
        editor_comment: str,
        trace_context: dict[str, Any],
        repair_context: dict[str, Any] | None,
    ) -> list[dict[str, str]]:
        system = (
            "You are Glavred's post-run human revision quality reviewer. Return strict JSON only. "
            "Evaluate whether the revised public post followed the editor comment without losing source markers, "
            "without adding internal pipeline jargon, and without becoming worse public prose."
        )
        payload = {
            "task": "Assess one human-comment revision. This is diagnostic: do not rewrite the post.",
            "requiredJson": {
                "status": "passed | warning | critical",
                "commentComplianceStatus": "passed | warning | critical",
                "sourceIntegrityStatus": "passed | warning | critical",
                "publicProseStatus": "passed | warning | critical",
                "internalJargonLeaks": ["string"],
                "regressionWarnings": ["string"],
                "matchedCommentIntents": ["string"],
                "missedCommentIntents": ["string"],
                "summary": "string",
            },
            "baseVersion": self._version_compactor.compact(base_version),
            "revisedVersion": self._version_compactor.compact(revised_version),
            "editorComment": editor_comment,
            "machineTraceContext": trace_context,
            "repairContext": repair_context,
        }
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]
