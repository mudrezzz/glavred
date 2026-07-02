import type {
  AuthorExternalSource,
  AuthorNote,
  EditorialModel,
  EditorialRule,
  Fabula,
  ProjectProfile,
  RadarDefinition,
  SourceSignal,
  Topic
} from '../domain/editorialWorkspace';
import type { PublicationChannel } from '../domain/publication-channels/types';
import { createPublicationChannel } from '../domain/publication-channels/transitions';
import type { DemoBenchmarkProjectId, BenchmarkWorkspaceSeed } from './demoBenchmarkPortfolio';

const projectId: DemoBenchmarkProjectId = 'project-ai-design-patterns';

export const aiDesignPatternsBenchmarkSeed: BenchmarkWorkspaceSeed = {
  projectProfile: {
    name: 'AI Design Patterns',
    description: 'Telegram-first blog about industrial AI design patterns, Decision Intelligence and reliable AI systems.',
    setupStatus: 'needsReview'
  },
  editorialModel: {
    author: 'Практик industrial AI и AI Product Management, который собирает работающие паттерны разработки AI-приложений для промышленности.',
    audience:
      'Руководители промышленной цифровизации, CDO/CIO, product leaders, инженеры ТОиР/EAM, AI architects и B2B-команды, которым нужны надежные AI-системы, а не новости про модели.',
    positioning:
      'Собираем открытую industrial AI pattern book о том, как строить надежные AI-приложения для промышленности: не вокруг модели, а вокруг решений, данных, проверок, ограничений и человека в контуре.',
    fabula:
      'Ценность блога в том, чтобы из разрозненных кейсов, статей, OSS и внутренних практик выделять повторяемые design patterns industrial AI и приглашать сообщество к совместной книге паттернов.',
    rubrics: [
      'Industrial AI patterns',
      'ТОиР и EAM',
      'Decision Intelligence',
      'RAG / Knowledge Graph / HITL',
      'OSS pattern book'
    ],
    styleRules: [
      'Писать по-русски, Telegram-first: энергично, предметно, без академической воды.',
      'Каждый пост должен выводить паттерн, анти-паттерн, критерий или проверяемую гипотезу для industrial AI.',
      'Разделять доказанные практики, сильные гипотезы и спорные места; приглашать к критике и соавторству.',
      'Показывать промышленный контекст: данные, регламенты, роли инженера, надежность, ограничения внедрения.'
    ],
    forbiddenTopics: [
      'Новости моделей без industrial AI вывода',
      'Список инструментов без паттерна применения',
      'Обещания автономного AI без HITL и контроля',
      'Vendor marketing без механизма и ограничений'
    ],
    goals: [
      'Привлекать клиентов через демонстрацию экспертизы в industrial AI application design.',
      'Собрать вокруг блога сообщество, которое помогает формировать открытую книгу AI design patterns.',
      'Сделать блог витриной зрелого подхода: кейс, паттерн, доказательство, ограничение, применение.'
    ]
  },
  authorNotes: [
    note(
      'ai-pattern-industrial-position',
      'thought',
      'Industrial AI надо проектировать вокруг решения, а не вокруг модели',
      'В промышленности AI ценен не потому, что отвечает красиво. Он должен помогать принять решение: собрать данные ТОиР, показать источники, объяснить уверенность, оставить инженера в контуре и не лезть в управление процессом без права.',
      ['industrial-ai', 'decision-intelligence', 'hitl'],
      '2026-07-02T09:00:00.000Z'
    ),
    note(
      'ai-pattern-engineer-augmentation',
      'manualCorrection',
      'Усиление инженера, а не замена инженера',
      'Редакционная позиция: сильный industrial AI не заменяет эксперта, а сокращает ручную сборку решения. Финальное решение остается у человека, спорные случаи уходят на экспертный разбор, качество проверяется на тестовых кейсах.',
      ['engineer-augmentation', 'maintenance', 'safety'],
      '2026-07-02T09:15:00.000Z'
    ),
    note(
      'ai-pattern-hybrid-ai',
      'thought',
      'Hybrid AI как промышленный паттерн',
      'Для ТОиР нужен не один LLM, а связка GenAI, ML/диагностики, правил, регламентов, оптимизации, knowledge graph и human-in-the-loop. Это и есть рабочий контур Decision Intelligence.',
      ['hybrid-ai', 'knowledge-graph', 'rules', 'optimization'],
      '2026-07-02T09:30:00.000Z'
    ),
    note(
      'ai-pattern-pattern-book',
      'thought',
      'Будущая OSS pattern book',
      'Блог должен вести к открытой книге industrial AI patterns: как GoF/POSA/Fowler, но для AI-приложений в промышленности. Не догма, а живая crowd-книга с критикой, pull requests и разбором спорных паттернов.',
      ['oss', 'pattern-book', 'community'],
      '2026-07-02T09:45:00.000Z'
    ),
    note(
      'ai-pattern-author-channel',
      'linkReaction',
      'Авторская валидация через AI Product Management канал',
      'Предыдущий авторский канал полезен как материал, прошедший редакторскую валидацию автора. Его нельзя копировать как шаблон постов, но можно учитывать позицию: AI полезен через продуктовую механику, ограничения и реальные workflow.',
      ['author-validation', 'ai-product-management', 'voice'],
      '2026-07-02T10:00:00.000Z',
      'https://t.me/ai_product_mgmt'
    )
  ],
  editorialRules: [
    rule(
      'ai-pattern-rule-industrial-scope',
      'positioning',
      'AI для промышленности, не AI вообще',
      'Каждый материал должен объяснять industrial AI контекст: ТОиР, EAM, диагностика, производственные данные, регламенты, риски, роли или экономику внедрения.'
    ),
    rule(
      'ai-pattern-rule-pattern-output',
      'author',
      'Пост должен давать reusable pattern',
      'Не публиковать новость ради новости. На выходе нужен паттерн, анти-паттерн, критерий внедрения, схема архитектуры или повод для RFC.'
    ),
    rule(
      'ai-pattern-rule-industrial-audience',
      'audience',
      'Писать для команд, которые внедряют промышленный AI',
      'Основная аудитория: CDO/CIO, product leaders, инженеры ТОиР/EAM, AI architects и B2B-команды, которым нужны надежные AI-системы для промышленного контура, а не общий AI-шум.'
    ),
    rule(
      'ai-pattern-rule-client-attraction-goal',
      'goal',
      'Привлекать клиентов через видимую экспертизу',
      'Каждый материал должен показывать зрелый подход к industrial AI application design: кейс, паттерн, ограничения, архитектурный вывод и практическую применимость для клиента.'
    ),
    rule(
      'ai-pattern-rule-proof-limits',
      'positioning',
      'Доказательства плюс ограничения',
      'Сильные claims требуют источника, кейса, benchmark, OSS-примера или честной пометки, что это гипотеза автора.'
    ),
    rule(
      'ai-pattern-rule-community',
      'styleVoice',
      'Приглашение к соавторству',
      'Тон не догматический: приветствуются критика, спор, уточнения и будущие pull requests в pattern book.'
    )
  ],
  topics: [
    topic(
      'ai-pattern-topic-decision-intelligence',
      'Decision Intelligence для ТОиР',
      'Как AI помогает инженеру ТОиР собрать данные, объяснить событие, найти похожие случаи, построить RCA и выбрать действие.',
      'Показать AI как рабочее место принятия решения, а не чат-бот вокруг документов.',
      'Читатель видит, где industrial AI дает ценность: меньше ручной сборки, лучше трассируемость, быстрее экспертная проверка.',
      'Промышленный AI начинается с решения, источников и ответственности человека.'
    ),
    topic(
      'ai-pattern-topic-hybrid-ai',
      'Hybrid AI architecture',
      'Паттерны связки LLM, ML/диагностики, правил, регламентов, knowledge graph, оптимизации и HITL.',
      'Снять иллюзию, что промышленную задачу можно решить одной моделью или одним агентом.',
      'Читатель получает архитектурную рамку для надежного industrial AI контура.',
      'Надежность в промышленности возникает из гибридной архитектуры, а не из размера модели.'
    ),
    topic(
      'ai-pattern-topic-industrial-cases',
      'Живые кейсы industrial AI',
      'Небанальные применения AI в промышленности: паспортизация оборудования, классификаторы, качество данных, похожие отказы, планирование, RCA, training simulators.',
      'Отбирать кейсы, где виден механизм, данные, роль пользователя и ограничение.',
      'Читатель получает идеи для пилотов и критерии, по которым отличать рабочий кейс от демо.',
      'Кейс интересен только тогда, когда понятно, какие данные он использует и какое решение улучшает.'
    ),
    topic(
      'ai-pattern-topic-pattern-book',
      'OSS pattern book',
      'Методика сбора, именования и обсуждения industrial AI design patterns как открытой книги.',
      'Постепенно переводить блог из авторского монолога в community-driven pattern catalog.',
      'Читатель понимает, как предложить паттерн, раскритиковать существующий или принести пример.',
      'Industrial AI patterns должны становиться общим языком практиков, а не личной коллекцией автора.'
    )
  ],
  fabulas: [
    fabula(
      'ai-pattern-fabula-pattern-card',
      'Карточка паттерна',
      'Разбор одного industrial AI паттерна: проблема, механизм, пример, ограничения, где применять.',
      'От промышленной боли к named pattern и практическому критерию применения.',
      ['Ситуация', 'Паттерн', 'Механизм', 'Пример или источник', 'Где работает', 'Где ломается', 'Что берем на вооружение'],
      ['Минимум один источник/пример', 'Ограничение или failure mode', 'Промышленный контекст'],
      'standard',
      'deep',
      'manual',
      [
        'найти: industrial AI case, OSS/project, paper или engineering write-up с конкретным механизмом',
        'проверить: есть ли данные, роль пользователя, метрика или ограничение',
        'не использовать: vendor announcement без архитектуры или результата'
      ]
    ),
    fabula(
      'ai-pattern-fabula-case-breakdown',
      'Разбор industrial AI кейса',
      'Живой разбор промышленного AI применения без банальности: что было, как работало, почему интересно.',
      'От кейса к повторяемому design pattern или anti-pattern.',
      ['Кейс', 'Данные и роли', 'AI-механизм', 'Что изменилось', 'Ограничения', 'Паттерн для книги'],
      ['Публичный источник или sanitized internal material', 'Ясная граница применения'],
      'standard',
      'marketResearch',
      'manual',
      [
        'искать: ТОиР, EAM, predictive maintenance, industrial knowledge graph, diagnostics assistant',
        'добавлять: что именно может повторить другая команда'
      ]
    ),
    fabula(
      'ai-pattern-fabula-paper-benchmark',
      'Paper / benchmark review',
      'Разбор статьи, arXiv, benchmark или technical report через вопрос: какой паттерн можно взять в industrial AI practice.',
      'От research artifact к практическому паттерну и проверяемой гипотезе.',
      ['Что проверяли', 'Почему это важно для промышленности', 'Цифры/доказательства', 'Ограничения', 'Что берем на вооружение'],
      ['Ссылка на paper/report', 'Цифры или результат', 'Ограничение переносимости'],
      'deep',
      'deep',
      'manual',
      [
        'не делать model leaderboard',
        'искать benchmark, который говорит о применении паттерна, а не просто о сравнении моделей'
      ]
    ),
    fabula(
      'ai-pattern-fabula-digest',
      'Ежемесячный digest pattern book',
      'Большой обновляемый дайджест найденных паттернов, кейсов, OSS и спорных вопросов.',
      'От разрозненных сигналов месяца к обновлению открытой книги паттернов.',
      ['Что добавили', 'Что подтвердилось', 'Что спорно', 'Что просим у сообщества', 'Планы на следующий месяц'],
      ['Несколько источников', 'Явная сортировка confirmed / hypothesis / disputed'],
      'deep',
      'marketResearch',
      'manual',
      [
        'собрать: свежие industrial AI cases, OSS, papers, статьи практиков',
        'разделить: confirmed patterns, candidate patterns, anti-patterns'
      ]
    ),
    fabula(
      'ai-pattern-fabula-oss-teardown',
      'OSS / framework teardown',
      'Разбор OSS-проекта или framework: что в нем реально полезно для industrial AI и какой паттерн он воплощает.',
      'От репозитория к применимости в промышленном контуре.',
      ['Что это', 'Какой паттерн воплощает', 'Что можно взять', 'Риски внедрения', 'Где применить'],
      ['GitHub/project link', 'Ограничение production readiness'],
      'standard',
      'deep',
      'manual',
      ['искать GitHub/OSS, где виден не только demo, но и архитектурная механика']
    )
  ],
  radars: [
    radar(
      'ai-pattern-radar-industrial-cases',
      'Industrial AI cases',
      'Искать практические кейсы industrial AI, где есть данные, роли пользователя, ограничения и результат.',
      'Public industrial AI cases, ТОиР/EAM materials, engineering blogs, vendor technical notes with enough detail.'
    ),
    radar(
      'ai-pattern-radar-papers',
      'Papers and benchmarks',
      'Искать papers/reports не про лидерборды моделей, а про применимость паттернов, фреймворков и архитектур.',
      'arXiv, ACM/IEEE-style reports, benchmark papers, technical reports.'
    ),
    radar(
      'ai-pattern-radar-oss',
      'OSS industrial AI patterns',
      'Искать OSS/frameworks, которые можно разобрать как практический паттерн для industrial AI.',
      'GitHub projects, docs, technical blogs, community examples.'
    ),
    radar(
      'ai-pattern-radar-author-materials',
      'Sanitized author materials',
      'Извлекать паттерны из авторских материалов про прикладной ИИ, ТОиР, Decision Intelligence и AI Product Management.',
      'User-provided sanitized docs and author-validated Telegram materials.'
    )
  ],
  sourceSignals: [
    signal(
      'ai-pattern-signal-decision-workbench',
      'Pattern candidate',
      'Maintenance Decision Intelligence Workbench как industrial AI pattern',
      'Sanitized ТОиР / Ctrl2GO Solutions material',
      'В ТОиР данные уже есть в диагностике, паспортах, регламентах, RCA, нарядах, дефектах и запчастях, но решение часто собирается вручную. Паттерн: AI workbench собирает источники, показывает уверенность и оставляет инженера финальным владельцем решения.',
      'Первый пост должен объяснить Decision Intelligence Workbench как industrial AI паттерн: GenAI + диагностика + правила + knowledge graph + HITL.',
      'ai-pattern-topic-decision-intelligence',
      'ai-pattern-fabula-pattern-card'
    ),
    signal(
      'ai-pattern-signal-hybrid-ai',
      'Architecture pattern',
      'Hybrid AI вместо одного LLM',
      'Sanitized ТОиР / Ctrl2GO Solutions material',
      'Промышленный контур требует гибридной архитектуры: GenAI для объяснения, ML/диагностика для сигналов, правила и регламенты для допустимости, оптимизация для выбора, knowledge graph для связей, HITL для ответственности.',
      'Хороший архитектурный пост: почему industrial AI нельзя строить как один чат с моделью.',
      'ai-pattern-topic-hybrid-ai',
      'ai-pattern-fabula-pattern-card'
    ),
    signal(
      'ai-pattern-signal-industrial-cases',
      'Case map',
      '10 прикладных industrial AI кейсов для ТОиР',
      'Sanitized ТОиР / Ctrl2GO Solutions material',
      'Паспортизация оборудования, классификаторы, контроль качества данных, поиск похожих отказов, интерпретация диагностических событий, AI-планировщик, RCA assistant, обследование перед EAM, анализ встреч и training simulator дают карту паттернов, а не список фич.',
      'Можно сделать вводный Telegram-пост: какие кейсы не банальны и почему каждый тянет на отдельный паттерн.',
      'ai-pattern-topic-industrial-cases',
      'ai-pattern-fabula-case-breakdown'
    ),
    signal(
      'ai-pattern-signal-pattern-book',
      'Community thesis',
      'Industrial AI нуждается в своей pattern book',
      'Author concept and public software-pattern tradition',
      'Как GoF, POSA и Fowler собирали язык проектирования для software architecture, industrial AI нуждается в живой книге паттернов: карточки, критика, примеры, disputed sections, community pull requests.',
      'Пост-приглашение к сообществу: не очередной канал про AI, а попытка собрать общий язык практиков.',
      'ai-pattern-topic-pattern-book',
      'ai-pattern-fabula-digest'
    )
  ],
  externalSources: [
    externalSource(
      'ai-pattern-source-ctrl2go-tor',
      'Sanitized ТОиР / Ctrl2GO Solutions material',
      'document',
      'Private user-provided material paraphrased into public-safe fixture notes about applied AI for ТОиР and Maintenance Decision Intelligence.'
    ),
    externalSource(
      'ai-pattern-source-author-channel',
      'Author-validated AI Product Management channel',
      'blogSite',
      'Public Telegram channel used as author-position reference, not as post template: https://t.me/ai_product_mgmt'
    ),
    externalSource(
      'ai-pattern-source-pattern-tradition',
      'Software design pattern tradition',
      'manualUpload',
      'Public-safe editorial reference to GoF, POSA and Fowler as inspiration for a community pattern book.'
    ),
    externalSource(
      'ai-pattern-source-public-research',
      'Public industrial AI research and OSS queue',
      'blogSite',
      'Future reviewed queue for arXiv papers, GitHub projects, industrial AI cases and benchmark reports.'
    )
  ],
  defaultPlatform: 'Telegram',
  defaultPublicationSizeProfileId: 'telegram-post',
  postsPerWeek: 2,
  readyScenario: {
    planId: 'ai-patterns-plan-decision-workbench',
    title: 'Decision Intelligence Workbench: первый industrial AI pattern',
    expectedEffect:
      'Написать русский Telegram-пост, который показывает паттерн Maintenance Decision Intelligence Workbench: зачем он нужен ТОиР, как устроен гибридный AI-контур и почему человек остается в контуре.',
    topicId: 'ai-pattern-topic-decision-intelligence',
    fabulaId: 'ai-pattern-fabula-pattern-card',
    sourceSignalId: 'ai-pattern-signal-decision-workbench',
    format: 'Telegram pattern card'
  }
};

