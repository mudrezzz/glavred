from typing import Any


def candidate_selection_blocked_payload(artifact: dict[str, Any]) -> dict[str, Any]:
    selection = artifact.get("selection") if isinstance(artifact.get("selection"), dict) else {}
    scorecard = selection.get("scorecard") if isinstance(selection.get("scorecard"), list) else []
    blocked_candidates = [
        {
            "candidateId": score.get("candidateId"),
            "selectionStatus": score.get("selectionStatus"),
            "selectionReasons": score.get("selectionReasons"),
        }
        for score in scorecard
        if isinstance(score, dict)
    ]
    return {
        "status": "blocked",
        "blockedBy": "draftCandidateSelection",
        "reason": selection.get("reason") or "No publishable draft candidate passed the selection guard.",
        "candidateIds": [item.get("candidateId") for item in blocked_candidates if item.get("candidateId")],
        "blockedCandidates": blocked_candidates,
    }
