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
import { createDemoWorkspace } from './demoWorkspace';

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
    language: 'en',
    defaultPlatform: 'LinkedIn',
    readyScenarioId: 'ai-patterns-plan-execution-layer',
    benchmarkSignals: ['pattern naming', 'anti-hype synthesis', 'external evidence', 'English-ready prose'],
    mustAvoid: ['new-tool roundup', 'model leaderboard without operating context', 'generic AI optimism']
  },
  'project-kasha-iz-topora': {
    projectId: 'project-kasha-iz-topora',
    language: 'ru',
    defaultPlatform: 'Telegram',
    readyScenarioId: 'kasha-plan-complex-sales',
    benchmarkSignals: ['strong stance', 'living Telegram voice', 'RevOps detail', 'field-tested B2B sales logic'],
    mustAvoid: ['consulting memo tone', 'CRM jargon without scene', 'generic sales motivation']
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

type BenchmarkWorkspaceSeed = {
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
  const contentPlanItems = createBenchmarkPlanItems(seed);

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
      defaultPlatform: seed.defaultPlatform,
      defaultPublicationSizeProfileId: seed.defaultPublicationSizeProfileId,
      publishSlots: [
        { date: '2026-07-01', time: '10:00' },
        { date: '2026-07-03', time: '10:00' },
        { date: '2026-07-06', time: '10:00' }
      ]
    },
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
  const legacy = createDemoWorkspace({ includeSeededHitlLearning: true });
  const authorNotes = [legacy.authorNotes[0], ...seed.authorNotes, ...legacy.authorNotes.slice(1)];
  const authorMemoryEvents = authorNotes.map(createAuthorMemoryEvent);
  const topics = [...legacy.topics, ...seed.topics];
  const fabulas = [...legacy.fabulas, ...seed.fabulas];
  const sourceSignals = [...legacy.sourceSignals, ...seed.sourceSignals.map(withSignalEvidence)];
  const contentPlanItems = [...legacy.contentPlanItems, ...createBenchmarkPlanItems(seed)];

  return {
    ...legacy,
    projectProfile: seed.projectProfile,
    editorialModel: {
      ...legacy.editorialModel,
      positioning: `${legacy.editorialModel.positioning} ${seed.editorialModel.positioning}`,
      rubrics: Array.from(new Set([...legacy.editorialModel.rubrics, ...seed.editorialModel.rubrics])),
      styleRules: Array.from(new Set([...legacy.editorialModel.styleRules, ...seed.editorialModel.styleRules])),
      forbiddenTopics: Array.from(new Set([...legacy.editorialModel.forbiddenTopics, ...seed.editorialModel.forbiddenTopics])),
      goals: Array.from(new Set([...legacy.editorialModel.goals, ...seed.editorialModel.goals]))
    },
    authorNotes,
    authorMemoryEvents,
    authorPositionAssertions: inferAuthorPositionAssertions(authorNotes, authorMemoryEvents),
    editorialRules: [...legacy.editorialRules, ...seed.editorialRules],
    topics,
    fabulas,
    topicFabulaMatrix: createDefaultTopicFabulaMatrix(topics, fabulas),
    radars: [...seed.radars, ...legacy.radars],
    sourceSignals,
    sourceSignal: legacy.sourceSignal,
    contentPlanItems,
    contentPlanSettings: {
      ...legacy.contentPlanSettings,
      maxCandidatesPerSlot: Math.max(legacy.contentPlanSettings.maxCandidatesPerSlot, 2)
    },
    externalSources: [...legacy.externalSources, ...seed.externalSources],
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

function createBenchmarkPlanItems(seed: BenchmarkWorkspaceSeed): ContentPlanItem[] {
  const first = seed.readyScenario;
  return [
    createPlanItem(seed, first, 'Высокий', '2026-07-01'),
    createPlanItem(seed, {
      ...first,
      planId: `${first.planId}-followup`,
      title: `${first.title}: follow-up angle`
    }, 'Нормальный', '2026-07-03')
  ];
}

function createPlanItem(
  seed: BenchmarkWorkspaceSeed,
  scenario: BenchmarkWorkspaceSeed['readyScenario'],
  priority: string,
  date: string
): ContentPlanItem {
  const topic = seed.topics.find((item) => item.id === scenario.topicId);
  const fabula = seed.fabulas.find((item) => item.id === scenario.fabulaId);
  return {
    id: scenario.planId,
    insightId: `insight-${seed.readyScenario.planId}`,
    title: scenario.title,
    platform: seed.defaultPlatform,
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
    publicationSizeProfileId: seed.defaultPublicationSizeProfileId,
    manualOverride: false,
    weightWarningIds: []
  };
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
  'project-ai-design-patterns': {
    projectProfile: {
      name: 'AI Design Patterns',
      description: 'English-capable research blog about durable AI product and engineering patterns.',
      setupStatus: 'needsReview'
    },
    editorialModel: {
      author: 'AI systems practitioner who curates durable design patterns from scattered field knowledge.',
      audience:
        'AI product leaders, staff engineers, founders and technical product teams who need reliable AI systems, not tool hype.',
      positioning:
        'Anti-hype synthesis: turn noisy AI practice into named patterns with evidence, constraints and operating guidance.',
      fabula:
        'The value is not in announcing a new tool, but in explaining the repeatable pattern that makes AI useful in a real workflow.',
      rubrics: ['Pattern catalog', 'Applied AI architecture', 'Evidence and evals', 'Enterprise reliability'],
      styleRules: [
        'Write in clear English by default, with pattern names and practical trade-offs.',
        'Separate what works now from what is still experimental.',
        'Use public evidence and concrete system boundaries before advice.'
      ],
      forbiddenTopics: ['New model hype without operational lesson', 'Tool roundup without pattern', 'Benchmark ranking as the main point'],
      goals: [
        'Build authority as a curator of durable AI design patterns.',
        'Help teams reason about context, evidence, tools, orchestration and validation.',
        'Create a reusable pattern catalog for AI product and engineering teams.'
      ]
    },
    authorNotes: [
      note('ai-pattern-execution-layer', 'thought', 'AI as an execution layer, not a chat box',
        'The durable pattern is not "ask the model better". It is an execution layer: understand context, find grounds, call tools, produce a structured artifact and leave an audit trail.',
        ['execution-layer', 'orchestration', 'tools'], '2026-06-20T09:00:00.000Z'),
      note('ai-pattern-evidence-first', 'thought', 'Evidence before generation',
        'For enterprise AI, retrieval is not decoration. The system needs visible grounds before it is allowed to state conclusions.',
        ['evidence', 'rag', 'enterprise'], '2026-06-20T09:20:00.000Z'),
      note('ai-pattern-context-budget', 'manualCorrection', 'Too much context is also a bug',
        'A long context window does not replace context design. Good systems select context packs by role and purpose instead of dumping the whole trace.',
        ['context', 'rag', 'context-pack'], '2026-06-20T09:40:00.000Z'),
      note('ai-pattern-validator-layer', 'thought', 'Reliability is layered outside the model',
        'The useful question is not which model is smartest. It is where schemas, deterministic checks, evals and human review compensate for model limits.',
        ['validators', 'evals', 'reliability'], '2026-06-20T10:00:00.000Z')
    ],
    editorialRules: [
      rule('ai-pattern-rule-author', 'author', 'Pattern curator, not AI news commentator',
        'Author must extract a reusable pattern from noisy AI practice instead of reacting to new tools.'),
      rule('ai-pattern-rule-evidence', 'positioning', 'Claims need operating evidence',
        'Every serious recommendation should name its evidence source, limitation or failure mode.'),
      rule('ai-pattern-rule-language', 'styleLanguage', 'English-ready technical clarity',
        'Use concise English terms for patterns, but explain them through workflow scenes.'),
      rule('ai-pattern-rule-no-hype', 'forbiddenTopic', 'No model hype as thesis',
        'Do not make the model leaderboard the main argument.')
    ],
    topics: [
      topic('ai-pattern-topic-execution-layer', 'AI execution layer',
        'Patterns for turning model output into controlled process execution.',
        'Explain the architecture between user intent and reliable output.',
        'Readers get a repeatable map: context, evidence, orchestration, tools, schema, validation.',
        'AI value appears when the model is embedded into a controlled execution contour.'),
      topic('ai-pattern-topic-context-packs', 'Context packs and article memory',
        'How AI systems select the right context without flooding the model.',
        'Show context engineering as product architecture, not prompt decoration.',
        'Readers learn when to preserve memory, compress it, or retrieve only the relevant cards.',
        'Good context is curated by role and task; raw trace dumping is a reliability risk.'),
      topic('ai-pattern-topic-reliability', 'Reliability layers',
        'Evals, deterministic validators, schemas and human review as design patterns.',
        'Translate model uncertainty into engineering controls.',
        'Readers get practical reliability layers for production AI systems.',
        'Reliable AI is model capability plus external discipline.')
    ],
    fabulas: [
      fabula('ai-pattern-fabula-pattern-card', 'Pattern card',
        'Name a durable pattern, show when it applies, why it works and where it breaks.',
        'From noisy practice to a named reusable pattern.',
        ['Problem signal', 'Pattern name', 'Operating mechanism', 'Failure modes', 'How to apply'],
        ['At least two public examples or sources', 'One failure mode or limitation'],
        'deep', 'deep', 'manual', [
          'find: recent public examples of AI systems using tools, RAG, schemas or validators in production',
          'verify: whether the examples show actual workflow execution, not only demo output',
          'do not use: vendor launch posts without operational detail'
        ]),
      fabula('ai-pattern-fabula-architecture-note', 'Architecture note',
        'Explain a system boundary or component choice through trade-offs.',
        'From architecture smell to a safer AI system design.',
        ['Architecture smell', 'Why it fails', 'Better boundary', 'Implementation checklist'],
        ['Concrete system boundary', 'Trade-off or cost'],
        'standard', 'standard', 'auto'),
      fabula('ai-pattern-fabula-anti-hype', 'Anti-hype teardown',
        'Challenge a fashionable AI claim and replace it with a more useful pattern.',
        'From hype claim to operational criterion.',
        ['Hype claim', 'What it hides', 'Operational criterion', 'Better question'],
        ['Public claim or example', 'Author stance'],
        'standard', 'light', 'auto')
    ],
    radars: [
      radar('ai-pattern-radar-public-practice', 'Public AI engineering practice',
        'Search for mature public examples of AI architecture, RAG, orchestration and evaluation.',
        'AI engineering essays, product architecture writeups and public talks.'),
      radar('ai-pattern-radar-author-notes', 'Author pattern notes',
        'Extract repeated patterns from author memory and manual research notes.',
        'Local author memory and imported research snippets.')
    ],
    sourceSignals: [
      signal('ai-pattern-signal-execution-layer', 'Pattern candidate', 'AI systems are moving from answers to controlled execution',
        'Sanitized enterprise AI deck', 'A strong pattern emerges: useful AI systems collect context, find grounds, call tools, produce structured output and keep auditability.',
        'Use this to write a pattern card about AI as an execution layer rather than a chat UI.',
        'ai-pattern-topic-execution-layer', 'ai-pattern-fabula-pattern-card'),
      signal('ai-pattern-signal-context-overload', 'Architecture smell', 'Long context does not solve context selection',
        'Author memory and public architecture discussions', 'Teams with huge context windows still need role-specific context packs, summarization and retrieval discipline.',
        'Good scenario for explaining ArticleDossier and ContextPack as a general AI product pattern.',
        'ai-pattern-topic-context-packs', 'ai-pattern-fabula-architecture-note'),
      signal('ai-pattern-signal-reliability-layers', 'Reliability note', 'Model limits are compensated by engineering layers',
        'Sanitized enterprise AI deck', 'Hallucination, nondeterminism and context limits require schemas, deterministic checks, evals and human review.',
        'Turn this into an anti-hype note: reliability is designed outside the model too.',
        'ai-pattern-topic-reliability', 'ai-pattern-fabula-anti-hype')
    ],
    externalSources: [
      externalSource('ai-pattern-source-enterprise-deck', 'Enterprise AI architecture deck', 'document',
        'Sanitized notes from a private deck about AI as execution layer and reliability controls.'),
      externalSource('ai-pattern-source-public-practice', 'Public AI engineering essays', 'blogSite',
        'Future reviewed queue for public examples of production AI patterns.')
    ],
    defaultPlatform: 'LinkedIn',
    defaultPublicationSizeProfileId: 'linkedin-article',
    postsPerWeek: 1,
    readyScenario: {
      planId: 'ai-patterns-plan-execution-layer',
      title: 'AI execution layer: Pattern card',
      expectedEffect: 'Produce an English-ready pattern card that explains AI as controlled execution, not a chat answer.',
      topicId: 'ai-pattern-topic-execution-layer',
      fabulaId: 'ai-pattern-fabula-pattern-card',
      sourceSignalId: 'ai-pattern-signal-execution-layer',
      format: 'LinkedIn article / pattern card'
    }
  },
  'project-kasha-iz-topora': {
    projectProfile: {
      name: 'Каша из топора',
      description: 'Telegram-native RevOps and Product Marketing blog about complex B2B commercialization.',
      setupStatus: 'needsReview'
    },
    editorialModel: {
      author: 'Практик product commercialization и RevOps для сложных B2B-продуктов.',
      audience:
        'Основатели, CPO, коммерческие директора, product marketing и sales leaders, которые продают сложные продукты длинным корпоративным циклом.',
      positioning:
        'Ироничный, практичный разбор того, почему сложный B2B нельзя продать как коробку: нужна связка клиент, ценность, сделка, материалы и изменение.',
      fabula:
        'Продажи сложного B2B ломаются не из-за слабой презентации, а из-за отсутствия повторяемой системы: рынок, ценность, CRM, материалы, обучение и аналитика.',
      rubrics: ['Каша из топора', 'RevOps field notes', 'Product commercialization', 'Сложные B2B-продажи'],
      styleRules: [
        'Писать живым Telegram-голосом: жестко, иронично, но с практической пользой.',
        'Начинать с наблюдения из продаж или внедрения, а не с консалтингового определения.',
        'Давать управленческую рамку, но не превращать пост в презентационный слайд.'
      ],
      forbiddenTopics: ['Мотивационные продажи без механики', 'CRM ради CRM', 'Консалтинговая вода без полевого примера'],
      goals: [
        'Собрать вокруг автора аудиторию, которой нужна коммерциализация сложных B2B-продуктов.',
        'Показать опыт связки product, marketing, sales, presale, delivery и внедрения.',
        'Превратить прошлую продуктово-коммерческую практику в узнаваемую авторскую оптику.'
      ]
    },
    authorNotes: [
      note('kasha-note-box-sales', 'thought', 'Сложный B2B не продается как коробка',
        'Если клиент покупает изменение процесса, презентация продукта сама по себе почти ничего не решает. Нужны проблема, экономика, ЛПР, процесс, ТКП, закупка и внедрение.',
        ['complex-b2b', 'sales', 'value'], '2026-06-21T09:00:00.000Z'),
      note('kasha-note-five-questions', 'thought', 'Пять вопросов повторяемых продаж',
        'Клиент, ценность, сделка, материалы, измерение - без этих пяти вопросов продажи превращаются в героизм отдельных людей.',
        ['revops', 'sales-system', 'crm'], '2026-06-21T09:20:00.000Z'),
      note('kasha-note-bant-plus', 'manualCorrection', 'BANT+ нужен как дисциплина сделки, а не табличка',
        'Скоринг сделки полезен только если меняет поведение команды: кого зовем, какой риск закрываем, какой следующий шаг доказывает движение.',
        ['bant', 'scoring', 'crm'], '2026-06-21T09:40:00.000Z'),
      note('kasha-note-loss-to-action', 'thought', 'Loss-to-Action как язык ценности',
        'Сильная B2B-ценность появляется, когда финансовая потеря переводится в управляемый кейс: причина, действие, эффект, владелец и проверка результата.',
        ['loss-to-action', 'value', 'industrial-ai'], '2026-06-21T10:00:00.000Z'),
      note('kasha-note-sales-materials', 'linkReaction', 'Материалы вооружают продажи',
        'Sales kit нужен не для красоты. Он должен помогать пройти разговор с разными ролями: инженер, ИТ, производство, закупки, финансы, топ-менеджмент.',
        ['sales-enablement', 'materials', 'roles'], '2026-06-21T10:20:00.000Z')
    ],
    editorialRules: [
      rule('kasha-rule-author', 'author', 'Полевой коммерческий практик',
        'Автор говорит из опыта вывода сложных B2B-продуктов на рынок, а не как внешний консультант.'),
      rule('kasha-rule-voice', 'styleVoice', 'Ирония плюс польза',
        'Можно шутить и спорить, но каждый пост должен оставлять рабочую рамку или критерий.'),
      rule('kasha-rule-position', 'positioning', 'Повторяемая система важнее героизма продаж',
        'Главная позиция: сложные продажи надо превращать в систему, а не оставлять на харизме отдельных людей.'),
      rule('kasha-rule-forbidden-memo', 'forbiddenTopic', 'Не консультационный меморандум',
        'Не писать сухим языком отчета или презентации без живой сцены.')
    ],
    topics: [
      topic('kasha-topic-complex-sales', 'Сложные B2B-продажи',
        'Почему корпоративная сделка требует системы, а не только продукта и презентации.',
        'Показать механику повторяемых продаж.',
        'Читатель видит, где у него ломается коммерческий контур.',
        'Сложный B2B продается через управляемое изменение клиента, а не через демо функции.'),
      topic('kasha-topic-revops-crm', 'RevOps и CRM-дисциплина',
        'CRM, BANT+, этапы, критерии перехода и аналитика SQL как операционная система продаж.',
        'Снять романтику с CRM и вернуть ей управленческий смысл.',
        'Читатель получает критерии, по которым CRM помогает сделке, а не имитирует контроль.',
        'CRM полезна, когда управляет следующим действием, риском и доказательством движения.'),
      topic('kasha-topic-value-materials', 'Ценность и материалы продаж',
        'Как упаковывать ценность, ROI, TCO, роли клиента и возражения для сложных продуктов.',
        'Показать связь product marketing и sales enablement.',
        'Читатель понимает, почему one-pager, ТКП и battlecard должны жить в одной логике ценности.',
        'Материалы должны вооружать разговор, а не украшать продукт.')
    ],
    fabulas: [
      fabula('kasha-fabula-field-note', 'Полевая заметка',
        'Живой Telegram-пост из наблюдения о продажах, который выводит управленческий принцип.',
        'От раздражающей сцены к полезной рамке.',
        ['Сцена', 'Что в ней смешного или болезненного', 'Почему так происходит', 'Что делать иначе'],
        ['Авторская память', 'Один практический пример'],
        'compact', 'light', 'manual', [
          'найти: публичные примеры сложных B2B-продаж, где проблема не в продукте, а в процессе сделки',
          'не использовать: мотивационные sales-посты без операционной механики'
        ]),
      fabula('kasha-fabula-framework', 'Рабочая рамка',
        'Короткий фреймворк для диагностики коммерческого контура.',
        'От хаоса сделки к 3-5 проверочным вопросам.',
        ['Проблема', 'Вопросы диагностики', 'Как применить', 'Где не сработает'],
        ['Связь с RevOps или product marketing', 'Ограничение применимости'],
        'standard', 'standard', 'auto'),
      fabula('kasha-fabula-myth', 'Разбор мифа продаж',
        'Разобрать привычный миф продаж и заменить его более точной операционной логикой.',
        'Миф -> почему удобен -> где ломается -> чем заменить.',
        ['Миф', 'Почему в него верят', 'Полевая поломка', 'Новая формула'],
        ['Контрпример', 'Авторская позиция'],
        'standard', 'light', 'auto')
    ],
    radars: [
      radar('kasha-radar-author-memory', 'Память автора: RevOps',
        'Искать повторяющиеся мысли про сложные сделки, CRM, BANT+, материалы и value selling.',
        'Авторские заметки и старые материалы.'),
      radar('kasha-radar-sales-materials', 'Архив коммерческих материалов',
        'Искать reusable-паттерны из sales kits, ТКП-развилок, battlecards и обучения продаж.',
        'Санитизированный архив предыдущей версии блога и презентации команды.')
    ],
    sourceSignals: [
      signal('kasha-signal-complex-sales-box', 'Авторская рамка', 'Когда продукт сложно продать "как коробку"',
        'Санитизированная презентация о поддержке сложных B2B-продаж', 'Сложная продажа проходит через проблему, экономику, ЛПР, процесс, ТКП, закупку и внедрение; простая презентация не покрывает этот путь.',
        'Хороший первый пост для Каши: объяснить, почему коммерциализация сложного продукта начинается с системы продажи.',
        'kasha-topic-complex-sales', 'kasha-fabula-field-note'),
      signal('kasha-signal-five-questions', 'Рабочая рамка', 'Пять вопросов, которые превращают продукт в повторяемые продажи',
        'Санитизированный RevOps архив', 'Клиент, ценность, сделка, материалы и измерение дают карту того, где коммерческая система проседает.',
        'Можно сделать Telegram-фреймворк без сухой презентационности.',
        'kasha-topic-revops-crm', 'kasha-fabula-framework'),
      signal('kasha-signal-loss-to-action', 'Авторская методология', 'Loss-to-Action помогает говорить о ценности без магии ROI',
        'Санитизированное резюме product commercialization', 'Финансовая потеря превращается в управляемый кейс: причина, действие, эффект и владелец.',
        'Связать RevOps, industrial AI и product marketing через язык управляемой потери.',
        'kasha-topic-value-materials', 'kasha-fabula-framework')
    ],
    externalSources: [
      externalSource('kasha-source-revops-resume', 'Product commercialization background', 'document',
        'Sanitized notes from product commercialization and RevOps experience.'),
      externalSource('kasha-source-b2b-sales-deck', 'Complex B2B sales support deck', 'document',
        'Sanitized slides about market, value, sales process, CRM, education and analytics.')
    ],
    defaultPlatform: 'Telegram',
    defaultPublicationSizeProfileId: 'telegram-post',
    postsPerWeek: 3,
    readyScenario: {
      planId: 'kasha-plan-complex-sales',
      title: 'Почему сложный B2B нельзя продать как коробку',
      expectedEffect: 'Показать живой авторский взгляд на RevOps: сложная продажа требует системы, а не очередной красивой презентации.',
      topicId: 'kasha-topic-complex-sales',
      fabulaId: 'kasha-fabula-field-note',
      sourceSignalId: 'kasha-signal-complex-sales-box',
      format: 'Telegram field note'
    }
  },
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
