from typing import Any

from backend.app.application.draft_rule_pack_sections import (
    as_dict,
    as_list_of_dicts,
    candidate_constraints,
    dramaturgy_requirements,
    evidence_requirements,
    forbidden_moves,
    publisher_constraints,
    quality_rubric,
    topic_fit_requirements,
)
from backend.app.domain.draft_rule_pack import RulePack


class DraftRulePackCompiler:
    def compile(self, context_summary: dict[str, Any]) -> RulePack:
        brief = as_dict(context_summary.get("brief"))
        topic = as_dict(context_summary.get("topic"))
        fabula = as_dict(context_summary.get("fabula"))
        candidate = as_dict(context_summary.get("candidate"))
        signal = as_dict(context_summary.get("sourceSignal"))
        publisher_rules = as_dict(context_summary.get("publisherRules"))
        missing_context = as_list_of_dicts(context_summary.get("missingContext"))

        hard_constraints, soft_constraints = publisher_constraints(publisher_rules)
        hard_constraints.extend(candidate_constraints(candidate))

        return RulePack(
            draft_intent={
                "title": brief.get("title"),
                "thesis": brief.get("thesis"),
                "audience": brief.get("audience"),
                "conflict": brief.get("conflict"),
                "authorPosition": brief.get("authorPosition"),
                "cta": brief.get("cta"),
            },
            hard_constraints=hard_constraints,
            soft_constraints=soft_constraints,
            evidence_requirements=evidence_requirements(brief, candidate, signal, fabula),
            dramaturgy_requirements=dramaturgy_requirements(fabula),
            topic_fit_requirements=topic_fit_requirements(topic),
            quality_rubric=quality_rubric(),
            forbidden_moves=forbidden_moves(topic, publisher_rules, candidate),
            metadata={
                "version": "rule-pack-v1",
                "briefOnly": bool(context_summary.get("compatibility", {}).get("briefOnly")),
                "missingContextCount": len(missing_context),
            },
            warnings=missing_context,
        )
