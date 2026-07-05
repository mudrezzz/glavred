"""Owner: drafting.application.revision

Used by: DraftRun revision package migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any


def _constraint_for(reason: str) -> str:
    if "ideaStrength" in reason:
        return "Do not weaken the central idea while fixing validators."
    if "source" in reason or "attribution" in reason:
        return "Do not remove visible source markers or weaken source integration."
    if "warning" in reason or "critical" in reason:
        return "Do not introduce new deterministic validator findings."
    return f"Do not repeat rejected move: {reason[:180]}"


class RevisionRejectedMovePolicy:
    """Owns rejected-move extraction and anti-regression constraints for revision cycles."""

    def rejected_moves_from_cycle(
        self,
        *,
        cycle_number: int,
        revised_candidate: dict[str, Any] | None,
        rejection_reasons: list[str],
        unresolved_editorial_goals: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        candidate_id = str((revised_candidate or {}).get("id") or f"cycle-{cycle_number}")
        moves: list[dict[str, Any]] = []
        for index, reason in enumerate(rejection_reasons[:4], start=1):
            moves.append({
                "id": f"rejected-cycle-{cycle_number}-{index}",
                "cycleNumber": cycle_number,
                "candidateId": candidate_id,
                "reason": reason,
                "constraint": _constraint_for(reason),
            })
        for goal in unresolved_editorial_goals[:4]:
            message = str(goal.get("message") or goal.get("id") or "").strip()
            if message:
                moves.append({
                    "id": f"unresolved-goal-cycle-{cycle_number}-{goal.get('id') or len(moves) + 1}",
                    "cycleNumber": cycle_number,
                    "candidateId": candidate_id,
                    "reason": f"Unresolved editorial goal: {message}",
                    "constraint": f"Do not ignore editorial goal: {message[:180]}",
                })
        return moves

    def constraints_from_rejected_moves(self, moves: list[dict[str, Any]]) -> list[str]:
        return [str(move.get("constraint") or move.get("reason")) for move in moves if str(move.get("constraint") or move.get("reason") or "").strip()]

    def constraints_from_editorial_goals(self, goals: list[dict[str, Any]]) -> list[str]:
        return [f"Still unresolved editorial goal: {message}" for message in self.goal_messages(goals[:6])]

    def goal_messages(self, goals: list[dict[str, Any]]) -> list[str]:
        return [str(goal.get("message") or goal.get("id")) for goal in goals if str(goal.get("message") or goal.get("id") or "").strip()]

    def cycle_stop_reason(self, accepted: bool, unresolved_goals: list[str], unresolved_editorial_goals: list[dict[str, Any]]) -> str:
        if not accepted:
            return "no-fresh-angle"
        if unresolved_goals or unresolved_editorial_goals:
            return "max-iterations"
        return "editorially-improved"
