from enum import StrEnum


class DraftRunStepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class DraftRunStepKey(StrEnum):
    CONTEXT = "context"
    SOURCE_INTENT = "sourceIntent"
    PUBLIC_EVIDENCE = "publicEvidence"
    FEASIBILITY = "feasibility"
    POST_CONTRACT = "postContract"
    RULE_PACK = "rulePack"
    MATERIAL_PLAN = "materialPlan"
    STRATEGY = "strategy"
    RHETORICAL_PLANS = "rhetoricalPlans"
    DRAFT = "draft"
    VALIDATION = "validation"
    COMPLETE = "complete"


DRAFT_RUN_STEP_ORDER: tuple[DraftRunStepKey, ...] = (
    DraftRunStepKey.CONTEXT,
    DraftRunStepKey.SOURCE_INTENT,
    DraftRunStepKey.PUBLIC_EVIDENCE,
    DraftRunStepKey.FEASIBILITY,
    DraftRunStepKey.POST_CONTRACT,
    DraftRunStepKey.RULE_PACK,
    DraftRunStepKey.MATERIAL_PLAN,
    DraftRunStepKey.STRATEGY,
    DraftRunStepKey.RHETORICAL_PLANS,
    DraftRunStepKey.DRAFT,
    DraftRunStepKey.VALIDATION,
    DraftRunStepKey.COMPLETE,
)


STEP_TITLES: dict[DraftRunStepKey, str] = {
    DraftRunStepKey.CONTEXT: "Context",
    DraftRunStepKey.SOURCE_INTENT: "Source plan",
    DraftRunStepKey.PUBLIC_EVIDENCE: "Public evidence",
    DraftRunStepKey.FEASIBILITY: "Feasibility",
    DraftRunStepKey.POST_CONTRACT: "Post contract",
    DraftRunStepKey.RULE_PACK: "Rule pack",
    DraftRunStepKey.MATERIAL_PLAN: "Material plan",
    DraftRunStepKey.STRATEGY: "Draft strategy",
    DraftRunStepKey.RHETORICAL_PLANS: "Rhetorical plans",
    DraftRunStepKey.DRAFT: "Draft candidates",
    DraftRunStepKey.VALIDATION: "Validation",
    DraftRunStepKey.COMPLETE: "Complete",
}
