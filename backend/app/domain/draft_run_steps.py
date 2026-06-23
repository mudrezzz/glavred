from enum import StrEnum


class DraftRunStepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class DraftRunStepKey(StrEnum):
    CONTEXT = "context"
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
    DraftRunStepKey.CONTEXT: "Сбор контекста",
    DraftRunStepKey.FEASIBILITY: "Проверка возможности",
    DraftRunStepKey.POST_CONTRACT: "Контракт поста",
    DraftRunStepKey.RULE_PACK: "Правила издательства",
    DraftRunStepKey.MATERIAL_PLAN: "План материалов",
    DraftRunStepKey.STRATEGY: "Стратегия драфта",
    DraftRunStepKey.RHETORICAL_PLANS: "Риторические планы",
    DraftRunStepKey.DRAFT: "Черновик текста",
    DraftRunStepKey.VALIDATION: "Проверка результата",
    DraftRunStepKey.COMPLETE: "Завершение",
}
