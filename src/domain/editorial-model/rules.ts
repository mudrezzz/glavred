import type { EditorialRule, EditorialRuleGroup } from './types';

// Atomic editorial rules are independent validation units used by setup and future draft validators.
export function getRulesByGroup(rules: EditorialRule[], group: EditorialRuleGroup): EditorialRule[] {
  return rules.filter((rule) => rule.group === group);
}

export function createEditorialRule(
  group: EditorialRuleGroup,
  title: string,
  statement: string
): EditorialRule {
  return {
    id: `rule-${group}-${Date.now()}`,
    group,
    title,
    statement,
    status: 'active'
  };
}

export function updateEditorialRule(rules: EditorialRule[], rule: EditorialRule): EditorialRule[] {
  return rules.map((item) => (item.id === rule.id ? rule : item));
}

export function deleteEditorialRule(rules: EditorialRule[], ruleId: string): EditorialRule[] {
  return rules.filter((rule) => rule.id !== ruleId);
}
