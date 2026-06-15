import type { AuthorPositionAssertion } from '../author-memory/types';
import { clampPercent } from '../shared/numbers';
import type { WeightRange } from '../shared/types';
import type { WorkspaceState } from '../workspace/types';
import type {
  CompatibleTopicFabula,
  EditorialRule,
  EditorialRuleGroup,
  EditorialValidationItem,
  EditorialValidationRun,
  EditorialValidationStatus,
  EditorialValidationSummary,
  Fabula,
  Topic,
  TopicFabulaMatrixEntry,
  TopicFabulaWarning,
  ValidatorDefinition,
  ValidatorEvidence,
  ValidatorResult,
  ValidatorRun,
  ValidatorStatus,
} from './types';

// Pure editorial-model transitions and deterministic setup validators.
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

export function validateEditorialSetupLegacy(workspace: WorkspaceState): EditorialValidationSummary {
  const warnings = getTopicFabulaWarnings(workspace.topics, workspace.fabulas, workspace.topicFabulaMatrix);
  const activeRules = workspace.editorialRules.filter((rule) => rule.status === 'active');
  const antiAiRules = getRulesByGroup(activeRules, 'antiAiPattern');
  const goalRules = getRulesByGroup(activeRules, 'goal');
  const styleRules = [
    ...getRulesByGroup(activeRules, 'styleVoice'),
    ...getRulesByGroup(activeRules, 'styleLanguage'),
    ...getRulesByGroup(activeRules, 'styleRhythm')
  ];
  const items: EditorialValidationItem[] = [
    {
      id: 'validation-project-profile',
      status: workspace.projectProfile.name.trim() && workspace.projectProfile.description.trim() ? 'green' : 'yellow',
      title: 'Профиль проекта',
      summary: workspace.projectProfile.name.trim()
        ? `Проект задан как "${workspace.projectProfile.name}".`
        : 'У проекта нет явного названия.',
      recommendation: workspace.projectProfile.name.trim()
        ? 'Использовать название как верхний контекст редакционного кабинета.'
        : 'Добавить название проекта перед настройкой правил.'
    },
    {
      id: 'validation-editorial-rules',
      status: activeRules.length >= 10 ? 'green' : 'yellow',
      title: 'Атомарные правила',
      summary: `${activeRules.length} активных правил описывают издательство.`,
      recommendation:
        activeRules.length >= 10
          ? 'Правил достаточно для первого deterministic review.'
          : 'Добавить правила автора, аудитории, позиции, стиля и целей.'
    },
    {
      id: 'validation-style-anti-ai',
      status: antiAiRules.length > 0 && styleRules.length >= 3 ? 'green' : 'yellow',
      title: 'Стиль и anti-AI',
      summary: `${styleRules.length} style rules, ${antiAiRules.length} anti-AI rules.`,
      recommendation:
        antiAiRules.length > 0
          ? 'Anti-AI правила можно использовать в будущем валидаторе редакторского тона.'
          : 'Добавить хотя бы одно правило против стерильного AI-текста.'
    },
    {
      id: 'validation-topic-fabula-matrix',
      status: warnings.length === 0 ? 'green' : 'red',
      title: 'Матрица тем и фабул',
      summary: warnings.length === 0 ? 'Все активные сущности имеют связки.' : `${warnings.length} сущностей без связок.`,
      recommendation:
        warnings.length === 0
          ? 'Матрица пригодна для планирования.'
          : 'Вернуть хотя бы одну совместимую связку для каждой активной темы и фабулы.'
    },
    {
      id: 'validation-goal-fit',
      status: goalRules.length > 0 ? 'yellow' : 'red',
      title: 'Цели блога',
      summary: goalRules.length > 0 ? `${goalRules.length} целей заданы как правила.` : 'Цели не заданы.',
      recommendation:
        'Следующий слой должен сверить цели с образом автора, аудиторией, темами и будущими метриками.'
    }
  ];
  const status: EditorialValidationStatus = items.some((item) => item.status === 'red')
    ? 'red'
    : items.some((item) => item.status === 'yellow')
      ? 'yellow'
      : 'green';

  return {
    status,
    title: status === 'green' ? 'Редакционная модель согласована' : 'Редакционная модель требует внимания',
    summary:
      'Проверка deterministic: оценивает профиль проекта, атомарность правил, стиль, anti-AI слой, цели и матрицу совместимости.',
    items
  };
}

