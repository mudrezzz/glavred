import { createDefaultRadarEditorialFilters, evaluateSignalAgainstRadarFilters } from '../domain/editorialWorkspace';
import type { RadarDefinition, SourceSignal, Topic, WorkspaceState } from '../domain/editorialWorkspace';

const demoRadars: RadarDefinition[] = [
  {
    id: 'radar-author-memory',
    title: 'Память автора',
    sourceType: 'authorMemory',
    rules: [
      { id: 'rule-author-memory-workflow', operator: 'and', negate: false, statement: 'Искать повторяющиеся мысли про workflow, adoption, evals и trust loop.', status: 'active' },
      { id: 'rule-author-memory-no-model-hype', operator: 'and', negate: true, statement: 'Не брать материал, где главный фокус только на выборе модели.', status: 'active' }
    ],
    sources: [
      { id: 'source-author-memory-feed', type: 'authorArchive', title: 'Лента памяти автора', value: 'authorNotes', notes: 'Локальные заметки и ручные корректировки автора.', status: 'active' }
    ],
    scope: 'Мысли, ручные правки и реакции автора про AI-B2B productization.',
    acceptancePolicy: 'manual',
    triggerMode: 'deficitDriven',
    status: 'active',
    lastRunAt: '2026-06-13T09:00:00.000Z',
    notes: 'Ищет повторяющиеся мотивы в авторских заметках и предлагает их как материал для постов.'
  },
  {
    id: 'radar-archive',
    title: 'Архив постов',
    sourceType: 'archive',
    rules: [
      { id: 'rule-archive-reusable-patterns', operator: 'and', negate: false, statement: 'Находить архивные паттерны, которые можно переосмыслить без самоповтора.', status: 'active' },
      { id: 'rule-archive-no-duplicate-posts', operator: 'and', negate: true, statement: 'Не предлагать материал, слишком похожий на уже выпущенный пост.', status: 'active' }
    ],
    sources: [
      { id: 'source-archive-released-posts', type: 'authorArchive', title: 'Архив выпущенных постов', value: 'archiveRecords', notes: 'Локальный архив релизов и импортированных материалов.', status: 'active' }
    ],
    scope: 'Старые Telegram-посты, доклады и архивные заметки про rollout, trust и evals.',
    acceptancePolicy: 'automaticWithReview',
    triggerMode: 'deficitDriven',
    status: 'needsReview',
    lastRunAt: '2026-06-12T18:30:00.000Z',
    notes: 'Поднимает архивные паттерны, но не делает их evidence без ручного решения.'
  },
  {
    id: 'radar-external-sources',
    title: 'Внешние источники',
    sourceType: 'externalSource',
    rules: [
      { id: 'rule-external-adoption-failures', operator: 'and', negate: false, statement: 'Искать кейсы, где AI-пилот не превратился в регулярный workflow.', status: 'active' },
      { id: 'rule-external-evidence-required', operator: 'and', negate: false, statement: 'В сигнале должны быть фактура, цитата или наблюдение, а не только ссылка.', status: 'active' }
    ],
    sources: [
      { id: 'source-external-interviews', type: 'manualSource', title: 'Customer interviews', value: 'interview notes', notes: 'Демо-заметки интервью без реального API.', status: 'active' },
      { id: 'source-external-open-web', type: 'searchKeywords', title: 'AI adoption research', value: 'AI B2B adoption evals trust rollout', notes: 'Будущая поисковая поверхность.', status: 'active' }
    ],
    scope: 'Customer interviews, blog essays и внешние разборы AI adoption.',
    acceptancePolicy: 'manual',
    triggerMode: 'scheduled',
    status: 'active',
    lastRunAt: '2026-06-11T12:00:00.000Z',
    notes: 'Пока работает как deterministic demo без API, OAuth и crawler.'
  },
  {
    id: 'radar-manual-research',
    title: 'Ручное исследование',
    sourceType: 'manualResearch',
    rules: [
      { id: 'rule-manual-research-product-mechanic', operator: 'and', negate: false, statement: 'Брать материалы, где видна продуктовая механика AI-B2B внедрения.', status: 'active' }
    ],
    sources: [],
    scope: 'Материалы, которые автор вручную занес как сырье для будущего поста.',
    acceptancePolicy: 'manual',
    triggerMode: 'manual',
    status: 'active',
    lastRunAt: '2026-06-10T16:00:00.000Z',
    notes: 'Используется, когда автор хочет быстро зафиксировать источник и свою мысль.'
  }
];

