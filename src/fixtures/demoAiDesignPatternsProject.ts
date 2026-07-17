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
    name: 'Опытный цех «Сборочная»',
    description: 'Telegram-first workshop for industrial AI patterns: cases, test protocols, hybrid contours and reliable decision support.',
    setupStatus: 'needsReview'
  },
  editorialModel: {
    author:
      'Практик industrial AI product design и прикладной AI-архитектуры, который пишет как руководитель опытного цеха: берет кейсы, документы, OSS и research на испытательный стенд, ищет слабые сборки и выводит пригодные паттерны.',
    audience:
      'Руководители промышленной цифровизации, CDO/CIO/CTO, product leaders, инженеры ТОиР/EAM, AI architects и B2B-команды, которым нужны надежные industrial AI-системы, а не демонстрации моделей.',
    positioning:
      'Опытный цех, где industrial AI идеи проходят через стенд: решение, данные, роли, ограничения, надежность, HITL и критерии применения. На выходе не новость, а паттерн, анти-паттерн, протокол или RFC для будущей pattern book.',
    fabula:
      'Ценность блога в том, чтобы из разрозненных кейсов, статей, OSS и авторских материалов собирать проверяемые industrial AI patterns и приглашать сообщество к совместной инженерной книге.',
    rubrics: [
      'Промышленные артефакты',
      'Контуры надежности',
      'Гибридная сборка',
      'Данные как сырье',
      'Полигон внедрения',
      'Открытый каталог паттернов',
      'ТОиР и EAM',
      'Decision Intelligence'
    ],
    styleRules: [
      'Писать по-русски, Telegram-first: живо, предметно, с ощущением цеха и испытательного стенда, но без натянутой метафоры в каждом абзаце.',
      'Публичный артефакт выпуска: паттерн, анти-паттерн, протокол испытаний, критерий внедрения, архитектурная граница или RFC-вопрос.',
      'Разделять доказанные практики, сильные гипотезы и спорные места; приглашать к критике и соавторству.',
      'Сильные claims должны иметь источник, кейс, benchmark, OSS-пример или честную пометку авторской гипотезы.'
    ],
    forbiddenTopics: [
      'Новости моделей без industrial AI вывода',
      'Список инструментов без паттерна применения',
      'Обещания автономного AI без HITL и контроля',
      'Vendor marketing без механизма и ограничений',
      'Мистический флер вокруг AI вместо инженерного разбора'
    ],
    goals: [
      'Привлекать клиентов через демонстрацию зрелой экспертизы в industrial AI application design.',
      'Собрать вокруг блога сообщество, которое помогает формировать открытую книгу industrial AI patterns.',
      'Показывать, как industrial AI собирается из решения, данных, ролей, надежности, ограничений и ответственности человека.',
      'Создать отличимый авторский проект: не AI-новости, а опытный цех прикладных паттернов.'
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
      'Будущая OSS pattern book как журнал цеха',
      'Блог должен вести к открытой книге industrial AI patterns: как GoF/POSA/Fowler, но для AI-приложений в промышленности. Не догма, а живая crowd-книга с критикой, pull requests, протоколами испытаний и разбором спорных паттернов.',
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
    ),
    note(
      'ai-pattern-workshop-identity',
      'thought',
      'Опытный цех вместо сухого каталога',
      'Авторская рамка: мы не называем AI магией и не пишем каталог ради каталога. Мы берем industrial AI артефакт на стенд, проверяем сборку, называем паттерн, показываем допуски и зовем практиков спорить по делу.',
      ['workshop', 'voice', 'pattern-book'],
      '2026-07-02T10:15:00.000Z'
    )
  ],
  editorialRules: [
    rule(
      'ai-pattern-rule-author-workshop-lead',
      'author',
      'Автор как руководитель опытного цеха',
      'Писать с позиции практика industrial AI product design: разбирать сборку решения, данные, роли, надежность и ограничения, а не пересказывать новости AI.'
    ),
    rule(
      'ai-pattern-rule-industrial-audience',
      'audience',
      'Писать для команд, которые внедряют промышленный AI',
      'Основная аудитория: CDO/CIO/CTO, product leaders, инженеры ТОиР/EAM, AI architects и B2B-команды, которым нужны надежные industrial AI-системы, а не общий AI-шум.'
    ),
    rule(
      'ai-pattern-rule-client-attraction-goal',
      'goal',
      'Привлекать клиентов через видимую экспертизу',
      'Каждый материал должен показывать зрелый подход к industrial AI application design: кейс, паттерн, ограничения, архитектурный вывод и практическую применимость для клиента.'
    ),
    rule(
      'ai-pattern-rule-pattern-book-goal',
      'goal',
      'Собирать открытую книгу промышленных AI-паттернов',
      'Посты должны постепенно складываться в community pattern book: проверенные паттерны, спорные гипотезы, анти-паттерны, протоколы испытаний и RFC-вопросы.'
    ),
    rule(
      'ai-pattern-rule-industrial-scope',
      'positioning',
      'Industrial AI workshop, не AI вообще',
      'Материал должен объяснять промышленный контекст: ТОиР, EAM, диагностика, производственные данные, регламенты, риски, роли, экономику внедрения или reliability contour.'
    ),
    rule(
      'ai-pattern-rule-pattern-output',
      'styleVoice',
      'Пост должен давать рабочий артефакт',
      'Не публиковать новость ради новости. На выходе нужен паттерн, анти-паттерн, критерий внедрения, схема архитектуры или повод для RFC.'
    ),
    rule(
      'ai-pattern-rule-proof-limits',
      'styleLanguage',
      'Доказательства плюс ограничения',
      'Сильные claims требуют источника, кейса, benchmark, OSS-примера или честной пометки, что это гипотеза автора.'
    ),
    rule(
      'ai-pattern-rule-community',
      'styleVoice',
      'Приглашение к соавторству',
      'Тон не догматический: приветствуются критика, спор, уточнения и будущие pull requests в pattern book.'
    ),
    rule(
      'ai-pattern-rule-no-mystic-frame',
      'positioning',
      'Не продавать AI как магию',
      'Публичная рамка проекта - цех, сборка, стенд и проверка. Избегать мистического флера: AI интересен как инженерная сборка, а не как непостижимое чудо.'
    )
  ],
  topics: [
    topic(
      'ai-pattern-topic-industrial-artifacts',
      'Промышленные артефакты',
      'Кейсы и объекты промышленного контура: ТОиР, EAM, диагностика, паспорта оборудования, наряды, дефекты, запчасти, RCA и события обслуживания.',
      'Показывать industrial AI через реальные артефакты, а не через абстрактные возможности модели.',
      'Читатель видит, из каких данных и ролей собирается рабочий AI-контур.',
      'Ценность industrial AI начинается с понятного объекта, решения и владельца ответственности.'
    ),
    topic(
      'ai-pattern-topic-reliability-contours',
      'Контуры надежности',
      'Валидация, fallback, трассировка, evidence, HITL, safety boundaries и ответственность в industrial AI.',
      'Показывать, почему надежность рождается из контроля, а не из размера модели.',
      'Читатель получает критерии, по которым можно отличить production-контур от красивого демо.',
      'Без надежности и ответственности industrial AI остается демонстрацией, а не системой.'
    ),
    topic(
      'ai-pattern-topic-hybrid-assembly',
      'Гибридная сборка',
      'Связка LLM, ML/диагностики, правил, регламентов, knowledge graph, оптимизации, инструментов и workflow.',
      'Снимать иллюзию, что промышленную задачу можно решить одной моделью или одним агентом.',
      'Читатель получает архитектурную рамку для сборки промышленного AI-контура.',
      'Сильный industrial AI - это сборка, где каждый компонент имеет роль и допуск.'
    ),
    topic(
      'ai-pattern-topic-data-raw-material',
      'Данные как сырье',
      'Классификаторы, журналы событий, документы, регламенты, коды дефектов, иерархия оборудования, качество данных и provenance.',
      'Показывать, что industrial AI собирается из сырья разного качества, а не из чистого prompt engineering.',
      'Читатель понимает, какие данные нужны, где они ломаются и как это влияет на паттерн.',
      'Плохое сырье нельзя спрятать за красивым интерфейсом.'
    ),
    topic(
      'ai-pattern-topic-implementation-field',
      'Полигон внедрения',
      'Пилоты, экономика, adoption, роли, операционные изменения, интеграции с EAM/ERP/CRM и критерии успеха.',
      'Проверять industrial AI паттерны на внедряемость, а не только на техническую красоту.',
      'Читатель получает рамку для пилота, оценки эффекта и разговора с бизнесом.',
      'Паттерн становится ценным только после проверки на реальном контуре внедрения.'
    ),
    topic(
      'ai-pattern-topic-open-catalog',
      'Открытый каталог паттернов',
      'Именование, спор, RFC, примеры, анти-паттерны, digest updates и будущая OSS/community pattern book.',
      'Переводить блог из авторской витрины в живой каталог, который можно критиковать и дополнять.',
      'Читатель понимает, как принести пример, оспорить паттерн или предложить улучшение.',
      'Industrial AI patterns должны становиться общим языком практиков, а не личной коллекцией автора.'
    )
  ],
  fabulas: [
    fabula(
      'ai-pattern-fabula-pattern-card',
      'Карточка паттерна',
      'Разбор одного industrial AI паттерна: recurring problem, механизм, пример, ограничения и критерий применения.',
      'От промышленной ситуации к named pattern и практическому критерию применения.',
      ['Ситуация', 'Повторяемая проблема', 'Паттерн', 'Механизм', 'Пример или источник', 'Где работает', 'Где ломается', 'Что берем на вооружение'],
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
      'ai-pattern-fabula-test-protocol',
      'Протокол испытаний',
      'Проверка claim, инструмента, подхода или архитектурной сборки на стенде: условия, поведение, failure modes, допуск.',
      'От обещания к проверке на применимость в промышленном контуре.',
      ['Что заявлено', 'Стенд и условия', 'Что наблюдаем', 'Где ломается', 'Допустимое применение', 'Решение цеха'],
      ['Источник claim/tool', 'Условия проверки', 'Failure mode или ограничение'],
      'standard',
      'deep',
      'manual',
      [
        'искать: case, tool, OSS, paper или industrial AI claim, который можно проверить как сборку',
        'добавлять: условия допустимости и что нельзя обещать'
      ]
    ),
    fabula(
      'ai-pattern-fabula-artifact-teardown',
      'Разбор артефакта',
      'Разбор кейса, paper, OSS-репозитория или продукта как воплощенного industrial AI паттерна.',
      'От внешнего артефакта к тому, что можно забрать в свою сборку.',
      ['Что это', 'Какой паттерн воплощает', 'Что можно взять', 'Риски внедрения', 'Где применить', 'Что спорно'],
      ['Ссылка на artifact', 'Промышленная переносимость', 'Ограничение production readiness'],
      'deep',
      'deep',
      'manual',
      [
        'не делать tool announcement',
        'искать embodied pattern, а не просто список features'
      ]
    ),
    fabula(
      'ai-pattern-fabula-field-note',
      'Полевой отчет из цеха',
      'Живая industrial AI сцена, из которой выводится принцип и практический ход.',
      'От наблюдения к принципу и следующему действию.',
      ['Сцена', 'Наблюдение', 'Почему важно', 'Принцип', 'Практический ход'],
      ['Конкретная сцена или sanitized material', 'Практический вывод'],
      'standard',
      'standard',
      'manual',
      [
        'не превращать сцену в байку без вывода',
        'держать промышленный контекст и роль пользователя'
      ]
    ),
    fabula(
      'ai-pattern-fabula-anti-pattern',
      'Анти-паттерн',
      'Разбор соблазнительного, но опасного industrial AI хода: почему выглядит разумно, где ломается, чем заменить.',
      'От красивого shortcut к безопасной инженерной сборке.',
      ['Соблазнительный ход', 'Почему кажется разумным', 'Как ломается в промышленности', 'Более безопасная сборка', 'Проверка перед использованием'],
      ['Failure mode', 'Контрпример или ограничение', 'Альтернативная сборка'],
      'standard',
      'deep',
      'manual',
      ['искать: AI shortcuts, model-first решения, vendor claims или внутренние риски внедрения']
    ),
    fabula(
      'ai-pattern-fabula-test-journal',
      'Журнал испытаний',
      'Периодический digest цеха: подтвержденные паттерны, candidate patterns, спорные места, anti-patterns, source queue и вопросы к сообществу.',
      'От разрозненных сигналов месяца к обновлению открытого каталога паттернов.',
      ['Что подтвердили', 'Что стало candidate pattern', 'Что спорно', 'Какие anti-patterns нашли', 'Что просим у сообщества', 'Следующая партия испытаний'],
      ['Несколько источников', 'Явная сортировка confirmed / hypothesis / disputed'],
      'deep',
      'marketResearch',
      'manual',
      [
        'собрать: свежие industrial AI cases, OSS, papers, статьи практиков',
        'разделить: confirmed patterns, candidate patterns, anti-patterns, RFC'
      ]
    )
  ],
  topicFabulaCompatibility: [
    compatibility('ai-pattern-topic-industrial-artifacts', 'ai-pattern-fabula-pattern-card'),
    compatibility('ai-pattern-topic-industrial-artifacts', 'ai-pattern-fabula-test-protocol'),
    compatibility('ai-pattern-topic-industrial-artifacts', 'ai-pattern-fabula-field-note'),
    compatibility('ai-pattern-topic-reliability-contours', 'ai-pattern-fabula-pattern-card'),
    compatibility('ai-pattern-topic-reliability-contours', 'ai-pattern-fabula-test-protocol'),
    compatibility('ai-pattern-topic-reliability-contours', 'ai-pattern-fabula-anti-pattern'),
    compatibility('ai-pattern-topic-hybrid-assembly', 'ai-pattern-fabula-pattern-card'),
    compatibility('ai-pattern-topic-hybrid-assembly', 'ai-pattern-fabula-artifact-teardown'),
    compatibility('ai-pattern-topic-hybrid-assembly', 'ai-pattern-fabula-anti-pattern'),
    compatibility('ai-pattern-topic-data-raw-material', 'ai-pattern-fabula-pattern-card'),
    compatibility('ai-pattern-topic-data-raw-material', 'ai-pattern-fabula-field-note'),
    compatibility('ai-pattern-topic-data-raw-material', 'ai-pattern-fabula-anti-pattern'),
    compatibility('ai-pattern-topic-implementation-field', 'ai-pattern-fabula-test-protocol'),
    compatibility('ai-pattern-topic-implementation-field', 'ai-pattern-fabula-field-note'),
    compatibility('ai-pattern-topic-implementation-field', 'ai-pattern-fabula-anti-pattern'),
    compatibility('ai-pattern-topic-open-catalog', 'ai-pattern-fabula-pattern-card'),
    compatibility('ai-pattern-topic-open-catalog', 'ai-pattern-fabula-artifact-teardown'),
    compatibility('ai-pattern-topic-open-catalog', 'ai-pattern-fabula-test-journal')
  ],
  radars: [
    radar(
      'ai-pattern-radar-industrial-cases',
      'Промышленные AI-кейсы',
      'Искать практические кейсы industrial AI, где есть данные, роли пользователя, ограничения и результат.',
      'Публичные кейсы industrial AI, материалы по ТОиР/EAM, инженерные блоги и технические заметки вендоров с достаточной детализацией.'
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
      'Maintenance Decision Intelligence Workbench как артефакт для стенда',
      'Sanitized ТОиР / Ctrl2GO Solutions material',
      'В ТОиР данные уже есть в диагностике, паспортах, регламентах, RCA, нарядах, дефектах и запчастях, но решение часто собирается вручную. Паттерн: AI workbench собирает источники, показывает уверенность и оставляет инженера финальным владельцем решения.',
      'Первый пост должен поставить Decision Intelligence Workbench на стенд: что собирается, где допуск, где ломается, почему человек остается в контуре.',
      'ai-pattern-topic-industrial-artifacts',
      'ai-pattern-fabula-pattern-card'
    ),
    signal(
      'ai-pattern-signal-hybrid-ai',
      'Architecture pattern',
      'Hybrid AI вместо одного LLM',
      'Sanitized ТОиР / Ctrl2GO Solutions material',
      'Промышленный контур требует гибридной архитектуры: GenAI для объяснения, ML/диагностика для сигналов, правила и регламенты для допустимости, оптимизация для выбора, knowledge graph для связей, HITL для ответственности.',
      'Хороший архитектурный пост: почему industrial AI нельзя строить как один чат с моделью.',
      'ai-pattern-topic-hybrid-assembly',
      'ai-pattern-fabula-pattern-card'
    ),
    signal(
      'ai-pattern-signal-industrial-cases',
      'Case map',
      '10 прикладных industrial AI кейсов для ТОиР',
      'Sanitized ТОиР / Ctrl2GO Solutions material',
      'Паспортизация оборудования, классификаторы, контроль качества данных, поиск похожих отказов, интерпретация диагностических событий, AI-планировщик, RCA assistant, обследование перед EAM, анализ встреч и training simulator дают карту паттернов, а не список фич.',
      'Можно сделать вводный Telegram-пост: какие кейсы не банальны и почему каждый тянет на отдельный паттерн.',
      'ai-pattern-topic-industrial-artifacts',
      'ai-pattern-fabula-field-note'
    ),
    signal(
      'ai-pattern-signal-pattern-book',
      'Community thesis',
      'Industrial AI нуждается в своей pattern book',
      'Author concept and public software-pattern tradition',
      'Как GoF, POSA и Fowler собирали язык проектирования для software architecture, industrial AI нуждается в живой книге паттернов: карточки, критика, примеры, disputed sections, community pull requests.',
      'Пост-приглашение к сообществу: не очередной канал про AI, а попытка вести журнал цеха и собрать общий язык практиков.',
      'ai-pattern-topic-open-catalog',
      'ai-pattern-fabula-test-journal'
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
    title: 'Decision Intelligence Workbench: первая сборка на стенде',
    expectedEffect:
      'Написать русский Telegram-пост, который показывает Maintenance Decision Intelligence Workbench как промышленный AI-паттерн: зачем он нужен ТОиР, как устроена сборка и где ее допуски.',
    topicId: 'ai-pattern-topic-industrial-artifacts',
    fabulaId: 'ai-pattern-fabula-pattern-card',
    sourceSignalId: 'ai-pattern-signal-decision-workbench',
    format: 'Telegram workshop pattern card'
  }
};

