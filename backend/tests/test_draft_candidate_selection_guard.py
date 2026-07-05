from backend.app.drafting.application.generation.draft_candidate_selection_service import DraftCandidateSelectionService


def test_candidate_selector_prefers_stronger_score() -> None:
    selection = DraftCandidateSelectionService().select(
        [
            {"id": "weak", "title": "Weak", "body": "short", "usedEvidence": [], "ruleCoverage": [], "risks": ["risk"]},
            {
                "id": "strong",
                "title": "Strong",
                "body": "AI topic conflict with practical checks",
                "usedEvidence": ["e1", "e2"],
                "ruleCoverage": ["r1", "r2", "r3"],
                "risks": [],
            },
        ]
    )

    assert selection.selected_candidate_id == "strong"
    assert selection.scorecard[1].total > selection.scorecard[0].total


def test_candidate_selector_excludes_fallback_when_provider_candidate_is_publishable() -> None:
    selection = DraftCandidateSelectionService().select(
        [
            {
                "id": "fallback",
                "title": "Fallback",
                "body": "AI topic conflict with practical checks",
                "source": "deterministicFallback",
                "fallbackUsed": True,
                "usedEvidence": ["e1", "e2", "e3"],
                "ruleCoverage": ["r1", "r2", "r3", "r4"],
                "risks": [],
            },
            {
                "id": "provider",
                "title": "Provider",
                "body": "AI topic conflict with practical checks",
                "source": "openrouter",
                "fallbackUsed": False,
                "usedEvidence": ["e1"],
                "ruleCoverage": ["r1"],
                "risks": ["risk"],
            },
        ]
    )

    assert selection.selected_candidate_id == "provider"
    fallback_score = next(score for score in selection.scorecard if score.candidate_id == "fallback")
    assert fallback_score.selection_status == "excluded"
    assert "fallback-candidate-provider-alternative" in fallback_score.selection_reasons


def test_candidate_selector_excludes_raw_artifact_dump() -> None:
    selection = DraftCandidateSelectionService().select(
        [
            {
                "id": "raw",
                "title": "Raw",
                "body": "Evidence: {'id': 'public-evidence-1', 'type': 'source'}",
                "source": "openrouter",
                "fallbackUsed": False,
            }
        ]
    )

    assert selection.selected_candidate_id is None
    assert selection.scorecard[0].selection_status == "excluded"
    assert "raw-artifact-dump" in selection.scorecard[0].selection_reasons


def test_candidate_selector_excludes_provider_rewrite_weakness() -> None:
    selection = DraftCandidateSelectionService().select(
        [
            {
                "id": "rewrite",
                "title": "Rewrite",
                "body": "Draft body",
                "source": "deterministicFallback",
                "fallbackUsed": True,
                "weaknesses": ["Needs provider rewrite before publication"],
            }
        ]
    )

    assert selection.selected_candidate_id is None
    assert selection.scorecard[0].selection_status == "excluded"
    assert "needs-provider-rewrite" in selection.scorecard[0].selection_reasons