export function runEditorialSetupValidators(workspace: WorkspaceState): ValidatorRun {
  const results = [
    validateAuthorPositionClarity(workspace),
    validateAntiAiStyleCoverage(workspace),
    validateAudienceValueFit(workspace),
    validateGoalConsistency(workspace),
    validateTopicFabulaCoverage(workspace)
  ];

  return {
    id: `validator-run-${Date.now()}`,
    revision: workspace.editorialSetupRevision ?? 0,
    checkedAt: new Date().toISOString(),
    results
  };
}

export function createEditorialValidationRun(
  workspace: WorkspaceState,
  checkedAt = new Date().toISOString()
): EditorialValidationRun {
  const run = runEditorialSetupValidators(workspace);
  const normalizedRun = { ...run, checkedAt };
  const aggregateStatus = getValidatorRunStatus(normalizedRun.results);
  const aggregateScore = getValidatorRunScore(normalizedRun.results);

  return {
    ...normalizedRun,
    aggregateStatus,
    aggregateScore,
    summary: summarizeValidatorRun(normalizedRun)
  };
}

export function validateEditorialSetup(workspace: WorkspaceState): EditorialValidationSummary {
  return summarizeValidatorRun(runEditorialSetupValidators(workspace));
}

export function summarizeValidatorRun(run: ValidatorRun): EditorialValidationSummary {
  const status = getValidatorRunStatus(run.results);
  const aggregateScore = getValidatorRunScore(run.results);

  return {
    status,
    title: status === 'green' ? 'Редакционная модель согласована' : 'Редакционная модель требует внимания',
    summary: `Проверено ${run.results.length} валидаторов. Средний score: ${Math.round(aggregateScore * 100)}%.`,
    items: run.results.map((result) => ({
      id: result.id,
      status: result.status,
      title: validatorDefinitionTitle(result.validatorId),
      summary: result.summary,
      recommendation: result.suggestions[0]?.description ?? 'Критичных рекомендаций нет.'
    }))
  };
}

export function getValidatorRunStatus(results: ValidatorResult[]): ValidatorStatus {
  if (results.some((result) => result.status === 'red')) return 'red';
  if (results.some((result) => result.status === 'yellow')) return 'yellow';
  return 'green';
}

export function getValidatorRunScore(results: ValidatorResult[]): number {
  if (results.length === 0) return 0;

  return Math.round((results.reduce((sum, result) => sum + result.score, 0) / results.length) * 100) / 100;
}

export function validatorDefinitionTitle(validatorId: string): string {
  return VALIDATOR_DEFINITIONS.find((definition) => definition.id === validatorId)?.title ?? validatorId;
}

export const VALIDATOR_DEFINITIONS: ValidatorDefinition[] = [
  {
    id: 'author-position-clarity',
    title: 'Позиция автора',
    description: 'Проверяет, есть ли ясная авторская позиция и evidence из авторской памяти.',
    targetTypes: ['authorPositionAssertion', 'editorialSetup']
  },
  {
    id: 'anti-ai-style-coverage',
    title: 'Стиль и anti-AI слой',
    description: 'Проверяет, что стиль задан правилами и есть защита от стерильного AI-текста.',
    targetTypes: ['editorialRule', 'editorialSetup']
  },
  {
    id: 'audience-value-fit',
    title: 'Ценность для аудитории',
    description: 'Проверяет связь тем и правил с пользой для AI PM, founders и product leaders.',
    targetTypes: ['editorialRule', 'topic', 'editorialSetup']
  },
  {
    id: 'goal-consistency',
    title: 'Согласованность целей',
    description: 'Проверяет, что цели блога поддержаны автором, аудиторией, темами и будущими метриками.',
    targetTypes: ['projectProfile', 'editorialRule', 'topic', 'editorialSetup']
  },
  {
    id: 'topic-fabula-coverage',
    title: 'Покрытие тем и фабул',
    description: 'Проверяет, что активные темы и фабулы имеют связи в матрице.',
    targetTypes: ['topic', 'fabula', 'topicFabulaMatrix']
  }
];

