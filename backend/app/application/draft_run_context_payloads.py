from typing import Any

from backend.app.domain.draft_run_context import DraftRunContext


def context_from_payload(payload: dict[str, Any]) -> DraftRunContext | None:
    raw_context = payload.get("draftContext")
    if not isinstance(raw_context, dict):
        return None
    return DraftRunContext(
        work_item=_dict_or_none(raw_context.get("workItem")),
        plan_slot=_dict_or_none(raw_context.get("planSlot")),
        candidate=_dict_or_none(raw_context.get("candidate")),
        source_signal=_dict_or_none(raw_context.get("sourceSignal")),
        topic=_dict_or_none(raw_context.get("topic")),
        fabula=_dict_or_none(raw_context.get("fabula")),
        project_profile=_dict_or_empty(raw_context.get("projectProfile")),
        editorial_model=_dict_or_empty(raw_context.get("editorialModel")),
        publisher_rules=_list_of_dicts(raw_context.get("publisherRules")),
        author_position_evidence=_list_of_dicts(raw_context.get("authorPositionEvidence")),
        publication_size=_dict_or_empty(raw_context.get("publicationSize")),
        missing_context=_list_of_dicts(raw_context.get("missingContext")),
    )


def context_to_payload(context: DraftRunContext) -> dict[str, Any]:
    return {
        "workItem": context.work_item,
        "planSlot": context.plan_slot,
        "candidate": context.candidate,
        "sourceSignal": context.source_signal,
        "topic": context.topic,
        "fabula": context.fabula,
        "projectProfile": context.project_profile,
        "editorialModel": context.editorial_model,
        "publisherRules": context.publisher_rules,
        "authorPositionEvidence": context.author_position_evidence,
        "publicationSize": context.publication_size,
        "missingContext": context.missing_context,
    }


def context_input_summary(context: DraftRunContext) -> dict[str, Any]:
    return {
        "hasWorkItem": context.work_item is not None,
        "hasPlanSlot": context.plan_slot is not None,
        "hasCandidate": context.candidate is not None,
        "hasSourceSignal": context.source_signal is not None,
        "hasTopic": context.topic is not None,
        "hasFabula": context.fabula is not None,
        "publisherRuleCount": len(context.publisher_rules),
        "authorEvidenceCount": len(context.author_position_evidence),
        "hasPublicationSize": bool(context.publication_size),
        "missingContextCount": len(context.missing_context),
    }


def _dict_or_none(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
