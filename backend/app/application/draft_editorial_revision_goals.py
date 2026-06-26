from typing import Any


EDITORIAL_DIMENSIONS = (
    "ideaStrength",
    "tension",
    "readerValue",
    "authorStance",
    "sourceIntegration",
    "structure",
    "validatorHealth",
)


class DraftEditorialRevisionGoalBuilder:
    def build(
        self,
        *,
        candidate_id: str | None,
        repair_goals: list[str],
        validation_report: dict[str, Any],
        rule_pack: dict[str, Any],
        material_plan: dict[str, Any],
        previous_rejected_moves: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        goals: list[dict[str, Any]] = []
        if repair_goals:
            _append_goal(
                goals,
                goal_id="validator-health",
                dimension="validatorHealth",
                source="validation",
                message="Fix validator findings without losing source markers, CTA, size contract, or post contract.",
                guidance="Close the listed repair goals while preserving all already valid parts of the draft.",
            )
        _append_critique_goals(goals, candidate_id, validation_report)
        _append_evidence_goals(goals, rule_pack)
        _append_alternative_angle_goals(goals, validation_report)
        _append_material_plan_goals(goals, material_plan)
        _append_rejected_move_goals(goals, previous_rejected_moves or [])
        return goals[:10]


def _append_critique_goals(goals: list[dict[str, Any]], candidate_id: str | None, validation_report: dict[str, Any]) -> None:
    critique = _record(validation_report.get("editorialCritiqueReport"))
    for report in _records(critique.get("candidateReports")):
        if candidate_id and report.get("candidateId") != candidate_id:
            continue
        if report.get("weakestMove"):
            text = _text(report.get("weakestMove"))
            _append_goal(goals, goal_id=f"critique-weakest-{candidate_id}", dimension=_dimension_for(text, "ideaStrength"), source="editorialCritique", message=f"Weakest move: {text}", guidance="Replace this weak move with a sharper editorial choice.")
        if report.get("recommendedEditorialMove"):
            text = _text(report.get("recommendedEditorialMove"))
            _append_goal(goals, goal_id=f"critique-recommended-{candidate_id}", dimension=_dimension_for(text, "tension"), source="editorialCritique", message=text, guidance="Apply the critic's recommended editorial move without breaking the contract.")
        for index, finding in enumerate(_records(report.get("findings")), start=1):
            message = _text(finding.get("message"))
            guidance = _text(finding.get("repairGuidance"))
            if message or guidance:
                _append_goal(goals, goal_id=f"critique-finding-{candidate_id}-{index}", dimension=_dimension_for(message + " " + guidance, _text(_record(finding.get("metadata")).get("editorialDimension"), "ideaStrength")), source="editorialCritique", message=message or guidance, guidance=guidance or "Resolve the editorial critique finding.")


def _append_evidence_goals(goals: list[dict[str, Any]], rule_pack: dict[str, Any]) -> None:
    interpretation = _record(rule_pack.get("evidenceInterpretation"))
    for key, dimension, label in (
        ("tensions", "tension", "Use evidence tension"),
        ("readerValueHooks", "readerValue", "Use reader-value hook"),
        ("authorPositionLinks", "authorStance", "Strengthen author stance"),
        ("implications", "sourceIntegration", "Interpret evidence implication"),
        ("usableExamples", "sourceIntegration", "Use evidence as example"),
    ):
        for item in _records(interpretation.get(key))[:2]:
            summary = _text(item.get("summary") or item.get("title"))
            if summary:
                _append_goal(goals, goal_id=f"evidence-{key}-{item.get('id') or len(goals) + 1}", dimension=dimension, source="evidenceInterpretation", message=f"{label}: {summary}", guidance="Use this as interpreted material, not as pasted citation filler.")
    for item in _records(interpretation.get("rejectedEvidenceUses"))[:3]:
        summary = _text(item.get("summary") or item.get("title"))
        if summary:
            _append_goal(goals, goal_id=f"avoid-evidence-{item.get('id') or len(goals) + 1}", dimension="sourceIntegration", source="evidenceInterpretation", message=f"Avoid rejected evidence use: {summary}", guidance="Do not repeat this rejected source move.")


def _append_alternative_angle_goals(goals: list[dict[str, Any]], validation_report: dict[str, Any]) -> None:
    tournament = _record(validation_report.get("alternativeAngleTournament"))
    route = _record(tournament.get("route"))
    if route:
        angle = _text(route.get("angle"))
        why = _text(route.get("whyDifferent"))
        if angle or why:
            _append_goal(goals, goal_id="alternative-angle-lesson", dimension=_dimension_for(angle + " " + why, "ideaStrength"), source="alternativeAngleTournament", message=f"Alternative-angle lesson: {angle or why}", guidance=why or "Use the alternative route lesson if it improves the selected draft.")
        for risk in _strings(route.get("risks"))[:2]:
            _append_goal(goals, goal_id=f"alternative-risk-{len(goals) + 1}", dimension="structure", source="alternativeAngleTournament", message=f"Alternative route risk: {risk}", guidance="Avoid this risk while borrowing any useful angle.")


def _append_material_plan_goals(goals: list[dict[str, Any]], material_plan: dict[str, Any]) -> None:
    plan = _record(material_plan.get("materialPlan")) or material_plan
    for question in _strings(plan.get("openQuestions"))[:2]:
        _append_goal(goals, goal_id=f"material-question-{len(goals) + 1}", dimension="ideaStrength", source="materialPlan", message=f"Open material question: {question}", guidance="Answer or explicitly avoid this gap.")


def _append_rejected_move_goals(goals: list[dict[str, Any]], moves: list[dict[str, Any]]) -> None:
    for move in moves[-4:]:
        reason = _text(move.get("reason"))
        if reason:
            _append_goal(goals, goal_id=f"prior-rejected-{move.get('id') or len(goals) + 1}", dimension="structure", source="revisionLoop", message=f"Prior rejected move: {reason}", guidance="Do not repeat this failed revision move.")


def _append_goal(goals: list[dict[str, Any]], *, goal_id: str, dimension: str, source: str, message: str, guidance: str) -> None:
    if not message or goal_id in {goal.get("id") for goal in goals}:
        return
    goals.append({"id": goal_id, "dimension": dimension if dimension in EDITORIAL_DIMENSIONS else _dimension_for(dimension, "ideaStrength"), "source": source, "message": message, "repairGuidance": guidance, "priority": "high" if source in {"validation", "editorialCritique"} else "medium"})


def _dimension_for(text: str, fallback: str) -> str:
    lowered = text.lower()
    if fallback in EDITORIAL_DIMENSIONS:
        return fallback
    if any(token in lowered for token in ("tension", "conflict", "trade-off", "спор", "конфликт")):
        return "tension"
    if any(token in lowered for token in ("reader", "audience", "value", "польз", "аудитор")):
        return "readerValue"
    if any(token in lowered for token in ("source", "evidence", "proof", "citation", "источник", "доказ")):
        return "sourceIntegration"
    if any(token in lowered for token in ("author", "stance", "position", "автор", "позици")):
        return "authorStance"
    if any(token in lowered for token in ("structure", "opening", "cta", "структур", "начал")):
        return "structure"
    return "ideaStrength"


def _record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [str(item).strip() for item in value if str(item).strip()] if isinstance(value, list) else []


def _text(value: Any, fallback: str = "") -> str:
    return str(value).strip() if value is not None and str(value).strip() else fallback