export const demoRadarsWithFilters: RadarDefinition[] = demoRadars.map((radar) => {
  if (radar.id === 'radar-author-memory') {
    return {
      ...radar,
      sourceDiscoveryMode: 'specifiedAndAdditional',
      filters: createDefaultRadarEditorialFilters(radar.id, ['positioning', 'topics'])
    };
  }

  if (radar.id === 'radar-archive') {
    return {
      ...radar,
      sourceDiscoveryMode: 'specifiedOnly',
      filters: createDefaultRadarEditorialFilters(radar.id, ['forbiddenTopics', 'topics'])
    };
  }

  if (radar.id === 'radar-external-sources') {
    return {
      ...radar,
      sourceDiscoveryMode: 'specifiedAndAdditional',
      filters: createDefaultRadarEditorialFilters(radar.id, ['audience', 'positioning', 'forbiddenTopics']).map((filter) =>
        filter.dimension === 'positioning' ? { ...filter, mode: 'seekTension' } : filter
      )
    };
  }

  return {
    ...radar,
    sourceDiscoveryMode: 'autonomous',
    filters: createDefaultRadarEditorialFilters(radar.id, ['goals', 'topics'])
  };
});

const demoSourceSignals: SourceSignal[] = ([
  {
    id: 'signal-ai-demo-to-adoption-gap',
    type: 'Повторяющийся паттерн',
    title: 'AI-B2B пилоты не переходят из demo magic в adoption',
    source: 'Telegram, customer interviews, заметки автора',
    capturedAt: '2026-06-10',
    summary:
      'Несколько команд показывают сильные AI demo, но после пилота usage не становится регулярным. Повторяются причины: не встроен workflow, нет evals, непонятны границы уверенности и нет rollback path.',
    rawNote:
      'Хороший материал для TG-поста: не спорить про модели, а показать разрыв между демо и продуктом. Это лучше относится к GTM/adoption, чем к support automation.',
    radarId: 'radar-author-memory',
    reviewStatus: 'approved',
    suggestedTopicId: 'topic-gtm-adoption-economics',
    suggestedFabulaId: 'fabula-myth-breakdown',
    suggestedValue: 'Показать, почему adoption ломается после пилота и что проверять до rollout.',
    duplicateRisk: 'low'
  },
  {
    id: 'signal-evals-are-product-function',
    type: 'Авторская мысль',
    title: 'Evals должны быть продуктовой функцией, а не лабораторным отчетом',
    source: 'Память автора',
    capturedAt: '2026-06-11',
    summary:
      'Если evals не встроены в пользовательский сценарий и релизный процесс, команда не понимает, улучшился ли AI-продукт после изменений.',
    rawNote:
      'Стоит собрать пост про evals как interface между PM, engineering и пользователем.',
    radarId: 'radar-author-memory',
    reviewStatus: 'new',
    suggestedTopicId: 'topic-evals-quality-loop',
    suggestedFabulaId: 'fabula-practical-framework',
    suggestedValue: 'Дать AI PM практичный способ отличать demo-quality от production-quality.',
    duplicateRisk: 'medium'
  },
  {
    id: 'signal-enterprise-confidence-boundaries',
    type: 'Интервью',
    title: 'Enterprise users требуют объяснять границы уверенности AI-фичи',
    source: 'Customer interviews · AI adoption',
    capturedAt: '2026-06-09',
    summary:
      'В интервью повторяется запрос: пользователю нужно понимать, когда AI уверен, откуда взят ответ и как безопасно откатить решение.',
    rawNote:
      'Можно связать с trust loop: confidence, evidence, rollback, human review.',
    radarId: 'radar-external-sources',
    reviewStatus: 'new',
    suggestedTopicId: 'topic-enterprise-trust-rollout',
    suggestedFabulaId: 'fabula-research-note',
    suggestedValue: 'Показать trust loop как продуктовую часть enterprise AI rollout.',
    duplicateRisk: 'low'
  },
  {
    id: 'signal-procurement-trust-loop',
    type: 'Внешний разбор',
    title: 'Procurement спрашивает не про модель, а про контроль риска внедрения',
    source: 'AI adoption research digest',
    capturedAt: '2026-06-09',
    summary:
      'В обсуждениях enterprise AI повторяется вопрос: как доказать, что система не создаст новый операционный риск после пилота.',
    rawNote:
      'Сигнал полезен для темы enterprise trust: показать, что trust loop начинается с контроля изменений, audit trail и rollback.',
    radarId: 'radar-external-sources',
    reviewStatus: 'new',
    suggestedTopicId: 'topic-enterprise-trust-rollout',
    suggestedFabulaId: 'fabula-practical-framework',
    suggestedValue: 'Объяснить trust loop как практический контур контроля внедрения, а не как юридическую формальность.',
    duplicateRisk: 'medium'
  },
  {
    id: 'signal-rollout-economics',
    type: 'Архивный паттерн',
    title: 'Экономика внедрения ломается, если AI заменяет шаг без владельца процесса',
    source: 'Архив постов',
    capturedAt: '2026-06-08',
    summary:
      'В старых материалах автора повторяется тезис: AI-фича не экономит деньги, если до нее не описан владелец workflow и критерий результата.',
    rawNote:
      'Хорошо ложится в тему GTM/adoption economics, но может дублировать уже опубликованные посты.',
    radarId: 'radar-archive',
    reviewStatus: 'new',
    suggestedTopicId: 'topic-gtm-adoption-economics',
    suggestedFabulaId: 'fabula-pilot-postmortem',
    suggestedValue: 'Разобрать, почему ROI не появляется без ownership и adoption ritual.',
    duplicateRisk: 'high'
  },
  {
    id: 'signal-workflow-automation-architecture',
    type: 'Ручное исследование',
    title: 'Workflow automation architecture важнее выбора модели',
    source: 'Manual research uploads',
    capturedAt: '2026-06-07',
    summary:
      'Сравнение нескольких AI-B2B кейсов показывает, что надежность появляется из очередей, статусов, fallback и audit trail, а не из model-first подхода.',
    rawNote:
      'Можно сделать техническую исследовательскую заметку для CPO/product leaders.',
    radarId: 'radar-manual-research',
    reviewStatus: 'corrected',
    suggestedTopicId: 'topic-workflow-automation-architecture',
    suggestedFabulaId: 'fabula-practical-framework',
    suggestedValue: 'Дать архитектурный фрейм для AI workflow вместо обсуждения модели.',
    duplicateRisk: 'low',
    authorCorrection: 'Автор уточнил: это не support automation, а архитектура workflow и rollout.'
  },
  {
    id: 'signal-demo-magic-hype',
    type: 'Внешний повод',
    title: 'Очередной кейс AI demo без данных о регулярном использовании',
    source: 'Blog essays · Evals and trust',
    capturedAt: '2026-06-06',
    summary:
      'Материал выглядит как повод для поста, но в нем мало фактуры: есть красивое демо, но нет информации о пользователях, evals и adoption.',
    rawNote:
      'Может быть полезен как отрицательный пример, но пока слабый сигнал.',
    radarId: 'radar-external-sources',
    reviewStatus: 'archived',
    suggestedTopicId: 'topic-ai-product-discovery',
    suggestedFabulaId: 'fabula-myth-breakdown',
    suggestedValue: 'Показать, какие вопросы задавать к AI demo до восторга.',
    duplicateRisk: 'medium'
  }
] as SourceSignal[]).map((signal): SourceSignal => ({
  ...signal,
  evidence: [
    {
      id: `evidence-${signal.id}`,
      sourceTitle: signal.source,
      sourceUrl: '',
      quote: signal.summary,
      summary: signal.rawNote
    }
  ],
  searchNote: signal.searchNote ?? `Проверить риск дубля: ${signal.duplicateRisk ?? 'low'}.`
}));

export function createEvaluatedDemoSourceSignals(topics: Topic[]): SourceSignal[] {
  return demoSourceSignals.map((signal) => {
    const radar = demoRadarsWithFilters.find((candidate) => candidate.id === signal.radarId);
    return radar
      ? evaluateSignalAgainstRadarFilters(signal, radar, {
          editorialModel: {
            author: '',
            audience: '',
            positioning: '',
            fabula: '',
            rubrics: [],
            styleRules: [],
            forbiddenTopics: [],
            goals: []
          },
          topics
        } as unknown as WorkspaceState)
      : signal;
  });
}
