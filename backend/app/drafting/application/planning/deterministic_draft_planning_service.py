"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.draft_planning import DraftStrategy, MaterialPlan


class DeterministicDraftPlanningService:
    def create_material_plan(
        self,
        *,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
    ) -> MaterialPlan:
        evidence = _details(rule_pack.get("evidenceRequirements"))
        missing = [
            f"Missing {item.get('entity')} {item.get('id')}"
            for item in _dicts(rule_pack.get("warnings"))
            if item.get("entity") or item.get("id")
        ]
        risks = _statements(rule_pack.get("forbiddenMoves"))
        return MaterialPlan(
            available_evidence=evidence or ["Use approved brief evidence."],
            missing_evidence=missing,
            risky_claims=risks,
            grounding_plan=[
                "Ground the opening in the selected signal.",
                "Use candidate evidence before broader commentary.",
                "Keep unverified claims as author observations.",
            ],
            source_notes=_source_notes(context_summary),
            open_questions=missing,
        )

    def create_strategy(
        self,
        *,
        context_summary: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
    ) -> DraftStrategy:
        intent = _dict(rule_pack.get("draftIntent"))
        return DraftStrategy(
            thesis_angle=str(intent.get("thesis") or _dict(context_summary.get("brief")).get("thesis") or ""),
            opening_move="Start with the tension between demo success and adoption reality.",
            argument_sequence=[
                "Name the observed signal.",
                "Explain why the signal matters for the target audience.",
                "Apply the selected fabula and evidence plan.",
                "Close with the approved CTA.",
            ],
            fabula_usage=_first_detail(rule_pack.get("dramaturgyRequirements")),
            cta_plan=str(intent.get("cta") or ""),
            forbidden_moves=_statements(rule_pack.get("forbiddenMoves")),
            tone_notes=_details(rule_pack.get("softConstraints")) + _details(material_plan.get("sourceNotes")),
        )


def _source_notes(context_summary: dict[str, Any]) -> list[str]:
    signal = _dict(context_summary.get("sourceSignal"))
    candidate = _dict(context_summary.get("candidate"))
    return [
        note
        for note in [
            signal.get("summary"),
            signal.get("rawNote"),
            signal.get("authorCorrection"),
            candidate.get("evidenceSummary"),
        ]
        if note
    ]


def _details(value: Any) -> list[str]:
    return [str(item.get("detail") or item.get("statement") or "") for item in _dicts(value) if item]


def _statements(value: Any) -> list[str]:
    return [str(item.get("statement") or "") for item in _dicts(value) if item.get("statement")]


def _first_detail(value: Any) -> str:
    items = _details(value)
    return items[0] if items else ""


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


DeterministicDraftPlanningFallbackService = DeterministicDraftPlanningService


__all__ = (
    'DeterministicDraftPlanningService',
    'DeterministicDraftPlanningFallbackService',
)
