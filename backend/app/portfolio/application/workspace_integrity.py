"""Owner: portfolio.application

Used by: portfolio workspace persistence, recovery tooling, and API diagnostics.
Does not own: HTTP routing, SQLite schema, frontend fallback, or workspace normalization.
Architecture doc: docs/adr/2026-07-16-workspace-text-integrity-and-connected-ui-acceptance.md
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Iterable


@dataclass(frozen=True)
class WorkspaceIntegrityIssue:
    path: str
    code: str
    severity: str
    char_count: int
    value_hash: str

    def to_payload(self) -> dict[str, object]:
        return {
            "path": self.path,
            "code": self.code,
            "severity": self.severity,
            "charCount": self.char_count,
            "valueHash": self.value_hash,
        }


@dataclass(frozen=True)
class WorkspaceIntegrityReport:
    project_id: str
    snapshot_id: str | None
    payload_bytes: int
    string_count: int
    issues: tuple[WorkspaceIntegrityIssue, ...]

    @property
    def blocking_issues(self) -> tuple[WorkspaceIntegrityIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "blocking")

    @property
    def is_clean(self) -> bool:
        return not self.blocking_issues

    def to_payload(self) -> dict[str, object]:
        return {
            "projectId": self.project_id,
            "snapshotId": self.snapshot_id,
            "payloadBytes": self.payload_bytes,
            "stringCount": self.string_count,
            "issueCount": len(self.issues),
            "blockingIssueCount": len(self.blocking_issues),
            "issues": [issue.to_payload() for issue in self.issues],
        }


class WorkspaceIntegrityError(ValueError):
    def __init__(self, report: WorkspaceIntegrityReport, *, operation: str) -> None:
        super().__init__("workspace-text-integrity-failed")
        self.report = report
        self.operation = operation

    def to_payload(self) -> dict[str, object]:
        return {
            "code": "workspace-text-integrity-failed",
            "operation": self.operation,
            **self.report.to_payload(),
        }


class WorkspaceTextIntegrityInspector:
    """Detects high-confidence corruption without attempting semantic repair."""

    _QUESTION_REPLACEMENT = re.compile(r"\?{4,}")
    _LATIN_MOJIBAKE = ("Ã", "Â", "Ð", "Ñ", "â€", "ï¿½")
    _CYRILLIC_MOJIBAKE = (
        "Рђ", "Р‘", "Р’", "Р“", "Р”", "Р•", "Р–", "Р—", "Р", "Р™",
        "Рљ", "Р›", "Рњ", "Рќ", "Рћ", "Рџ", "Р ", "РЎ", "Рў", "РЈ",
        "Р¤", "РҐ", "Р¦", "Р§", "РЁ", "Р©", "Р­", "Р®", "РЇ", "СЃ",
        "С‚", "СЂ", "Сѓ", "С„", "С…", "С†", "С‡", "С€", "С‰", "СЊ",
        "С‹", "СЌ", "СЋ", "СЏ", "В«", "В»", "вЂ",
    )
    _PATH_LIMITS = (
        (re.compile(r"\.searchPlan\.queries\[\d+\]\.query$"), 1_000),
        (re.compile(r"\.rawResults\[\d+\]\.query$"), 1_000),
        (re.compile(r"\.radars\[\d+\]\.rules\[\d+\]\.statement$"), 6_000),
        (re.compile(r"\.insightCard\.title$"), 2_000),
        (re.compile(r"\.insightCard\.(whyItMatters|audienceRelevance|authorPosition)$"), 12_000),
        (re.compile(r"\.sourceSignals\[\d+\]\.(title|summary|rawNote|searchNote)$"), 12_000),
    )
    DEFAULT_STRING_LIMIT = 120_000
    PAYLOAD_LIMIT_BYTES = 16_000_000

    def inspect(
        self,
        payload: dict[str, Any],
        *,
        project_id: str,
        snapshot_id: str | None = None,
    ) -> WorkspaceIntegrityReport:
        serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        issues: list[WorkspaceIntegrityIssue] = []
        string_count = 0
        for path, value in self._walk_strings(payload):
            string_count += 1
            issue_code = self._corruption_code(value)
            if issue_code:
                issues.append(self._issue(path, value, issue_code))
                continue
            limit = self._limit_for(path)
            if len(value) > limit:
                issues.append(self._issue(path, value, "text-field-too-large"))
        payload_bytes = len(serialized.encode("utf-8"))
        if payload_bytes > self.PAYLOAD_LIMIT_BYTES:
            issues.append(
                WorkspaceIntegrityIssue(
                    path="$",
                    code="workspace-payload-too-large",
                    severity="blocking",
                    char_count=len(serialized),
                    value_hash=self._hash(serialized),
                )
            )
        return WorkspaceIntegrityReport(
            project_id=project_id,
            snapshot_id=snapshot_id,
            payload_bytes=payload_bytes,
            string_count=string_count,
            issues=tuple(issues),
        )

    def _corruption_code(self, value: str) -> str | None:
        if "\ufffd" in value:
            return "unicode-replacement-character"
        if any(marker in value for marker in self._LATIN_MOJIBAKE):
            return "probable-mojibake"
        cyrillic_hits = sum(value.count(marker) for marker in self._CYRILLIC_MOJIBAKE)
        if cyrillic_hits >= 3:
            return "probable-mojibake"
        if self._QUESTION_REPLACEMENT.search(value):
            return "question-mark-replacement-text"
        return None

    def _limit_for(self, path: str) -> int:
        for pattern, limit in self._PATH_LIMITS:
            if pattern.search(path):
                return limit
        return self.DEFAULT_STRING_LIMIT

    @classmethod
    def _walk_strings(cls, value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
        if isinstance(value, dict):
            for key, child in value.items():
                yield from cls._walk_strings(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from cls._walk_strings(child, f"{path}[{index}]")
        elif isinstance(value, str):
            yield path, value

    @classmethod
    def _issue(cls, path: str, value: str, code: str) -> WorkspaceIntegrityIssue:
        return WorkspaceIntegrityIssue(
            path=path,
            code=code,
            severity="blocking",
            char_count=len(value),
            value_hash=cls._hash(value),
        )

    @staticmethod
    def _hash(value: str) -> str:
        return sha256(value.encode("utf-8")).hexdigest()[:20]


class WorkspaceIntegrityPolicy:
    def __init__(self, inspector: WorkspaceTextIntegrityInspector | None = None) -> None:
        self._inspector = inspector or WorkspaceTextIntegrityInspector()

    def ensure_readable(self, payload: dict[str, Any], *, project_id: str, snapshot_id: str) -> None:
        report = self._inspector.inspect(payload, project_id=project_id, snapshot_id=snapshot_id)
        if not report.is_clean:
            raise WorkspaceIntegrityError(report, operation="read")

    def ensure_saveable(self, payload: dict[str, Any], *, project_id: str) -> None:
        report = self._inspector.inspect(payload, project_id=project_id)
        if not report.is_clean:
            raise WorkspaceIntegrityError(report, operation="save")