export function createAiDesignPatternsPublicationChannels(): PublicationChannel[] {
  return [
    createPublicationChannel({
      id: 'channel-ai-telegram',
      projectId,
      platform: 'telegram',
      title: 'Telegram',
      handleOrUrl: '@sborochnaya_ai',
      language: 'ru',
      role: 'primary',
      defaultPublicationSizeProfileId: 'telegram-post'
    }),
    createPublicationChannel({
      id: 'channel-ai-github-pattern-book',
      projectId,
      platform: 'site',
      title: 'GitHub pattern book',
      handleOrUrl: 'https://github.com/sborochnaya-industrial-ai',
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

function compatibility(topicId: string, fabulaId: string): { topicId: string; fabulaId: string } {
  return { topicId, fabulaId };
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
        title: `Источники: ${title}`,
        value: scope,
        notes: 'Безопасная настройка демонстрационного радара; приватные документы источников не хранятся в репозитории.',
        status: 'active'
      }
    ],
    filters: [
      {
        id: `${id}-filter-industrial`,
        dimension: 'topics',
        enabled: true,
        mode: 'mustMatch',
        instruction: 'Сигнал должен быть полезен для разбора паттернов industrial AI, ТОиР/EAM, Decision Intelligence, гибридного AI или открытой книги паттернов.'
      }
    ],
    sourceDiscoveryMode: 'specifiedAndAdditional',
    sourceLanguagePolicy: 'editorialAndEnglish',
    acceptancePolicy: 'manual',
    triggerMode: 'deficitDriven',
    status: 'active',
    lastRunAt: '2026-07-02T10:00:00.000Z',
    notes: 'Контрольный радар для мастерской промышленных AI-паттернов «Сборочная».'
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