export function createAiDesignPatternsPublicationChannels(): PublicationChannel[] {
  return [
    createPublicationChannel({
      id: 'channel-ai-telegram',
      projectId,
      platform: 'telegram',
      title: 'Telegram',
      handleOrUrl: '@industrial_ai_patterns',
      language: 'ru',
      role: 'primary',
      defaultPublicationSizeProfileId: 'telegram-post'
    }),
    createPublicationChannel({
      id: 'channel-ai-github-pattern-book',
      projectId,
      platform: 'site',
      title: 'GitHub pattern book',
      handleOrUrl: 'https://github.com/industrial-ai-patterns',
      language: 'ru',
      role: 'experiment',
      publishingMode: 'adapterPlanned',
      status: 'paused',
      defaultPublicationSizeProfileId: 'linkedin-article'
    })
  ];
}

function note(
  id: string,
  type: AuthorNote['type'],
  title: string,
  body: string,
  tags: string[],
  capturedAt: string,
  sourceUrl = ''
): AuthorNote {
  return { id, type, title, body, sourceUrl, tags, attachments: [], capturedAt };
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
    rules: ['Начинать с industrial AI ситуации', 'Выводить reusable pattern', 'Показывать ограничение и критерий применения'],
    forbiddenAngles: ['generic AI advice', 'model-first hype', 'vendor retelling without mechanism'],
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
    rules: ['Не терять промышленный контекст', 'Не подменять вывод списком источников', 'Отделять факт от авторской гипотезы'],
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
    sourceType: id.includes('author') ? 'authorMemory' : 'externalSource',
    scope,
    rules: [{ id: `${id}-rule`, operator: 'and', negate: false, statement: ruleStatement, status: 'active' }],
    sources: [
      {
        id: `${id}-source`,
        type: id.includes('author') ? 'manualSource' : 'openWeb',
        title: `${title} source`,
        value: scope,
        notes: 'Sanitized benchmark seed; private source documents are not committed.',
        status: 'active'
      }
    ],
    filters: [
      {
        id: `${id}-filter-industrial`,
        dimension: 'topics',
        enabled: true,
        mode: 'mustMatch',
        instruction: 'Signal must be useful for industrial AI patterns, ТОиР/EAM, Decision Intelligence, hybrid AI, or pattern-book discussion.'
      }
    ],
    sourceDiscoveryMode: 'specifiedAndAdditional',
    acceptancePolicy: 'manual',
    triggerMode: 'deficitDriven',
    status: 'active',
    lastRunAt: '2026-07-02T10:00:00.000Z',
    notes: 'Benchmark radar for AI Design Patterns rework.'
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
    capturedAt: '2026-07-02',
    summary,
    rawNote,
    radarId: 'ai-pattern-radar-author-materials',
    reviewStatus: 'new',
    suggestedTopicId: topicId,
    suggestedFabulaId: fabulaId,
    suggestedValue: rawNote,
    duplicateRisk: 'low',
    searchNote: 'Sanitized benchmark signal from user-provided materials and project concept discussion.'
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
    lastCheckedAt: '2026-07-02',
    lastImportedAt: '',
    notes
  };
}