function validateAuthorPositionClarity(workspace: WorkspaceState): ValidatorResult {
  const assertionsWithEvidence = workspace.authorPositionAssertions.filter((assertion) => assertion.evidence.length > 0);
  const status: ValidatorStatus =
    assertionsWithEvidence.length >= 3 ? 'green' : assertionsWithEvidence.length > 0 ? 'yellow' : 'red';
  const evidence = assertionsWithEvidence.slice(0, 3).map((assertion, index) => ({
    id: `author-position-evidence-${index + 1}`,
    type: assertion.type,
    title: assertion.title,
    quote: assertion.evidence[0]?.quote ?? assertion.statement,
    sourceId: assertion.evidence[0]?.noteId ?? assertion.id,
    reason: assertion.evidence[0]?.reason ?? 'Вывод о позиции автора уже зафиксирован в памяти.'
  }));

  return {
    id: 'validator-author-position-clarity',
    validatorId: 'author-position-clarity',
    targetType: 'authorPositionAssertion',
    targetId: 'author-position',
    status,
    score: status === 'green' ? 0.92 : status === 'yellow' ? 0.62 : 0.2,
    summary:
      status === 'green'
        ? 'Авторская позиция читается через несколько подтвержденных выводов из памяти.'
        : status === 'yellow'
          ? 'Позиция автора есть, но evidence пока недостаточно для уверенной настройки издательства.'
          : 'Позиция автора не подтверждена заметками и правками.',
    evidence,
    suggestions:
      status === 'green'
        ? []
        : [
            {
              id: 'author-position-add-evidence',
              title: 'Добавить evidence из памяти',
              description: 'Зафиксируйте еще несколько мыслей или корректировок, которые объясняют отношение автора к AI-B2B продуктам.',
              severity: status === 'red' ? 'critical' : 'warning'
            }
          ]
  };
}

function validateAntiAiStyleCoverage(workspace: WorkspaceState): ValidatorResult {
  const activeRules = workspace.editorialRules.filter((rule) => rule.status === 'active');
  const antiAiRules = getRulesByGroup(activeRules, 'antiAiPattern');
  const styleRules = [
    ...getRulesByGroup(activeRules, 'styleVoice'),
    ...getRulesByGroup(activeRules, 'styleLanguage'),
    ...getRulesByGroup(activeRules, 'styleRhythm')
  ];
  const status: ValidatorStatus =
    antiAiRules.length > 0 && styleRules.length >= 3
      ? 'green'
      : antiAiRules.length > 0 || styleRules.length >= 2
        ? 'yellow'
        : 'red';
  const evidenceRules = [...antiAiRules, ...styleRules].slice(0, 4);

  return {
    id: 'validator-anti-ai-style-coverage',
    validatorId: 'anti-ai-style-coverage',
    targetType: 'editorialRule',
    targetId: 'style-rules',
    status,
    score: status === 'green' ? 0.88 : status === 'yellow' ? 0.58 : 0.28,
    summary: `${styleRules.length} style rules, ${antiAiRules.length} anti-AI rules.`,
    evidence: evidenceRules.map((rule) => ({
      id: `style-evidence-${rule.id}`,
      type: rule.group,
      title: rule.title,
      quote: rule.statement,
      sourceId: rule.id,
      reason: 'Правило будет использоваться как проверяемое ограничение для будущих драфтов.'
    })),
    suggestions:
      antiAiRules.length > 0
        ? [
            {
              id: 'anti-ai-expand',
              title: 'Развить anti-AI паттерны',
              description: 'Добавьте запреты на пустые вводные, универсальные советы и стерильный тон, чтобы валидатор мог ловить больше типовых AI-приемов.',
              severity: 'info'
            }
          ]
        : [
            {
              id: 'anti-ai-missing',
              title: 'Добавить anti-AI правила',
              description: 'Сейчас стиль не защищен от стерильного AI-текста. Нужны отдельные правила против обобщений и псевдоэкспертной подачи.',
              severity: 'critical'
            }
          ]
  };
}

function validateAudienceValueFit(workspace: WorkspaceState): ValidatorResult {
  const audienceRules = getRulesByGroup(
    workspace.editorialRules.filter((rule) => rule.status === 'active'),
    'audience'
  );
  const activeTopics = workspace.topics.filter((topic) => topic.status === 'active');
  const topicsWithValue = activeTopics.filter((topic) => topic.audienceValue.trim().length > 0);
  const status: ValidatorStatus =
    audienceRules.length > 0 && topicsWithValue.length === activeTopics.length
      ? 'green'
      : topicsWithValue.length > 0
        ? 'yellow'
        : 'red';

  return {
    id: 'validator-audience-value-fit',
    validatorId: 'audience-value-fit',
    targetType: 'topic',
    targetId: 'audience-value',
    status,
    score: status === 'green' ? 0.86 : status === 'yellow' ? 0.6 : 0.25,
    summary: `${topicsWithValue.length} из ${activeTopics.length} активных тем объясняют ценность для аудитории.`,
    evidence: [
      ...audienceRules.slice(0, 2).map((rule) => ({
        id: `audience-rule-${rule.id}`,
        type: rule.group,
        title: rule.title,
        quote: rule.statement,
        sourceId: rule.id,
        reason: 'Правило описывает, кому и зачем нужен блог.'
      })),
      ...topicsWithValue.slice(0, 2).map((topic) => ({
        id: `audience-topic-${topic.id}`,
        type: 'topic',
        title: topic.title,
        quote: topic.audienceValue,
        sourceId: topic.id,
        reason: 'Тема содержит явную ценность для читателя.'
      }))
    ],
    suggestions:
      status === 'green'
        ? []
        : [
            {
              id: 'audience-value-fill-gaps',
              title: 'Дописать ценность тем',
              description: 'У каждой активной темы должна быть проверяемая польза для AI PM, founders или product leaders.',
              severity: status === 'red' ? 'critical' : 'warning'
            }
          ]
  };
}

