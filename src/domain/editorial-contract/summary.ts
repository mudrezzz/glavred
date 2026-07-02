import type { EditorialModel, EditorialRule, EditorialRuleGroup } from '../editorialWorkspace';

const STYLE_GROUPS: EditorialRuleGroup[] = ['styleVoice', 'styleLanguage', 'styleRhythm', 'antiAiPattern'];

export type EditorialContractSummary = {
  author: string;
  audience: string;
  positioning: string;
  styleRules: string[];
  forbiddenTopics: string[];
  goals: string[];
};

export function synthesizeEditorialRulesFromModel(
  model: EditorialModel,
  rules: EditorialRule[]
): EditorialRule[] {
  const next = [...rules];
  addMissingSingleRule(next, 'author', 'Автор', model.author);
  addMissingSingleRule(next, 'audience', 'Аудитория', model.audience);
  addMissingSingleRule(next, 'positioning', 'Позиция', model.positioning);
  addMissingListRules(next, 'goal', 'Цель', model.goals);
  addMissingListRules(next, 'styleVoice', 'Стиль', model.styleRules);
  addMissingListRules(next, 'forbiddenTopic', 'Запрет', model.forbiddenTopics);
  return next;
}

export function summarizeEditorialContract(
  model: EditorialModel,
  rules: EditorialRule[],
  audienceOverride?: string | null
): EditorialContractSummary {
  const active = rules.filter((rule) => rule.status === 'active');
  const author = joinRuleStatements(active, ['author']) || model.author;
  const audience = normalizeText(audienceOverride) || joinRuleStatements(active, ['audience']) || model.audience;
  const positioning = joinRuleStatements(active, ['positioning']) || model.positioning;
  const styleRules = ruleStatementList(active, STYLE_GROUPS, model.styleRules);
  const forbiddenTopics = ruleStatementList(active, ['forbiddenTopic'], model.forbiddenTopics);
  const goals = ruleStatementList(active, ['goal'], model.goals);

  return { author, audience, positioning, styleRules, forbiddenTopics, goals };
}

export function deriveEditorialModelSummary(model: EditorialModel, rules: EditorialRule[]): EditorialModel {
  const summary = summarizeEditorialContract(model, rules);
  return {
    ...model,
    author: summary.author,
    audience: summary.audience,
    positioning: summary.positioning,
    styleRules: summary.styleRules,
    forbiddenTopics: summary.forbiddenTopics,
    goals: summary.goals
  };
}

function addMissingSingleRule(
  rules: EditorialRule[],
  group: EditorialRuleGroup,
  title: string,
  statement: string
) {
  if (hasGroup(rules, group) || !normalizeText(statement)) return;
  rules.push(makeRule(`legacy-${group}`, group, title, statement));
}

function addMissingListRules(
  rules: EditorialRule[],
  group: EditorialRuleGroup,
  title: string,
  statements: string[]
) {
  if (hasGroup(rules, group)) return;
  statements.map(normalizeText).filter(Boolean).forEach((statement, index) => {
    rules.push(makeRule(`legacy-${group}-${index + 1}`, group, title, statement));
  });
}

function hasGroup(rules: EditorialRule[], group: EditorialRuleGroup): boolean {
  return rules.some((rule) => rule.group === group);
}

function makeRule(id: string, group: EditorialRuleGroup, title: string, statement: string): EditorialRule {
  return { id, group, title, statement: statement.trim(), status: 'active' };
}

function joinRuleStatements(rules: EditorialRule[], groups: EditorialRuleGroup[]): string {
  return ruleStatementList(rules, groups, []).join('\n');
}

function ruleStatementList(
  rules: EditorialRule[],
  groups: EditorialRuleGroup[],
  fallback: string[]
): string[] {
  const statements = rules
    .filter((rule) => groups.includes(rule.group))
    .map((rule) => normalizeText(rule.statement))
    .filter(Boolean);
  return statements.length > 0 ? statements : fallback;
}

function normalizeText(value: string | null | undefined): string {
  return typeof value === 'string' ? value.trim() : '';
}
