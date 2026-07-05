"""Owner: drafting.application.planning

Used by: DraftRun planning migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.domain.draft_rhetorical_plan import (
    RhetoricalMove,
    RhetoricalPlan,
    RhetoricalPlanClaimUse,
    RhetoricalPlanSet,
)


class DeterministicRhetoricalPlanService:
    def create_plans(
        self,
        *,
        context_summary: dict[str, Any],
        rule_registry: dict[str, Any],
        post_contract: dict[str, Any],
        material_plan: dict[str, Any],
        draft_strategy: dict[str, Any],
    ) -> RhetoricalPlanSet:
        topic = _get(context_summary, "topic", "title") or _get(context_summary, "brief", "rubric") or "topic"
        thesis = str(post_contract.get("thesis") or draft_strategy.get("thesisAngle") or "approved thesis")
        cta = str(post_contract.get("cta") or draft_strategy.get("ctaPlan") or "editorial CTA")
        claim_ids = _claim_ids(post_contract)
        rule_ids = _rule_ids(rule_registry)
        risky = _strings(material_plan.get("riskyClaims"))
        return RhetoricalPlanSet(
            plans=[
                self._research(topic, thesis, cta, claim_ids, rule_ids, risky),
                self._contrast(topic, thesis, cta, claim_ids, rule_ids, risky),
                self._practical(topic, thesis, cta, claim_ids, rule_ids, risky),
            ]
        )

    def _research(self, topic: str, thesis: str, cta: str, claim_ids: list[str], rule_ids: list[str], risks: list[str]) -> RhetoricalPlan:
        return RhetoricalPlan(
            id="research",
            title="Исследовательский маршрут",
            angle=f"Разобрать {topic} через доказательства и тезис: {thesis}.",
            opening_move="Начать с наблюдения, затем показать, какие факты удерживают позицию.",
            moves=[
                RhetoricalMove("Наблюдение", "Зафиксировать исходный сигнал и контекст.", claim_ids[:1]),
                RhetoricalMove("Доказательства", "Разложить доступные подтверждения без усиления фактов.", claim_ids[:3]),
                RhetoricalMove("Вывод", "Свести факты к авторской позиции и CTA.", []),
            ],
            claims_to_use=_claim_uses(claim_ids),
            required_rule_ids=rule_ids[:6],
            size_intent="standard",
            cta_route=cta,
            risks=risks,
            why_this_plan="Лучше подходит, когда важна доказательность и аккуратная авторская позиция.",
        )

    def _contrast(self, topic: str, thesis: str, cta: str, claim_ids: list[str], rule_ids: list[str], risks: list[str]) -> RhetoricalPlan:
        return RhetoricalPlan(
            id="contrast",
            title="Контрастный маршрут",
            angle=f"Показать, какая привычная трактовка темы {topic} ломается о тезис: {thesis}.",
            opening_move="Открыть конфликтом между видимой простотой и реальным ограничением.",
            moves=[
                RhetoricalMove("Контраст", "Назвать ложное удобство или миф.", []),
                RhetoricalMove("Разворот", "Подкрепить разворот разрешенными claims.", claim_ids[:2]),
                RhetoricalMove("Позиция", "Закрыть авторским критерием действия.", []),
            ],
            claims_to_use=_claim_uses(claim_ids[:2]),
            claim_ids_to_avoid=[],
            required_rule_ids=rule_ids[:6],
            size_intent="compact",
            cta_route=cta,
            risks=risks,
            why_this_plan="Дает более сильную драматургию, если нужен sharp angle без новых фактов.",
        )

    def _practical(self, topic: str, thesis: str, cta: str, claim_ids: list[str], rule_ids: list[str], risks: list[str]) -> RhetoricalPlan:
        return RhetoricalPlan(
            id="practical",
            title="Практический маршрут",
            angle=f"Превратить {topic} в набор проверок, сохранив тезис: {thesis}.",
            opening_move="Начать с практической ситуации и сразу дать критерий проверки.",
            moves=[
                RhetoricalMove("Ситуация", "Назвать рабочий сценарий читателя.", []),
                RhetoricalMove("Проверки", "Разложить тезис на действия и ограничения.", claim_ids[:3]),
                RhetoricalMove("CTA", "Подвести к следующему редакционному действию.", []),
            ],
            claims_to_use=_claim_uses(claim_ids[:3]),
            required_rule_ids=rule_ids[:6],
            size_intent="standard",
            cta_route=cta,
            risks=risks,
            why_this_plan="Лучше подходит, когда пост должен дать аудитории прикладную пользу.",
        )


def _claim_uses(claim_ids: list[str]) -> list[RhetoricalPlanClaimUse]:
    return [RhetoricalPlanClaimUse(claim_id=claim_id, use="support") for claim_id in claim_ids]


def _claim_ids(contract: dict[str, Any]) -> list[str]:
    claims = contract.get("claims")
    if not isinstance(claims, list):
        return []
    ids: list[str] = []
    for item in claims:
        if isinstance(item, dict) and item.get("claimId"):
            ids.append(str(item["claimId"]))
        elif isinstance(item, dict) and item.get("id"):
            ids.append(str(item["id"]))
    return ids


def _rule_ids(registry: dict[str, Any]) -> list[str]:
    rules = registry.get("rules")
    if not isinstance(rules, list):
        return []
    return [str(item.get("id")) for item in rules if isinstance(item, dict) and item.get("id")]


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _get(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for key in path:
        current = current.get(key) if isinstance(current, dict) else None
    return current


DeterministicRhetoricalPlanFallbackService = DeterministicRhetoricalPlanService


__all__ = (
    'DeterministicRhetoricalPlanService',
    'DeterministicRhetoricalPlanFallbackService',
)
