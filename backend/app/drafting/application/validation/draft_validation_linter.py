"""Owner: drafting.application.validation

Used by: DraftRun validation package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

import re
from typing import Any

from backend.app.drafting.application.validation.draft_validation_evidence import ValidationEvidenceEvaluator
from backend.app.domain.draft_validation import DraftValidatorFinding, DraftValidatorStatus


RAW_ARTIFACT_PATTERNS = ("{'id':", '{"id":', '"id":', "'type':", '"type":', "[{", "}]")


class DeterministicDraftLinter:
    def __init__(self, evidence_evaluator: ValidationEvidenceEvaluator | None = None) -> None:
        self._evidence_evaluator = evidence_evaluator or ValidationEvidenceEvaluator()

    def lint(
        self,
        *,
        candidate: dict[str, Any],
        context_artifact: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        score_row: dict[str, Any] | None = None,
    ) -> list[DraftValidatorFinding]:
        findings: list[DraftValidatorFinding] = []
        candidate_id = str(candidate.get("id") or "unknown-candidate")
        title = str(candidate.get("title") or "")
        body = str(candidate.get("body") or "")
        findings.extend(self._shape_findings(candidate_id, title, body))
        findings.extend(self._size_findings(candidate_id, body, context_artifact))
        findings.extend(self._contract_findings(candidate_id, body, context_artifact))
        findings.extend(self._evidence_evaluator.findings(candidate_id=candidate_id, body=body, candidate=candidate, context_artifact=context_artifact, material_plan=material_plan, finding_factory=_finding))
        findings.extend(self._rule_findings(candidate_id, body, rule_pack))
        findings.extend(self._publishability_findings(candidate_id, candidate, score_row))
        return findings

    def _shape_findings(self, candidate_id: str, title: str, body: str) -> list[DraftValidatorFinding]:
        findings: list[DraftValidatorFinding] = []
        if not title.strip():
            findings.append(_finding("publishability.title", DraftValidatorStatus.CRITICAL, candidate_id, "Draft candidate has empty title.", "", "Generate a real title before publication."))
        if not body.strip():
            findings.append(_finding("publishability.body", DraftValidatorStatus.CRITICAL, candidate_id, "Draft candidate has empty body.", "", "Generate body text before publication."))
        body_lower = f"{title}\n{body}".lower()
        for pattern in RAW_ARTIFACT_PATTERNS:
            if pattern.lower() in body_lower:
                findings.append(_finding("publishability.raw-artifact", DraftValidatorStatus.CRITICAL, candidate_id, "Candidate leaks raw JSON/object artifact text.", _excerpt(body, pattern), "Rewrite the candidate as prose and remove service payload dumps."))
                break
        return findings

    def _size_findings(self, candidate_id: str, body: str, context_artifact: dict[str, Any]) -> list[DraftValidatorFinding]:
        contract = _dict(_dict(context_artifact.get("postContract")).get("publicationSizeContract"))
        if not contract or not body:
            return []
        findings: list[DraftValidatorFinding] = []
        length = len(body)
        hard_max = _int(contract.get("hardMaxChars"))
        max_chars = _int(contract.get("maxChars"))
        min_chars = _int(contract.get("minChars"))
        if hard_max and length > hard_max:
            findings.append(_finding("size.hard-max", DraftValidatorStatus.CRITICAL, candidate_id, f"Draft is {length} chars, above hard max {hard_max}.", f"{length} chars", "Shorten the post below the hard maximum.", rule_ids=["size:hard-max"]))
        elif max_chars and length > max_chars:
            findings.append(_finding("size.target-range", DraftValidatorStatus.WARNING, candidate_id, f"Draft is {length} chars, above target max {max_chars}.", f"{length} chars", "Compress examples or remove secondary arguments.", rule_ids=["size:target-range"]))
        if min_chars and length < min_chars:
            findings.append(_finding("size.target-range", DraftValidatorStatus.WARNING, candidate_id, f"Draft is {length} chars, below target min {min_chars}.", f"{length} chars", "Add one grounded argument or example.", rule_ids=["size:target-range"]))
        paragraph_range = _dict(contract.get("paragraphRange"))
        paragraph_count = len([item for item in re.split(r"\n\s*\n", body.strip()) if item.strip()])
        min_paragraphs = _int(paragraph_range.get("min"))
        max_paragraphs = _int(paragraph_range.get("max"))
        if min_paragraphs and paragraph_count < min_paragraphs:
            findings.append(_finding("shape.paragraph-range", DraftValidatorStatus.WARNING, candidate_id, f"Draft has {paragraph_count} paragraphs, below expected {min_paragraphs}.", f"{paragraph_count} paragraphs", "Split the argument into clearer paragraphs."))
        if max_paragraphs and paragraph_count > max_paragraphs:
            findings.append(_finding("shape.paragraph-range", DraftValidatorStatus.WARNING, candidate_id, f"Draft has {paragraph_count} paragraphs, above expected {max_paragraphs}.", f"{paragraph_count} paragraphs", "Merge or remove low-value paragraphs."))
        return findings

    def _contract_findings(self, candidate_id: str, body: str, context_artifact: dict[str, Any]) -> list[DraftValidatorFinding]:
        contract = _dict(context_artifact.get("postContract"))
        body_lower = body.lower()
        findings: list[DraftValidatorFinding] = []
        cta = str(contract.get("cta") or "")
        if cta and not _has_token_overlap(body_lower, cta):
            findings.append(_finding("contract.cta", DraftValidatorStatus.WARNING, candidate_id, "Draft does not visibly execute the locked CTA.", cta, "Add the CTA or an equivalent action at the end.", rule_ids=["contract:cta"]))
        for field, validator_id, message in (
            ("thesis", "contract.thesis", "Draft may not preserve the locked thesis."),
            ("audience", "contract.audience", "Draft does not visibly address the intended audience."),
            ("value", "contract.value", "Draft does not make the intended reader value explicit."),
        ):
            value = str(contract.get(field) or "")
            if value and not _has_token_overlap(body_lower, value):
                findings.append(_finding(validator_id, DraftValidatorStatus.WARNING, candidate_id, message, value, "Revise the draft to preserve the post contract.", rule_ids=[f"contract:{field}"]))
        return findings

    def _rule_findings(self, candidate_id: str, body: str, rule_pack: dict[str, Any]) -> list[DraftValidatorFinding]:
        body_lower = body.lower()
        findings: list[DraftValidatorFinding] = []
        forbidden_rules = [*_list(rule_pack.get("forbiddenMoves"))]
        registry_rules = _list(_dict(rule_pack.get("ruleRegistrySnapshot")).get("rules"))
        forbidden_rules.extend(rule for rule in registry_rules if _dict(rule).get("category") == "forbiddenMoves")
        for raw_rule in forbidden_rules:
            rule = _dict(raw_rule)
            rule_id = str(rule.get("id") or "rule:forbidden")
            statement = str(rule.get("statement") or rule.get("title") or "")
            if statement and _has_forbidden_phrase(body_lower, statement):
                findings.append(_finding("rules.forbidden-move", DraftValidatorStatus.CRITICAL, candidate_id, "Draft appears to violate a forbidden move.", statement, "Remove or reframe this move.", rule_ids=[rule_id]))
        return findings

    def _publishability_findings(
        self,
        candidate_id: str,
        candidate: dict[str, Any],
        score_row: dict[str, Any] | None,
    ) -> list[DraftValidatorFinding]:
        findings: list[DraftValidatorFinding] = []
        weaknesses = _strings(candidate.get("weaknesses"))
        if any("Needs provider rewrite before publication" in item for item in weaknesses):
            findings.append(_finding("publishability.provider-rewrite", DraftValidatorStatus.CRITICAL, candidate_id, "Candidate is marked as needing provider rewrite before publication.", "; ".join(weaknesses), "Do not publish this candidate without regeneration."))
        if score_row and str(score_row.get("selectionStatus") or "") == "excluded":
            findings.append(_finding("publishability.selection-status", DraftValidatorStatus.CRITICAL, candidate_id, "Candidate was excluded by publishability selection guard.", "; ".join(_strings(score_row.get("selectionReasons"))), "Keep this candidate only for diagnostics."))
        return findings


def _finding(
    validator_id: str,
    severity: DraftValidatorStatus,
    candidate_id: str,
    message: str,
    excerpt: str,
    guidance: str,
    *,
    rule_ids: list[str] | None = None,
    claim_ids: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> DraftValidatorFinding:
    return DraftValidatorFinding(
        validator_id=validator_id,
        severity=severity,
        candidate_id=candidate_id,
        message=message,
        evidence_excerpt=excerpt[:500],
        repair_guidance=guidance,
        rule_ids=rule_ids or [],
        claim_ids=claim_ids or [],
        metadata=metadata or {},
    )


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in _list(value) if str(item).strip()]


def _int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _has_token_overlap(body_lower: str, text: str) -> bool:
    tokens = [token.lower() for token in re.findall(r"[\wА-Яа-яЁё]{5,}", text)]
    if not tokens:
        return True
    return any(token in body_lower for token in tokens[:8])


def _has_forbidden_phrase(body_lower: str, statement: str) -> bool:
    statement_lower = statement.lower().strip()
    if len(statement_lower) < 8:
        return False
    if statement_lower in body_lower:
        return True
    tokens = [token for token in re.findall(r"[\wА-Яа-яЁё]{7,}", statement_lower) if token not in {"should", "must", "нельзя"}]
    return len(tokens) >= 2 and all(token in body_lower for token in tokens[:2])


def _excerpt(body: str, needle: str) -> str:
    index = body.lower().find(needle.lower())
    if index < 0:
        return body[:180]
    return body[max(0, index - 60):index + 160]