function validateGoalConsistency(workspace: WorkspaceState): ValidatorResult {
  const activeRules = workspace.editorialRules.filter((rule) => rule.status === 'active');
  const goalRules = getRulesByGroup(activeRules, 'goal');
  const authorRules = getRulesByGroup(activeRules, 'author');
  const audienceRules = getRulesByGroup(activeRules, 'audience');
  const hasSupportingContext = authorRules.length > 0 && audienceRules.length > 0 && workspace.topics.some((topic) => topic.status === 'active');
  const status: ValidatorStatus =
    goalRules.length > 0 && hasSupportingContext ? 'yellow' : goalRules.length > 0 ? 'yellow' : 'red';

  return {
    id: 'validator-goal-consistency',
    validatorId: 'goal-consistency',
    targetType: 'editorialSetup',
    targetId: 'goals',
    status,
    score: status === 'yellow' && hasSupportingContext ? 0.68 : status === 'yellow' ? 0.52 : 0.2,
    summary:
      goalRules.length > 0
        ? 'Цели заданы и поддержаны настройками издательства, но пока не декомпозированы в метрики.'
        : 'Цели блога не заданы как валидируемые правила.',
    evidence: goalRules.slice(0, 3).map((rule) => ({
      id: `goal-evidence-${rule.id}`,
      type: rule.group,
      title: rule.title,
      quote: rule.statement,
      sourceId: rule.id,
      reason: 'Цель участвует в проверке согласованности издательства.'
    })),
    suggestions: [
      {
        id: 'goal-add-metrics',
        title: 'Декомпозировать цель в метрики',
        description: 'Следующий слой должен связать цель блога с метриками: подписки, сохранения, входящие запросы, лиды и качество аудитории.',
        severity: goalRules.length > 0 ? 'warning' : 'critical'
      }
    ]
  };
}

function validateTopicFabulaCoverage(workspace: WorkspaceState): ValidatorResult {
  const warnings = getTopicFabulaWarnings(workspace.topics, workspace.fabulas, workspace.topicFabulaMatrix);
  const status: ValidatorStatus = warnings.length === 0 ? 'green' : 'red';

  return {
    id: 'validator-topic-fabula-coverage',
    validatorId: 'topic-fabula-coverage',
    targetType: 'topicFabulaMatrix',
    targetId: 'topic-fabula-matrix',
    status,
    score: status === 'green' ? 0.94 : Math.max(0.2, 1 - warnings.length / 5),
    summary:
      warnings.length === 0
        ? 'Все активные темы и фабулы имеют хотя бы одну совместимую связку.'
        : `${warnings.length} активных сущностей потеряли связи в матрице.`,
    evidence:
      warnings.length > 0
        ? warnings.map((warning) => ({
            id: `matrix-warning-${warning.targetType}-${warning.targetId}`,
            type: warning.targetType,
            title: warning.title,
            quote: warning.message,
            sourceId: warning.targetId,
            reason: 'Без связи сущность не попадет в контент-план.'
          }))
        : [
            {
              id: 'matrix-coverage-ok',
              type: 'topicFabulaMatrix',
              title: 'Матрица совместимости',
              quote: `${workspace.topics.length} тем, ${workspace.fabulas.length} фабул, ${workspace.topicFabulaMatrix.filter((entry) => entry.enabled).length} активных связей.`,
              sourceId: 'topic-fabula-matrix',
              reason: 'Матрица пригодна для планирования первого контент-потока.'
            }
          ],
    suggestions:
      warnings.length === 0
        ? []
        : [
            {
              id: 'matrix-restore-links',
              title: 'Вернуть совместимые связки',
              description: 'Включите хотя бы одну фабулу для каждой активной темы и хотя бы одну тему для каждой активной фабулы.',
              severity: 'critical'
            }
          ]
  };
}

export function normalizeWeightRange(range: WeightRange): WeightRange {
  const min = clampPercent(range.min);
  const max = clampPercent(range.max);

  return min <= max ? { min, max } : { min: max, max: min };
}

