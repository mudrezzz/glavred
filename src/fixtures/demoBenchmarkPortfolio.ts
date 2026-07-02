import { createAuthorMemoryEvent, inferAuthorPositionAssertions } from '../application/editorialServices';
import {
  createDefaultTopicFabulaMatrix,
  DEFAULT_CONTENT_PLAN_SETTINGS,
  type AuthorExternalSource,
  type AuthorNote,
  type ContentPlanItem,
  type EditorialModel,
  type EditorialRule,
  type Fabula,
  type InsightCard,
  type ProjectProfile,
  type RadarDefinition,
  type SourceSignal,
  type Topic,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import type { PublicationChannel } from '../domain/publication-channels/types';
import { createPublicationChannel } from '../domain/publication-channels/transitions';
import {
  aiDesignPatternsBenchmarkSeed,
  createAiDesignPatternsPublicationChannels
} from './demoAiDesignPatternsProject';
import { createDemoWorkspace } from './demoWorkspace';
import {
  createSevernayaStenaPublicationChannels,
  severnayaStenaBenchmarkSeed
} from './demoSevernayaStenaProject';

export type DemoBenchmarkProjectId =
  | 'project-ai-design-patterns'
  | 'project-kasha-iz-topora'
  | 'project-glavred-blog';

export interface DemoPortfolioBenchmarkExpectation {
  projectId: DemoBenchmarkProjectId;
  language: string;
  defaultPlatform: string;
  benchmarkSignals: string[];
  mustAvoid: string[];
  readyScenarioId: string;
}

export const demoPortfolioBenchmarkExpectations: Record<DemoBenchmarkProjectId, DemoPortfolioBenchmarkExpectation> = {
  'project-ai-design-patterns': {
    projectId: 'project-ai-design-patterns',
    language: 'ru',
    defaultPlatform: 'Telegram',
    readyScenarioId: 'ai-patterns-plan-decision-workbench',
    benchmarkSignals: ['industrial AI scope', 'pattern naming', 'ТОиР evidence', 'community pattern book'],
    mustAvoid: ['generic AI news', 'model leaderboard without industrial context', 'autonomous AI promises without HITL']
  },
  'project-kasha-iz-topora': {
    projectId: 'project-kasha-iz-topora',
    language: 'ru',
    defaultPlatform: 'Telegram',
    readyScenarioId: 'stena-plan-lost-route',
    benchmarkSignals: ['alpinist metaphor', 'complex B2B route', 'RevOps belay', 'field-tested deal pain'],
    mustAvoid: ['student handbook tone', 'mixed pilot metaphor', 'generic sales motivation', 'AI hype as main topic']
  },
  'project-glavred-blog': {
    projectId: 'project-glavred-blog',
    language: 'ru',
    defaultPlatform: 'Telegram',
    readyScenarioId: 'glavred-plan-editorial-memory',
    benchmarkSignals: ['product philosophy', 'practical editorial method', 'build-in-public clarity', 'Telegram/Dzen readiness'],
    mustAvoid: ['generic product marketing', 'opaque AI magic', 'internal trace dump as public prose']
  }
};

export type BenchmarkWorkspaceSeed = {
  projectProfile: ProjectProfile;
  editorialModel: EditorialModel;
  authorNotes: AuthorNote[];
  editorialRules: EditorialRule[];
  topics: Topic[];
  fabulas: Fabula[];
  radars: RadarDefinition[];
  sourceSignals: SourceSignal[];
  externalSources: AuthorExternalSource[];
  defaultPlatform: string;
  defaultPublicationSizeProfileId: string;
  postsPerWeek: number;
  readyScenario: {
    planId: string;
    title: string;
    expectedEffect: string;
    topicId: string;
    fabulaId: string;
    sourceSignalId: string;
    format: string;
  };
};

export function createBenchmarkProjectWorkspace(projectId: DemoBenchmarkProjectId): WorkspaceState {
  const seed = benchmarkWorkspaceSeeds[projectId];
  if (projectId === 'project-ai-design-patterns') return createAiDesignPatternsWorkspace(seed);

  const base = createDemoWorkspace({ includeSeededHitlLearning: false });
  const authorMemoryEvents = seed.authorNotes.map(createAuthorMemoryEvent);
  const topicFabulaMatrix = createDefaultTopicFabulaMatrix(seed.topics, seed.fabulas);
  const sourceSignals = seed.sourceSignals.map(withSignalEvidence);
  const sourceSignal = sourceSignals.find((signal) => signal.id === seed.readyScenario.sourceSignalId) ?? sourceSignals[0];
  const topic = seed.topics.find((item) => item.id === seed.readyScenario.topicId) ?? seed.topics[0];
  const fabula = seed.fabulas.find((item) => item.id === seed.readyScenario.fabulaId) ?? seed.fabulas[0];
  const insightCard = createBenchmarkInsight(seed, sourceSignal, topic, fabula);
  const publicationChannels = createBenchmarkPublicationChannels(projectId, seed);
  const defaultChannel = publicationChannels.find((channel) => channel.status === 'active') ?? publicationChannels[0];
  const contentPlanItems = createBenchmarkPlanItems(seed, defaultChannel);

  const workspace: WorkspaceState = {
    ...base,
    authorNotes: seed.authorNotes,
    authorMemoryEvents,
    authorPositionAssertions: inferAuthorPositionAssertions(seed.authorNotes, authorMemoryEvents),
    editorialModel: seed.editorialModel,
    projectProfile: seed.projectProfile,
    editorialRules: seed.editorialRules,
    editorialValidationRun: null,
    topics: seed.topics,
    fabulas: seed.fabulas,
    topicFabulaMatrix,
    radars: seed.radars,
    sourceSignal,
    sourceSignals,
    insightCard,
    contentPlanItem: contentPlanItems[0],
    contentPlanItems,
    contentPlanSettings: {
      ...DEFAULT_CONTENT_PLAN_SETTINGS,
      period: 'month',
      postsPerWeek: seed.postsPerWeek,
      defaultPlatform: defaultChannel?.title ?? seed.defaultPlatform,
      defaultChannelId: defaultChannel?.id,
      defaultPublicationSizeProfileId: seed.defaultPublicationSizeProfileId,
      publishSlots: [
        { date: '2026-07-01', time: '10:00' },
        { date: '2026-07-03', time: '10:00' },
        { date: '2026-07-06', time: '10:00' }
      ]
    },
    publicationChannels,
    postCandidates: [],
    postCandidate: null,
    postBrief: null,
    postDraft: null,
    editorialChecks: [],
    editorNotes: [],
    finalText: null,
    postVisual: null,
    releasePackage: null,
    editorialLearningNote: null,
    externalSources: seed.externalSources,
    importCandidates: [],
    archiveRecords: [],
    bulkImportActions: [],
    activeSection: 'memory',
    updatedAt: new Date().toISOString()
  };

  return workspace;
}

function createAiDesignPatternsWorkspace(seed: BenchmarkWorkspaceSeed): WorkspaceState {
  const base = createDemoWorkspace({ includeSeededHitlLearning: true });
  const learningNotes = base.authorNotes.filter((note) => note.type === 'editorialLearning');
  const authorNotes = [...seed.authorNotes, ...learningNotes];
  const authorMemoryEvents = authorNotes.map(createAuthorMemoryEvent);
  const topics = seed.topics;
  const fabulas = seed.fabulas;
  const topicFabulaMatrix = createDefaultTopicFabulaMatrix(topics, fabulas);
  const sourceSignals = seed.sourceSignals.map(withSignalEvidence);
  const sourceSignal = sourceSignals.find((signal) => signal.id === seed.readyScenario.sourceSignalId) ?? sourceSignals[0];
  const topic = topics.find((item) => item.id === seed.readyScenario.topicId) ?? topics[0];
  const fabula = fabulas.find((item) => item.id === seed.readyScenario.fabulaId) ?? fabulas[0];
  const insightCard = createBenchmarkInsight(seed, sourceSignal, topic, fabula);
  const publicationChannels = createBenchmarkPublicationChannels('project-ai-design-patterns', seed);
  const defaultChannel = publicationChannels.find((channel) => channel.status === 'active') ?? publicationChannels[0];
  const contentPlanItems = createBenchmarkPlanItems(seed, defaultChannel);

  return {
    ...base,
    projectProfile: seed.projectProfile,
    editorialModel: seed.editorialModel,
    authorNotes,
    authorMemoryEvents,
    authorPositionAssertions: inferAuthorPositionAssertions(authorNotes, authorMemoryEvents),
    editorialRules: seed.editorialRules,
    editorialValidationRun: null,
    topics,
    fabulas,
    topicFabulaMatrix,
    radars: seed.radars,
    sourceSignals,
    sourceSignal,
    insightCard,
    contentPlanItem: contentPlanItems[0],
    contentPlanItems,
    contentPlanSettings: {
      ...DEFAULT_CONTENT_PLAN_SETTINGS,
      period: 'month',
      postsPerWeek: seed.postsPerWeek,
      defaultPlatform: defaultChannel?.title ?? seed.defaultPlatform,
      defaultChannelId: defaultChannel?.id,
      defaultPublicationSizeProfileId: seed.defaultPublicationSizeProfileId,
      maxCandidatesPerSlot: 2,
      publishSlots: [
        { date: '2026-07-01', time: '10:00' },
        { date: '2026-07-08', time: '10:00' }
      ]
    },
    publicationChannels,
    postCandidates: base.postCandidates,
    postCandidate: base.postCandidate,
    postBrief: base.postBrief,
    postDraft: base.postDraft,
    editorialChecks: base.editorialChecks,
    editorNotes: base.editorNotes,
    finalText: base.finalText,
    postVisual: base.postVisual,
    releasePackage: base.releasePackage,
    editorialLearningNote: base.editorialLearningNote,
    externalSources: [...seed.externalSources, ...base.externalSources],
    importCandidates: base.importCandidates,
    archiveRecords: base.archiveRecords,
    bulkImportActions: base.bulkImportActions,
    activeSection: 'memory',
    updatedAt: new Date().toISOString()
  };
}

function createBenchmarkInsight(
  seed: BenchmarkWorkspaceSeed,
  signal: SourceSignal,
  topic: Topic,
  fabula: Fabula
): InsightCard {
  return {
    id: `insight-${seed.readyScenario.planId}`,
    signalId: signal.id,
    title: seed.readyScenario.title,
    whyItMatters: signal.summary,
    audienceRelevance: seed.editorialModel.audience,
    authorPosition: topic.authorStance,
    rubric: topic.title,
    urgency: 'Benchmark scenario: ready to test portfolio-specific drafting quality.',
    score: 0.9,
    banalityRisk: 0.16,
    factGaps: fabula.proofRequirements,
    topicId: topic.id,
    topicTitle: topic.title,
    fabulaId: fabula.id,
    fabulaTitle: fabula.title
  };
}

function createBenchmarkPlanItems(seed: BenchmarkWorkspaceSeed, defaultChannel?: PublicationChannel): ContentPlanItem[] {
  const first = seed.readyScenario;
  return [
    createPlanItem(seed, first, 'Высокий', '2026-07-01', defaultChannel),
    createPlanItem(seed, {
      ...first,
      planId: `${first.planId}-followup`,
      title: `${first.title}: follow-up angle`
    }, 'Нормальный', '2026-07-03', defaultChannel)
  ];
}

function createPlanItem(
  seed: BenchmarkWorkspaceSeed,
  scenario: BenchmarkWorkspaceSeed['readyScenario'],
  priority: string,
  date: string,
  defaultChannel?: PublicationChannel
): ContentPlanItem {
  const topic = seed.topics.find((item) => item.id === scenario.topicId);
  const fabula = seed.fabulas.find((item) => item.id === scenario.fabulaId);
  return {
    id: scenario.planId,
    insightId: `insight-${seed.readyScenario.planId}`,
    title: scenario.title,
    platform: defaultChannel?.title ?? seed.defaultPlatform,
    channelId: defaultChannel?.id,
    date,
    time: '10:00',
    priority,
    format: scenario.format,
    expectedEffect: scenario.expectedEffect,
    approvalStatus: 'draft',
    topicId: scenario.topicId,
    topicTitle: topic?.title,
    fabulaId: scenario.fabulaId,
    fabulaTitle: fabula?.title,
    sourceSignalId: scenario.sourceSignalId,
    publicationSizeProfileId: defaultChannel?.defaultPublicationSizeProfileId ?? seed.defaultPublicationSizeProfileId,
    manualOverride: false,
    weightWarningIds: []
  };
}

function createBenchmarkPublicationChannels(
  projectId: DemoBenchmarkProjectId,
  seed: BenchmarkWorkspaceSeed
): PublicationChannel[] {
  if (projectId === 'project-ai-design-patterns') {
    return createAiDesignPatternsPublicationChannels();
  }

  if (projectId === 'project-glavred-blog') {
    return [
      createPublicationChannel({
        id: 'channel-glavred-telegram',
        projectId,
        platform: 'telegram',
        title: 'Telegram',
        handleOrUrl: '@glavred_product',
        language: 'ru',
        role: 'primary',
        defaultPublicationSizeProfileId: 'telegram-post'
      }),
      createPublicationChannel({
        id: 'channel-glavred-dzen',
        projectId,
        platform: 'dzen',
        title: 'Дзен',
        handleOrUrl: 'dzen.ru/glavred',
        language: 'ru',
        role: 'experiment',
        defaultPublicationSizeProfileId: 'linkedin-article'
      })
    ];
  }

  return createSevernayaStenaPublicationChannels();
}

function withSignalEvidence(signal: SourceSignal): SourceSignal {
  return {
    ...signal,
    evidence: signal.evidence ?? [
      {
        id: `evidence-${signal.id}`,
        sourceTitle: signal.source,
        sourceUrl: '',
        quote: signal.summary,
        summary: signal.rawNote
      }
    ],
    searchNote: signal.searchNote ?? 'Benchmark seed: sanitized source context, not a live ingestion result.'
  };
}

const benchmarkWorkspaceSeeds: Record<DemoBenchmarkProjectId, BenchmarkWorkspaceSeed> = {
  'project-ai-design-patterns': aiDesignPatternsBenchmarkSeed,
  'project-kasha-iz-topora': severnayaStenaBenchmarkSeed,
  'project-glavred-blog': {
    projectProfile: {
      name: 'Блог Главреда',
      description: 'Product philosophy blog about AI-native editorial discipline and practical Glavred usage.',
      setupStatus: 'needsReview'
    },
    editorialModel: {
      author: 'Редактор продукта Главред, который объясняет философию и практику AI-native редакции.',
      audience:
        'Основатели, редакторы, product marketing и контент-команды, которые хотят управлять AI-производством текста как редакционным процессом.',
      positioning:
        'Главред показывает, как AI-пайплайн превращается из генератора текста в управляемую редакционную систему с памятью, проверками и HITL.',
      fabula:
        'Качественный AI-текст рождается не из одного промпта, а из редакционного контура: сигнал, фабула, источники, роли, проверки, правки и обучение памяти автора.',
      rubrics: ['Философия продукта', 'Практика редакции', 'Build in public', 'AI-native workflow'],
      styleRules: [
        'Писать как продуктовый главред: спокойно, предметно, с примерами из пайплайна.',
        'Объяснять внутренние механики через пользу редактора, а не через технический жаргон.',
        'Показывать, где человек принимает решение и чему система учится.'
      ],
      forbiddenTopics: ['Generic AI copywriting tips', 'Маркетинговые обещания без workflow', 'Внутренний trace dump вместо публичного объяснения'],
      goals: [
        'Объяснить философию Главреда и AI-native editorial office.',
        'Показывать практические приемы работы с фабулой, источниками, памятью и HITL.',
        'Готовить будущую multi-platform демонстрацию Telegram + Dzen.'
      ]
    },
    authorNotes: [
      note('glavred-note-not-generator', 'thought', 'Главред - не генератор постов',
        'Ценность продукта в том, что текст проходит редакционный контур: источники, договоренности, роли, проверки и человеческое решение.',
        ['product-philosophy', 'editorial-system'], '2026-06-22T09:00:00.000Z'),
      note('glavred-note-source-ledger', 'thought', 'SourceLedger должен быть понятен редактору',
        'Источники нужны не как механические ссылки в тексте, а как управляемая доказательная база для тезисов и ограничений.',
        ['source-ledger', 'evidence'], '2026-06-22T09:20:00.000Z'),
      note('glavred-note-hitl', 'manualCorrection', 'HITL должен возвращать текст в улучшение',
        'Комментарий редактора - это не заметка на будущее, а активный цикл: версия, правка, проверка, выбор финала и память о решении.',
        ['hitl', 'versions', 'editorial-learning'], '2026-06-22T09:40:00.000Z'),
      note('glavred-note-platform-variants', 'thought', 'Одна идея может жить на разных площадках',
        'Telegram и Dzen требуют разных версий одного замысла: один быстрый и плотный, второй длиннее и объяснительнее.',
        ['platforms', 'telegram', 'dzen'], '2026-06-22T10:00:00.000Z')
    ],
    editorialRules: [
      rule('glavred-rule-author', 'author', 'Product editor voice',
        'Автор объясняет продукт через редакционную практику и конкретные решения пайплайна.'),
      rule('glavred-rule-benefit', 'audience', 'Польза для редактора',
        'Каждый пост должен отвечать, что редактор сможет делать увереннее после прочтения.'),
      rule('glavred-rule-no-jargon', 'styleLanguage', 'Технический жаргон переводить в редакционную пользу',
        'SourceLedger, validators, final gate и HITL можно упоминать только с человеческим объяснением.'),
      rule('glavred-rule-platforms', 'goal', 'Готовить multi-platform мышление',
        'Фабула должна сохраняться, а версия текста адаптироваться под канал.')
    ],
    topics: [
      topic('glavred-topic-editorial-system', 'AI-native editorial system',
        'Почему продукт должен управлять не текстом, а редакционным контуром.',
        'Объяснить Главред как систему решений, а не генератор.',
        'Читатель понимает, где появляется качество и управляемость.',
        'Пайплайн должен показывать, почему текст выбран и какие риски остались.'),
      topic('glavred-topic-hitl-learning', 'HITL и память автора',
        'Как комментарии, версии и финальный выбор редактора становятся наблюдениями в памяти автора.',
        'Показать, что человек не только правит текст, но и обучает редакционную систему.',
        'Читатель видит, как улучшения становятся повторяемыми без скрытого автотренинга.',
        'Редакторское решение должно быть явным артефактом, а не потерянным комментарием.'),
      topic('glavred-topic-platform-variants', 'Telegram + Dzen adaptation',
        'Как одна фабула может породить разные версии для Telegram и Dzen.',
        'Подготовить будущий multi-platform workflow.',
        'Читатель понимает, почему фабула не должна быть прибита к платформе.',
        'Площадка меняет форму, но не должна разрушать источник, позицию и доказательную базу.')
    ],
    fabulas: [
      fabula('glavred-fabula-product-principle', 'Продуктовый принцип',
        'Объяснить один принцип Главреда через проблему редактора и решение продукта.',
        'От боли редактора к продуктовому принципу и рабочему примеру.',
        ['Проблема', 'Почему обычный AI-подход ломается', 'Принцип Главреда', 'Как это работает в практике'],
        ['Пример из текущего пайплайна', 'Польза для редактора'],
        'standard', 'standard', 'auto'),
      fabula('glavred-fabula-practical-case', 'Практический кейс',
        'Показать ситуацию в редактуре и решение через инструменты Главреда.',
        'Сцена -> ход редактора -> артефакт системы -> вывод.',
        ['Сцена', 'Решение', 'Что сохранилось в trace/memory', 'Чему научились'],
        ['Один конкретный workflow', 'Ограничение автоматизации'],
        'standard', 'light', 'auto'),
      fabula('glavred-fabula-platform-explainer', 'Объяснение для двух площадок',
        'Объяснить, как один замысел меняет форму под разные каналы.',
        'От одной фабулы к двум редакционным версиям.',
        ['Общий замысел', 'Telegram-версия', 'Dzen-версия', 'Что нельзя потерять'],
        ['Каналовые требования', 'Сохранение авторской позиции'],
        'deep', 'deep', 'manual', [
          'найти: публичные примеры адаптации одной идеи под короткий пост и длинную статью',
          'проверить: какие элементы нельзя терять при адаптации под канал'
        ])
    ],
    radars: [
      radar('glavred-radar-product-notes', 'Product build notes',
        'Искать заметки о философии Главреда, пайплайне, HITL и learning loop.',
        'Внутренние публично-безопасные заметки продукта.'),
      radar('glavred-radar-user-situations', 'Editorial situations',
        'Искать ситуации, где редактору нужна трассировка, версии или авторская память.',
        'Demo scenarios and sanitized product notes.')
    ],
    sourceSignals: [
      signal('glavred-signal-not-generator', 'Product principle', 'Главред - не генератор постов, а редакционный контур',
        'Product architecture notes', 'Пайплайн собирает источники, контекст, роли, проверки, правки и финальное человеческое решение.',
        'Сильный первый пост для объяснения философии продукта.',
        'glavred-topic-editorial-system', 'glavred-fabula-product-principle'),
      signal('glavred-signal-hitl-memory', 'Workflow case', 'Комментарий редактора должен возвращать текст в улучшение',
        'HITL implementation notes', 'Редактор может давать комментарии, получать версии и выбирать любую версию как финальную; система сохраняет наблюдение в память автора.',
        'Показать HITL как активный цикл, а не форму обратной связи.',
        'glavred-topic-hitl-learning', 'glavred-fabula-practical-case'),
      signal('glavred-signal-telegram-dzen', 'Platform intent', 'Одна фабула должна жить в Telegram и Dzen по-разному',
        'Portfolio roadmap notes', 'Будущая multi-platform механика должна сохранять замысел, но выпускать разные варианты под канал.',
        'Подготовить аудиторию к следующему срезу multi-platform publishing.',
        'glavred-topic-platform-variants', 'glavred-fabula-platform-explainer')
    ],
    externalSources: [
      externalSource('glavred-source-product-docs', 'Glavred product docs', 'document',
        'Current public-safe product docs and roadmap notes.'),
      externalSource('glavred-source-demo-trace', 'Demo DraftRun traces', 'manualUpload',
        'Sanitized examples of validation, final quality gate and HITL traces.')
    ],
    defaultPlatform: 'Telegram',
    defaultPublicationSizeProfileId: 'telegram-post',
    postsPerWeek: 2,
    readyScenario: {
      planId: 'glavred-plan-editorial-memory',
      title: 'Почему Главред - не генератор постов',
      expectedEffect: 'Объяснить продуктовую философию через пользу редактора: качество возникает из контура, а не из одного запроса к модели.',
      topicId: 'glavred-topic-editorial-system',
      fabulaId: 'glavred-fabula-product-principle',
      sourceSignalId: 'glavred-signal-not-generator',
      format: 'Telegram product note'
    }
  }
};

function note(
  id: string,
  type: AuthorNote['type'],
  title: string,
  body: string,
  tags: string[],
  capturedAt: string
): AuthorNote {
  return { id, type, title, body, sourceUrl: '', tags, attachments: [], capturedAt };
}

function rule(id: string, group: EditorialRule['group'], title: string, statement: string): EditorialRule {
  return { id, group, title, statement, status: 'active' };
}

function topic(
  id: string,
  title: string,
  description: string,
  purpose: string,
  audienceValue: string,
  authorStance: string
): Topic {
  return {
    id,
    title,
    description,
    purpose,
    audienceValue,
    authorStance,
    rules: ['Начинать с конкретной ситуации', 'Давать авторскую позицию', 'Заканчивать проверяемым выводом'],
    forbiddenAngles: ['generic AI advice', 'стерильная консультационная вода'],
    weightRange: { min: 20, max: 35 },
    status: 'active'
  };
}

function fabula(
  id: string,
  title: string,
  description: string,
  dramaturgy: string,
  structure: string[],
  proofRequirements: string[],
  sizeIntent: Fabula['sizeIntent'],
  researchDepth: Fabula['researchDepth'],
  researchMode: Fabula['researchStrategy']['mode'],
  instructions: string[] = []
): Fabula {
  return {
    id,
    title,
    description,
    dramaturgy,
    structure,
    proofRequirements,
    rules: ['Не терять авторскую позицию', 'Не подменять вывод списком источников'],
    weightRange: { min: 20, max: 35 },
    sizeIntent,
    researchDepth,
    researchStrategy: { mode: researchMode, instructions },
    status: 'active'
  };
}

function radar(id: string, title: string, ruleStatement: string, scope: string): RadarDefinition {
  return {
    id,
    title,
    sourceType: id.includes('external') ? 'externalSource' : 'authorMemory',
    scope,
    rules: [{ id: `${id}-rule`, operator: 'and', negate: false, statement: ruleStatement, status: 'active' }],
    sources: [
      {
        id: `${id}-source`,
        type: 'manualSource',
        title: `${title} source`,
        value: scope,
        notes: 'Sanitized benchmark seed; real private material is not committed.',
        status: 'active'
      }
    ],
    sourceDiscoveryMode: 'specifiedAndAdditional',
    acceptancePolicy: 'manual',
    triggerMode: 'deficitDriven',
    status: 'active',
    lastRunAt: '2026-06-30T10:00:00.000Z',
    notes: 'Benchmark radar for demo portfolio fixtures.'
  };
}

function signal(
  id: string,
  type: string,
  title: string,
  source: string,
  summary: string,
  rawNote: string,
  topicId: string,
  fabulaId: string
): SourceSignal {
  return {
    id,
    type,
    title,
    source,
    capturedAt: '2026-06-30',
    summary,
    rawNote,
    radarId: `${id.split('-').slice(0, 2).join('-')}-radar`,
    reviewStatus: 'approved',
    suggestedTopicId: topicId,
    suggestedFabulaId: fabulaId,
    suggestedValue: rawNote,
    duplicateRisk: 'low'
  };
}

function externalSource(
  id: string,
  title: string,
  type: AuthorExternalSource['type'],
  notes: string
): AuthorExternalSource {
  return {
    id,
    type,
    title,
    url: '',
    fileReference: '',
    status: 'needsReview',
    importMode: 'reviewedQueue',
    lastCheckedAt: '2026-06-30',
    lastImportedAt: '',
    notes
  };
}
