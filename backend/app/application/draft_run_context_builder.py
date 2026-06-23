from collections import defaultdict
from typing import Any

from backend.app.domain.draft_generation import DraftGenerationRequest
from backend.app.domain.draft_run_context import DraftRunContext, DraftRunContextSummary


def build_draft_run_context_summary(
    request: DraftGenerationRequest,
    context: DraftRunContext | None,
) -> dict[str, Any]:
    if context is None:
        return {
            "brief": _brief_summary(request),
            "workItem": None,
            "planSlot": None,
            "candidate": None,
            "sourceSignal": None,
            "topic": None,
            "fabula": None,
            "publisherRules": {
                "total": len(request.editorial_model.style_rules)
                + len(request.editorial_model.forbidden_topics)
                + len(request.editorial_model.goals),
                "groups": {
                    "styleRules": request.editorial_model.style_rules,
                    "forbiddenTopics": request.editorial_model.forbidden_topics,
                    "goals": request.editorial_model.goals,
                },
            },
            "authorPositionEvidence": {"total": 0, "items": []},
            "publicationSize": {},
            "missingContext": [],
            "compatibility": {"briefOnly": True},
        }

    summary = DraftRunContextSummary(
        brief=_brief_summary(request),
        work_item=_pick(
            context.work_item,
            "id",
            "title",
            "platform",
            "date",
            "time",
            "topicId",
            "fabulaId",
            "stage",
            "status",
        ),
        plan_slot=_pick(
            context.plan_slot,
            "id",
            "title",
            "platform",
            "date",
            "time",
            "approvalStatus",
            "expectedEffect",
            "topicId",
            "fabulaId",
        ),
        candidate=_pick(
            context.candidate,
            "id",
            "title",
            "thesis",
            "audience",
            "value",
            "goal",
            "platform",
            "confidence",
            "risks",
            "evidenceSummary",
        ),
        source_signal=_pick(
            context.source_signal,
            "id",
            "title",
            "source",
            "summary",
            "rawNote",
            "evidence",
            "authorCorrection",
        ),
        topic=_pick(
            context.topic,
            "id",
            "title",
            "purpose",
            "audienceValue",
            "authorStance",
            "rules",
            "forbiddenAngles",
            "weightRange",
        ),
        fabula=_pick(
            context.fabula,
            "id",
            "title",
            "dramaturgy",
            "structure",
            "proofRequirements",
            "rules",
            "weightRange",
        ),
        publisher_rules=_group_rules(context.publisher_rules),
        author_position_evidence={
            "total": len(context.author_position_evidence),
            "items": context.author_position_evidence[:10],
        },
        publication_size=context.publication_size,
        missing_context=context.missing_context,
    )
    return summary.to_payload()


def _brief_summary(request: DraftGenerationRequest) -> dict[str, Any]:
    return {
        "id": request.brief.id,
        "title": request.brief.title,
        "rubric": request.brief.rubric,
        "audience": request.brief.audience or request.editorial_model.audience,
        "thesis": request.brief.thesis,
        "conflict": request.brief.conflict,
        "authorPosition": request.brief.author_position,
        "cta": request.brief.cta,
        "evidenceCount": len(request.brief.evidence),
        "sourceCount": len(request.brief.sources),
    }


def _pick(source: dict[str, Any] | None, *keys: str) -> dict[str, Any] | None:
    if source is None:
        return None
    return {key: source.get(key) for key in keys if key in source}


def _group_rules(rules: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rule in rules:
        group = str(rule.get("group") or "unknown")
        groups[group].append(
            _pick(rule, "id", "title", "statement", "status", "evidenceNoteId") or {}
        )
    return {"total": len(rules), "groups": dict(groups)}