export function createTopicDraft(): Topic {
  return {
    id: `topic-custom-${Date.now()}`,
    title: '',
    description: '',
    purpose: '',
    audienceValue: '',
    authorStance: '',
    rules: [],
    forbiddenAngles: [],
    weightRange: { min: 5, max: 15 },
    status: 'active'
  };
}

export function createFabulaDraft(): Fabula {
  return {
    id: `fabula-custom-${Date.now()}`,
    title: '',
    description: '',
    dramaturgy: '',
    structure: [],
    proofRequirements: [],
    rules: [],
    weightRange: { min: 5, max: 15 },
    status: 'active'
  };
}

export function addTopic(topics: Topic[], topic: Topic): Topic[] {
  return [...topics, { ...topic, weightRange: normalizeWeightRange(topic.weightRange) }];
}

export function addFabula(fabulas: Fabula[], fabula: Fabula): Fabula[] {
  return [...fabulas, { ...fabula, weightRange: normalizeWeightRange(fabula.weightRange) }];
}

export function deleteTopic(
  topics: Topic[],
  matrix: TopicFabulaMatrixEntry[],
  topicId: string
): { topics: Topic[]; matrix: TopicFabulaMatrixEntry[] } {
  return {
    topics: topics.filter((topic) => topic.id !== topicId),
    matrix: matrix.filter((entry) => entry.topicId !== topicId)
  };
}

export function deleteFabula(
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[],
  fabulaId: string
): { fabulas: Fabula[]; matrix: TopicFabulaMatrixEntry[] } {
  return {
    fabulas: fabulas.filter((fabula) => fabula.id !== fabulaId),
    matrix: matrix.filter((entry) => entry.fabulaId !== fabulaId)
  };
}

export function createDefaultTopicFabulaMatrix(
  topics: Topic[],
  fabulas: Fabula[]
): TopicFabulaMatrixEntry[] {
  return topics.flatMap((topic) =>
    fabulas.map((fabula) => ({
      topicId: topic.id,
      fabulaId: fabula.id,
      enabled: true
    }))
  );
}

export function completeTopicFabulaMatrix(
  topics: Topic[],
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[]
): TopicFabulaMatrixEntry[] {
  const existing = new Map(matrix.map((entry) => [`${entry.topicId}:${entry.fabulaId}`, entry.enabled]));

  return topics.flatMap((topic) =>
    fabulas.map((fabula) => {
      const key = `${topic.id}:${fabula.id}`;

      return {
        topicId: topic.id,
        fabulaId: fabula.id,
        enabled: existing.get(key) ?? true
      };
    })
  );
}

export function isTopicFabulaEnabled(
  matrix: TopicFabulaMatrixEntry[],
  topicId: string,
  fabulaId: string
): boolean {
  return matrix.find((entry) => entry.topicId === topicId && entry.fabulaId === fabulaId)?.enabled ?? true;
}

export function selectCompatibleTopicFabula(
  topics: Topic[],
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[]
): CompatibleTopicFabula | null {
  const activeTopics = topics.filter((topic) => topic.status === 'active');
  const activeFabulas = fabulas.filter((fabula) => fabula.status === 'active');

  for (const topic of activeTopics) {
    const fabula = activeFabulas.find((item) => isTopicFabulaEnabled(matrix, topic.id, item.id));

    if (fabula) {
      return { topic, fabula };
    }
  }

  return null;
}

export function getTopicFabulaWarnings(
  topics: Topic[],
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[]
): TopicFabulaWarning[] {
  const activeTopics = topics.filter((topic) => topic.status === 'active');
  const activeFabulas = fabulas.filter((fabula) => fabula.status === 'active');
  const topicWarnings = activeTopics
    .filter((topic) => !activeFabulas.some((fabula) => isTopicFabulaEnabled(matrix, topic.id, fabula.id)))
    .map((topic) => ({
      targetType: 'topic' as const,
      targetId: topic.id,
      title: topic.title,
      message: 'У темы нет активных фабул. Она не попадет в план, пока матрица не включит хотя бы одну связку.'
    }));
  const fabulaWarnings = activeFabulas
    .filter((fabula) => !activeTopics.some((topic) => isTopicFabulaEnabled(matrix, topic.id, fabula.id)))
    .map((fabula) => ({
      targetType: 'fabula' as const,
      targetId: fabula.id,
      title: fabula.title,
      message: 'Фабула не применима ни к одной активной теме. Она не будет использоваться в планировании.'
    }));

  return [...topicWarnings, ...fabulaWarnings];
}
