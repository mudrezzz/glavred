import { createAuthorMemoryEvent, createBroadcastPlan, inferAuthorPositionAssertions } from '../application/editorialServices';
import {
  createDefaultRadarEditorialFilters,
  createDefaultTopicFabulaMatrix,
  evaluateSignalAgainstRadarFilters
} from '../domain/editorialWorkspace';
import type {
  ArchiveRecord,
  AuthorExternalSource,
  AuthorNote,
  EditorialRule,
  Fabula,
  ImportedMemoryCandidate,
  ProjectProfile,
  RadarDefinition,
  SourceSignal,
  Topic,
  WorkspaceState
} from '../domain/editorialWorkspace';

const demoProjectProfile: ProjectProfile = {
  name: 'TG-блог AI Product Manager',
  description: 'Исследовательский блог о построении AI-B2B продуктов',
  setupStatus: 'needsReview'
};

const demoEditorialRules: EditorialRule[] = [
  {
    id: 'rule-author-researcher',
    group: 'author',
    title: 'AI Product Manager с исследовательской оптикой',
    statement: 'Автор говорит как практик, который исследует workflow, adoption, доверие и экономику внедрения AI-B2B продуктов.',
    status: 'active',
    evidenceNoteId: 'note-workflow-risk'
  },
  {
    id: 'rule-author-no-evangelism',
    group: 'author',
    title: 'Не AI-евангелист',
    statement: 'Автор не продает магию модели, а показывает ограничения, failure modes и условия надежного rollout.',
    status: 'active',
    evidenceNoteId: 'note-demo-magic-fails'
  },
  {
    id: 'rule-audience-builders',
    group: 'audience',
    title: 'Строители AI-B2B продуктов',
    statement: 'Писать для AI PM, founders, CPO/product leaders и B2B SaaS команд, которым нужно довести AI-фичу от пилота до регулярного использования.',
    status: 'active'
  },
  {
    id: 'rule-audience-value',
    group: 'audience',
    title: 'Ценность для читателя',
    statement: 'Каждый пост должен давать читателю продуктовый критерий: что проверить, где риск, как понять, что AI-фича стала продуктом.',
    status: 'active'
  },
  {
    id: 'rule-position-demo-not-product',
    group: 'positioning',
    title: 'Демо не равно продукт',
    statement: 'AI-B2B продукт начинается не с красивого ответа модели, а с workflow improvement, evals, trust loop и adoption ritual.',
    status: 'active',
    evidenceNoteId: 'note-demo-magic-fails'
  },
  {
    id: 'rule-position-workflow-first',
    group: 'positioning',
    title: 'Workflow важнее выбора модели',
    statement: 'Если сценарий принятия решения не описан, AI ускоряет неясность вместо создания продуктовой ценности.',
    status: 'active',
    evidenceNoteId: 'note-workflow-risk'
  },
  {
    id: 'rule-style-voice-research-note',
    group: 'styleVoice',
    title: 'Голос исследовательской заметки',
    statement: 'Тон спокойный, наблюдательный, с авторской позицией до советов и чеклистов.',
    status: 'active'
  },
  {
    id: 'rule-style-language-concrete',
    group: 'styleLanguage',
    title: 'Конкретный язык продукта',
    statement: 'Использовать слова workflow, evals, rollout, adoption, trust, rollback только когда они привязаны к сцене или решению.',
    status: 'active'
  },
  {
    id: 'rule-style-rhythm',
    group: 'styleRhythm',
    title: 'Ритм: тезис -> сцена -> вывод',
    statement: 'Пост должен быстро дать конфликт, затем сцену из практики, затем критерий для читателя.',
    status: 'active'
  },
  {
    id: 'rule-anti-ai-no-generic-openers',
    group: 'antiAiPattern',
    title: 'Без стерильных AI-вводных',
    statement: 'Не начинать с фраз вроде "в современном мире AI меняет все"; сразу входить в наблюдение или конфликт.',
    status: 'active'
  },
  {
    id: 'rule-goal-build-audience',
    group: 'goal',
    title: 'Собрать аудиторию AI product builders',
    statement: 'Блог должен привлекать AI PM и founders, которым важны практические принципы AI-B2B productization.',
    status: 'active'
  },
  {
    id: 'rule-goal-research-experience',
    group: 'goal',
    title: 'Показывать исследовательский опыт',
    statement: 'Публикации должны превращать наблюдения из интервью, пилотов и архивов в ясные продуктовые принципы.',
    status: 'active'
  },
  {
    id: 'rule-forbidden-ai-hype',
    group: 'forbiddenTopic',
    title: 'Запрет: AI-хайп без механики',
    statement: 'Не публиковать тезисы о силе AI без продуктового механизма, проверки или ограничения применимости.',
    status: 'active'
  },
  {
    id: 'rule-forbidden-market-predictions',
    group: 'forbiddenTopic',
    title: 'Запрет: гарантированные прогнозы рынка',
    statement: 'Не делать уверенных рыночных прогнозов без данных и явных допущений.',
    status: 'active'
  }
];

const demoTopics: Topic[] = [
  {
    id: 'topic-ai-product-discovery',
    title: 'AI product discovery',
    description: 'Как находить AI-B2B возможности через реальные workflow, интервью и ограничения внедрения.',
    purpose: 'Помогать AI PM выбирать не эффектные демо, а проверяемые продуктовые гипотезы.',
    audienceValue: 'Читатель получает способ понять, где AI действительно меняет рабочий процесс.',
    authorStance: 'Discovery начинается с bottleneck, риска и поведения пользователя, а не с выбора модели.',
    rules: ['Начинать с наблюдения из workflow', 'Показывать trade-off между скоростью и качеством', 'Заканчивать проверяемым критерием'],
    forbiddenAngles: ['model-first hype', 'обещания универсальной автоматизации'],
    weightRange: { min: 20, max: 30 },
    status: 'active'
  },
  {
    id: 'topic-evals-quality-loop',
    title: 'Evals & quality loop',
    description: 'Evals как продуктовая функция, а не внутренняя таблица ML-команды.',
    purpose: 'Показывать, как качество AI-фичи становится видимым для команды и пользователя.',
    audienceValue: 'Читатель понимает, какие проверки нужны до rollout и после него.',
    authorStance: 'Без evals, failure modes и ownership AI-фича остается демо.',
    rules: ['Называть критерий качества', 'Отделять product evals от offline benchmark', 'Показывать владельца проверки'],
    forbiddenAngles: ['абстрактные benchmark без связи с пользователем'],
    weightRange: { min: 20, max: 30 },
    status: 'active'
  },
  {
    id: 'topic-enterprise-trust-rollout',
    title: 'Enterprise trust & rollout',
    description: 'Доверие, rollback, explainability и границы уверенности в enterprise AI.',
    purpose: 'Разобрать, почему enterprise adoption требует доказательств и безопасного отката.',
    audienceValue: 'Читатель видит, что доверие проектируется как часть продукта.',
    authorStance: 'Enterprise users принимают AI через evidence, control и понятную ответственность.',
    rules: ['Показывать источник доверия', 'Объяснять rollback path', 'Не скрывать uncertainty'],
    forbiddenAngles: ['магическое доверие к модели', 'AI как черный ящик без ответственности'],
    weightRange: { min: 15, max: 25 },
    status: 'active'
  },
  {
    id: 'topic-gtm-adoption-economics',
    title: 'GTM/adoption economics',
    description: 'Как AI-фича проходит путь от пилота к регулярному использованию и экономике внедрения.',
    purpose: 'Связать продуктовую ценность AI с adoption, retention и операционными затратами.',
    audienceValue: 'Читатель получает язык для разговора с founders, CPO и sales без demo magic.',
    authorStance: 'Пилот ценен только если понятны adoption ritual, cost of operation и метрика результата.',
    rules: ['Отделять vanity usage от настоящего adoption', 'Показывать экономику эксплуатации', 'Не обещать headcount cuts первым тезисом'],
    forbiddenAngles: ['продажи через страх увольнений', 'ROI без операционных допущений'],
    weightRange: { min: 15, max: 25 },
    status: 'active'
  },
  {
    id: 'topic-workflow-automation-architecture',
    title: 'Workflow automation architecture',
    description: 'Архитектура AI workflow: human-in-loop, escalation, observability, ownership.',
    purpose: 'Показывать, из каких контуров состоит надежная AI-автоматизация.',
    audienceValue: 'Читатель получает практическую карту проектирования AI workflow.',
    authorStance: 'AI автоматизирует не задачу в вакууме, а контур принятия решений с проверками.',
    rules: ['Рисовать контур решения', 'Указывать человека в петле', 'Фиксировать failure mode'],
    forbiddenAngles: ['полная автономия без контроля', 'замена процесса одной кнопкой'],
    weightRange: { min: 10, max: 20 },
    status: 'active'
  }
];

const demoFabulas: Fabula[] = [
  {
    id: 'fabula-research-note',
    title: 'Исследовательская заметка',
    description: 'Наблюдение из практики, которое превращается в аккуратный продуктовый вывод.',
    dramaturgy: 'От конкретного наблюдения к принципу, который можно проверить в своем продукте.',
    structure: ['Сцена или сигнал', 'Что в нем неочевидно', 'Продуктовый принцип', 'Как проверить у себя'],
    proofRequirements: ['Авторская заметка', 'Минимум один пример из интервью или пилота'],
    rules: ['Держать тон исследования', 'Не превращать вывод в чеклист без позиции'],
    weightRange: { min: 25, max: 35 },
    status: 'active'
  },
  {
    id: 'fabula-myth-breakdown',
    title: 'Разбор мифа',
    description: 'Пост, который разбирает популярное заблуждение об AI-B2B продуктах.',
    dramaturgy: 'Сначала формулируется миф, затем показывается, где он ломается в реальном workflow.',
    structure: ['Миф', 'Почему он кажется правдой', 'Где ломается', 'Более точная формулировка'],
    proofRequirements: ['Контрпример', 'Риск для продукта или GTM'],
    rules: ['Не высмеивать аудиторию', 'Давать замену мифу'],
    weightRange: { min: 15, max: 25 },
    status: 'active'
  },
  {
    id: 'fabula-practical-framework',
    title: 'Практический фреймворк',
    description: 'Схема или набор вопросов для PM/founder, который проектирует AI-фичу.',
    dramaturgy: 'От проблемы к рабочему фреймворку с критериями проверки.',
    structure: ['Когда применять', '3-5 элементов фреймворка', 'Как проверить', 'Что может пойти не так'],
    proofRequirements: ['Связь с темой', 'Минимум один failure mode'],
    rules: ['Фреймворк должен быть применим за один рабочий созвон', 'Не добавлять декоративные шаги'],
    weightRange: { min: 20, max: 30 },
    status: 'active'
  },
  {
    id: 'fabula-pilot-postmortem',
    title: 'Postmortem пилота',
    description: 'Разбор провала или риска AI-пилота без обвинений и задним числом.',
    dramaturgy: 'Что обещали, что произошло, какой системный урок забрать.',
    structure: ['Контекст пилота', 'Ожидание', 'Разрыв', 'Причина', 'Урок для следующего запуска'],
    proofRequirements: ['Сигнал из источника', 'Проверяемый урок'],
    rules: ['Не раскрывать приватные детали', 'Фокусироваться на системе, а не на виноватых'],
    weightRange: { min: 10, max: 20 },
    status: 'active'
  },
  {
    id: 'fabula-position-manifesto',
    title: 'Позиционный манифест',
    description: 'Сильный авторский тезис о том, как надо строить AI-B2B продукты.',
    dramaturgy: 'От несогласия с рынком к ясной авторской позиции и критерию качества.',
    structure: ['С чем не согласен', 'Почему это важно', 'Моя позиция', 'Критерий для читателя'],
    proofRequirements: ['Evidence из памяти автора', 'Ограничения тезиса'],
    rules: ['Позиция должна быть острой, но не декларативной', 'Добавлять границы применимости'],
    weightRange: { min: 10, max: 20 },
    status: 'active'
  }
];

const demoAuthorNotes: AuthorNote[] = [
  {
    id: 'note-workflow-risk',
    type: 'thought',
    title: 'Workflow risk важнее выбора модели',
    body:
      'В AI-B2B почти всегда спорят о модели, но настоящий риск сидит в workflow. Если сценарий принятия решения не описан, AI просто ускоряет неясность.',
    sourceUrl: '',
    tags: ['workflow', 'risk', 'AI-B2B'],
    attachments: [],
    capturedAt: '2026-06-10T09:00:00.000Z'
  },
  {
    id: 'note-evals-product-function',
    type: 'thought',
    title: 'Evals должны быть продуктовой функцией',
    body:
      'Evals нельзя прятать как внутреннюю таблицу ML-команды. Для B2B-пользователя это часть продукта: как он понимает качество, границы уверенности и момент, когда нужен человек.',
    sourceUrl: '',
    tags: ['evals', 'product', 'quality'],
    attachments: [],
    capturedAt: '2026-06-10T09:12:00.000Z'
  },
  {
    id: 'note-demo-magic-fails',
    type: 'linkReaction',
    title: 'Demo magic ломается после пилота',
    body:
      'Хороший пример: команда показала сильное AI demo, но после пилота usage не вырос. Похоже, проблема не в модели, а в adoption loop и отсутствии привычного места фичи в рабочем дне.',
    sourceUrl: 'https://example.com/ai-demo-to-adoption',
    tags: ['adoption', 'pilot', 'demo'],
    attachments: [],
    capturedAt: '2026-06-10T09:24:00.000Z'
  },
  {
    id: 'note-correction-gtm-adoption',
    type: 'manualCorrection',
    title: 'Это не support automation, а GTM/adoption',
    body:
      'Радар отнес инфоповод к support automation, но мне кажется, он лучше ложится в GTM/adoption: вопрос не в том, как отвечать тикетам, а как довести AI-фичу до регулярного использования.',
    sourceUrl: '',
    tags: ['gtm', 'adoption', 'manual-correction'],
    attachments: [],
    capturedAt: '2026-06-10T09:40:00.000Z'
  },
  {
    id: 'note-enterprise-trust-loop',
    type: 'thought',
    title: 'Enterprise trust строится через evidence и rollback',
    body:
      'Enterprise users не ждут магии. Им нужно понимать evidence, ограничения, кто отвечает за ошибку и как откатиться. Trust loop важнее красивой генерации.',
    sourceUrl: '',
    tags: ['enterprise', 'trust', 'rollback', 'evidence'],
    attachments: [],
    capturedAt: '2026-06-10T10:05:00.000Z'
  },
  {
    id: 'note-confidence-boundaries',
    type: 'linkReaction',
    title: 'AI-фича должна объяснять границы уверенности',
    body:
      'В customer interview снова всплыло: пользователь не знает, когда AI уверен, а когда угадывает. Без объяснения границ уверенности фича остается игрушкой для early adopters.',
    sourceUrl: 'https://example.com/customer-interview-confidence',
    tags: ['confidence', 'customer-interview', 'trust'],
    attachments: [],
    capturedAt: '2026-06-10T10:20:00.000Z'
  }
];

const demoExternalSources: AuthorExternalSource[] = [
  {
    id: 'source-tg-archive',
    type: 'telegramChannel',
    title: 'TG archive · AI Product Manager',
    url: 'https://t.me/ai_product_manager_demo',
    fileReference: '',
    status: 'needsReview',
    importMode: 'bulkArchive',
    lastCheckedAt: '2026-06-11',
    lastImportedAt: '2026-06-11',
    notes: 'Демо-архив канала: много исторических постов, поэтому крупные действия по умолчанию ведут в архив.'
  },
  {
    id: 'source-customer-interviews',
    type: 'document',
    title: 'Customer interviews · AI adoption',
    url: '',
    fileReference: 'interviews-ai-adoption.md',
    status: 'needsReview',
    importMode: 'reviewedQueue',
    lastCheckedAt: '2026-06-10',
    lastImportedAt: '2026-06-10',
    notes: 'Заметки интервью: могут давать сильное evidence, но требуют ручного review.'
  },
  {
    id: 'source-blog-essays',
    type: 'blogSite',
    title: 'Blog essays · Evals and trust',
    url: 'https://example.com/ai-product-essays',
    fileReference: '',
    status: 'connected',
    importMode: 'reviewedQueue',
    lastCheckedAt: '2026-06-09',
    lastImportedAt: '2026-06-09',
    notes: 'Длинные эссе автора про evals, trust loop и продуктовые ограничения AI.'
  },
  {
    id: 'source-talk-notes',
    type: 'document',
    title: 'Talk notes · Confidence boundaries',
    url: '',
    fileReference: 'confidence-boundaries-talk.pdf',
    status: 'imported',
    importMode: 'archiveOnly',
    lastCheckedAt: '2026-06-08',
    lastImportedAt: '2026-06-08',
    notes: 'Доклад используется как архивный контекст до появления анализа документов.'
  },
  {
    id: 'source-manual-uploads',
    type: 'manualUpload',
    title: 'Manual research uploads',
    url: '',
    fileReference: 'local uploads',
    status: 'planned',
    importMode: 'manualOnly',
    lastCheckedAt: '2026-06-07',
    lastImportedAt: '',
    notes: 'Место для ручных материалов: research snippets, screenshots, заметки из встреч.'
  }
];

const demoImportCandidates: ImportedMemoryCandidate[] = [
  {
    id: 'candidate-demo-adoption-gap',
    sourceId: 'source-tg-archive',
    title: 'Почему demo magic не становится adoption',
    excerpt:
      'В посте повторяется мысль: сильное AI demo не доказывает, что фича займет место в рабочем дне пользователя.',
    originalUrl: 'https://t.me/ai_product_manager_demo/14',
    capturedAt: '2026-05-12',
    detectedTags: ['adoption', 'pilot', 'workflow'],
    duplicateRisk: 'medium',
    suggestedTarget: 'Архив: повторяет текущую фабулу про demo-to-adoption gap',
    reviewStatus: 'new',
    evidencePolicy: 'archiveOnly'
  },
  {
    id: 'candidate-evals-interface',
    sourceId: 'source-blog-essays',
    title: 'Evals как интерфейс доверия',
    excerpt:
      'Автор объясняет, что evals должны быть видимы продуктовой команде и enterprise user, а не только ML-команде.',
    originalUrl: 'https://example.com/ai-product-essays/evals-as-interface',
    capturedAt: '2026-04-18',
    detectedTags: ['evals', 'trust', 'quality'],
    duplicateRisk: 'low',
    suggestedTarget: 'В память: усиливает принцип доверия через качество',
    reviewStatus: 'new',
    evidencePolicy: 'canSupportAssertions'
  },
  {
    id: 'candidate-rollback-path',
    sourceId: 'source-customer-interviews',
    title: 'Rollback path как условие enterprise adoption',
    excerpt:
      'В интервью CPO говорит: команда согласна пробовать AI, если понятно, кто видит ошибку и как быстро откатиться.',
    originalUrl: '',
    capturedAt: '2026-04-25',
    detectedTags: ['enterprise', 'rollback', 'trust'],
    duplicateRisk: 'low',
    suggestedTarget: 'В память: evidence для trust loop',
    reviewStatus: 'new',
    evidencePolicy: 'canSupportAssertions'
  },
  {
    id: 'candidate-confidence-boundary',
    sourceId: 'source-talk-notes',
    title: 'Граница уверенности должна быть частью UX',
    excerpt:
      'Тезис из доклада: AI-фича должна показывать, где она уверена, а где просит человека проверить вывод.',
    originalUrl: '',
    capturedAt: '2026-03-20',
    detectedTags: ['confidence', 'ux', 'human-in-loop'],
    duplicateRisk: 'medium',
    suggestedTarget: 'Архив: сохранить как докладный материал',
    reviewStatus: 'new',
    evidencePolicy: 'archiveOnly'
  },
  {
    id: 'candidate-sales-promise',
    sourceId: 'source-tg-archive',
    title: 'Не обещать сокращение headcount в первом питче',
    excerpt:
      'Автор критикует продажи AI через экономию людей: для B2B adoption лучше говорить о контроле качества и скорости цикла.',
    originalUrl: 'https://t.me/ai_product_manager_demo/31',
    capturedAt: '2026-02-15',
    detectedTags: ['gtm', 'economics', 'positioning'],
    duplicateRisk: 'low',
    suggestedTarget: 'В память: принцип GTM для AI-B2B',
    reviewStatus: 'new',
    evidencePolicy: 'canSupportAssertions'
  },
  {
    id: 'candidate-support-automation-mislabel',
    sourceId: 'source-tg-archive',
    title: 'Support automation как ложная классификация',
    excerpt:
      'Короткая правка автора: инфоповод про пилот скорее относится к GTM/adoption, а не к support automation.',
    originalUrl: 'https://t.me/ai_product_manager_demo/35',
    capturedAt: '2026-06-01',
    detectedTags: ['manual-correction', 'gtm', 'adoption'],
    duplicateRisk: 'high',
    suggestedTarget: 'Архив: уже отражено в ручной корректировке',
    reviewStatus: 'new',
    evidencePolicy: 'archiveOnly'
  },
  {
    id: 'candidate-usage-ritual',
    sourceId: 'source-customer-interviews',
    title: 'AI-фича должна войти в ритуал команды',
    excerpt:
      'PM из SaaS-команды говорит: если AI не встроен в weekly review, через месяц о нем забывают.',
    originalUrl: '',
    capturedAt: '2026-05-03',
    detectedTags: ['workflow', 'adoption', 'ritual'],
    duplicateRisk: 'low',
    suggestedTarget: 'В память: evidence для workflow-first позиции',
    reviewStatus: 'new',
    evidencePolicy: 'canSupportAssertions'
  },
  {
    id: 'candidate-data-readiness',
    sourceId: 'source-blog-essays',
    title: 'Data readiness важнее выбора модели',
    excerpt:
      'В заметке автор спорит с model-first подходом: продуктовая готовность данных определяет качество AI-фичи раньше выбора модели.',
    originalUrl: 'https://example.com/ai-product-essays/data-readiness',
    capturedAt: '2026-01-28',
    detectedTags: ['data', 'workflow', 'quality'],
    duplicateRisk: 'medium',
    suggestedTarget: 'Архив: поддерживающий материал',
    reviewStatus: 'new',
    evidencePolicy: 'archiveOnly'
  },
  {
    id: 'candidate-trust-dashboard',
    sourceId: 'source-manual-uploads',
    title: 'Скриншот trust dashboard',
    excerpt:
      'Ручной upload с наброском панели: confidence, evidence, last rollback и unresolved edge cases.',
    originalUrl: '',
    capturedAt: '2026-06-05',
    detectedTags: ['trust', 'dashboard', 'evidence'],
    duplicateRisk: 'low',
    suggestedTarget: 'Архив: файл требует будущего анализа вложений',
    reviewStatus: 'new',
    evidencePolicy: 'archiveOnly'
  },
  {
    id: 'candidate-ai-feature-boundaries',
    sourceId: 'source-customer-interviews',
    title: 'Пользователь хочет видеть границы AI-фичи',
    excerpt:
      'Customer interview: пользователь доверяет не уверенной формулировке, а объяснению, где система может ошибиться.',
    originalUrl: '',
    capturedAt: '2026-05-29',
    detectedTags: ['confidence', 'trust', 'customer-interview'],
    duplicateRisk: 'medium',
    suggestedTarget: 'В память: близко к текущему evidence, нужен review',
    reviewStatus: 'new',
    evidencePolicy: 'canSupportAssertions'
  },
  {
    id: 'candidate-pilot-economics',
    sourceId: 'source-blog-essays',
    title: 'Экономика пилота должна считаться до генерации',
    excerpt:
      'Автор пишет: если unit economics AI-процесса не ясна, демо только маскирует будущую стоимость эксплуатации.',
    originalUrl: 'https://example.com/ai-product-essays/pilot-economics',
    capturedAt: '2026-02-04',
    detectedTags: ['economics', 'pilot', 'operations'],
    duplicateRisk: 'low',
    suggestedTarget: 'В память: принцип AI-B2B productization',
    reviewStatus: 'new',
    evidencePolicy: 'canSupportAssertions'
  },
  {
    id: 'candidate-human-review',
    sourceId: 'source-talk-notes',
    title: 'Human review не должен быть стыдом продукта',
    excerpt:
      'Докладный тезис: человек в контуре не признак слабой модели, а элемент надежного B2B workflow.',
    originalUrl: '',
    capturedAt: '2026-03-21',
    detectedTags: ['human-in-loop', 'workflow', 'trust'],
    duplicateRisk: 'low',
    suggestedTarget: 'Архив: докладный материал',
    reviewStatus: 'new',
    evidencePolicy: 'archiveOnly'
  },
  {
    id: 'candidate-ai-prd',
    sourceId: 'source-manual-uploads',
    title: 'AI PRD должен содержать failure modes',
    excerpt:
      'Черновик шаблона: к каждой AI-фиче нужны success metric, eval scenario, failure mode и rollback owner.',
    originalUrl: '',
    capturedAt: '2026-06-06',
    detectedTags: ['prd', 'evals', 'rollback'],
    duplicateRisk: 'low',
    suggestedTarget: 'В память: сильный принцип процесса',
    reviewStatus: 'new',
    evidencePolicy: 'canSupportAssertions'
  },
  {
    id: 'candidate-model-benchmark',
    sourceId: 'source-tg-archive',
    title: 'Бенчмарки моделей без workflow ничего не решают',
    excerpt:
      'Пост с высокой похожестью к текущей позиции: автор снова говорит, что выбор модели вторичен к рабочему процессу.',
    originalUrl: 'https://t.me/ai_product_manager_demo/42',
    capturedAt: '2026-05-18',
    detectedTags: ['workflow', 'model-choice', 'quality'],
    duplicateRisk: 'high',
    suggestedTarget: 'Архив: высокая дубль-вероятность',
    reviewStatus: 'new',
    evidencePolicy: 'archiveOnly'
  },
  {
    id: 'candidate-founder-question',
    sourceId: 'source-customer-interviews',
    title: 'Founder спрашивает, кто владеет ошибкой AI',
    excerpt:
      'В интервью founder возвращается к вопросу ownership: кто отвечает за ошибочный AI-ответ перед клиентом.',
    originalUrl: '',
    capturedAt: '2026-05-09',
    detectedTags: ['ownership', 'risk', 'enterprise'],
    duplicateRisk: 'low',
    suggestedTarget: 'В память: риск и governance',
    reviewStatus: 'new',
    evidencePolicy: 'canSupportAssertions'
  },
  {
    id: 'candidate-roadmap-fit',
    sourceId: 'source-blog-essays',
    title: 'AI roadmap должен начинаться с workflow bottleneck',
    excerpt:
      'Автор предлагает выбирать AI-инициативы не по эффектности, а по тому, где bottleneck уже измерим.',
    originalUrl: 'https://example.com/ai-product-essays/workflow-bottleneck',
    capturedAt: '2026-01-19',
    detectedTags: ['roadmap', 'workflow', 'metrics'],
    duplicateRisk: 'medium',
    suggestedTarget: 'Архив: полезно для будущей сетки тем',
    reviewStatus: 'new',
    evidencePolicy: 'archiveOnly'
  },
  {
    id: 'candidate-customer-proof',
    sourceId: 'source-manual-uploads',
    title: 'Фрагмент customer proof для поста',
    excerpt:
      'Короткая выписка: покупатель просит не красивый ответ, а доказательство, что AI видел нужный контекст.',
    originalUrl: '',
    capturedAt: '2026-06-07',
    detectedTags: ['proof', 'evidence', 'customer'],
    duplicateRisk: 'low',
    suggestedTarget: 'В память: evidence для доказательности',
    reviewStatus: 'new',
    evidencePolicy: 'canSupportAssertions'
  },
  {
    id: 'candidate-ai-operating-cost',
    sourceId: 'source-tg-archive',
    title: 'AI operating cost появляется после пилота',
    excerpt:
      'Пост из архива: после пилота всплывают стоимость мониторинга, ручных проверок и поддержки edge cases.',
    originalUrl: 'https://t.me/ai_product_manager_demo/48',
    capturedAt: '2026-05-27',
    detectedTags: ['economics', 'operations', 'pilot'],
    duplicateRisk: 'medium',
    suggestedTarget: 'Архив: полезный контекст экономики',
    reviewStatus: 'new',
    evidencePolicy: 'archiveOnly'
  },
  {
    id: 'candidate-adoption-metric',
    sourceId: 'source-customer-interviews',
    title: 'Adoption metric должен быть рабочим, а не vanity',
    excerpt:
      'Команда считала просмотры AI-виджета, но настоящий сигнал был в повторном использовании в weekly planning.',
    originalUrl: '',
    capturedAt: '2026-05-16',
    detectedTags: ['metrics', 'adoption', 'planning'],
    duplicateRisk: 'low',
    suggestedTarget: 'В память: метрики цели блога и продукта',
    reviewStatus: 'new',
    evidencePolicy: 'canSupportAssertions'
  },
  {
    id: 'candidate-ai-meme',
    sourceId: 'source-manual-uploads',
    title: 'Мем про магический AI assistant',
    excerpt:
      'Материал смешной, но как evidence слабый: может пригодиться только как иллюстрация к посту.',
    originalUrl: '',
    capturedAt: '2026-06-08',
    detectedTags: ['meme', 'illustration'],
    duplicateRisk: 'low',
    suggestedTarget: 'Игнорировать evidence',
    reviewStatus: 'new',
    evidencePolicy: 'ignored'
  }
];

const demoArchiveRecords: ArchiveRecord[] = [
  {
    id: 'archive-seeded-demo-contracts',
    sourceId: 'source-tg-archive',
    title: 'Старый пост про пилоты без контракта качества',
    bodyExcerpt:
      'Автор уже писал, что пилот AI-фичи должен начинаться с контракта качества, а не с выбора модели.',
    originalUrl: 'https://t.me/ai_product_manager_demo/7',
    publishedAt: '2025-12-10',
    acceptedAt: '2026-06-11T08:00:00.000Z',
    acceptanceMode: 'manual',
    evidencePolicy: 'archiveOnly'
  },
  {
    id: 'archive-seeded-interview-boundaries',
    sourceId: 'source-customer-interviews',
    title: 'Интервью: границы уверенности',
    bodyExcerpt:
      'Респондент просит показывать не только ответ AI, но и уровень уверенности, источник и способ проверки.',
    originalUrl: '',
    publishedAt: '2026-03-05',
    acceptedAt: '2026-06-11T08:05:00.000Z',
    acceptanceMode: 'manual',
    evidencePolicy: 'archiveOnly'
  },
  {
    id: 'archive-seeded-talk-loop',
    sourceId: 'source-talk-notes',
    title: 'Доклад: trust loop вместо AI magic',
    bodyExcerpt:
      'Слайд доклада фиксирует связку: evidence, rollback, human review, adoption ritual.',
    originalUrl: '',
    publishedAt: '2026-03-21',
    acceptedAt: '2026-06-11T08:10:00.000Z',
    acceptanceMode: 'manual',
    evidencePolicy: 'archiveOnly'
  }
];

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

const demoRadarsWithFilters: RadarDefinition[] = demoRadars.map((radar) => {
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

export function createDemoWorkspace(): WorkspaceState {
  const authorMemoryEvents = demoAuthorNotes.map(createAuthorMemoryEvent);
  const authorPositionAssertions = inferAuthorPositionAssertions(demoAuthorNotes, authorMemoryEvents);
  const evaluatedSourceSignals = demoSourceSignals.map((signal) => {
    const radar = demoRadarsWithFilters.find((candidate) => candidate.id === signal.radarId);
    return radar ? evaluateSignalAgainstRadarFilters(signal, radar, {
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
      topics: demoTopics
      } as unknown as WorkspaceState) : signal;
  });

  const workspace: WorkspaceState = {
    authorNotes: demoAuthorNotes,
    authorMemoryEvents,
    authorPositionAssertions,
    editorialModel: {
      author:
        'AI Product Manager, ведущий Telegram-блог о исследовательском построении AI-B2B продуктов.',
      audience:
        'AI PM, founders, CPO/product leaders и B2B SaaS команды, которым нужно доводить AI-функции от пилота до регулярного использования.',
      positioning:
        'Исследовательский голос про AI product management: меньше демо-магии, больше workflow, evals, trust loop, adoption и экономики внедрения.',
      fabula:
        'AI-B2B продукт выигрывает не тем, что красиво отвечает в демо, а тем, что помогает пользователю надежно менять рабочий процесс и доверять границам системы.',
      rubrics: ['Product research notes', 'AI adoption', 'Evals & quality', 'Trust loop'],
      styleRules: [
        'Писать как исследователь продукта, а не как AI-евангелист',
        'Фиксировать авторскую позицию до советов',
        'Показывать workflow и trade-offs',
        'Убирать стерильные AI-обобщения'
      ],
      forbiddenTopics: ['AI-хайп без продуктовой механики', 'Гарантированные прогнозы рынка', 'Магическое мышление про модели'],
      goals: [
        'Собрать аудиторию AI PM и founders вокруг практики AI-B2B productization',
        'Показывать исследовательский опыт построения AI-функций',
        'Превращать наблюдения из интервью и пилотов в ясные продуктовые принципы'
      ]
    },
    projectProfile: demoProjectProfile,
    editorialRules: demoEditorialRules,
    editorialSetupRevision: 0,
    editorialValidationRun: null,
    topics: demoTopics,
    fabulas: demoFabulas,
    topicFabulaMatrix: createDefaultTopicFabulaMatrix(demoTopics, demoFabulas),
    radars: demoRadarsWithFilters,
    sourceSignal: {
      id: 'signal-ai-demo-to-adoption-gap',
      type: 'Повторяющийся паттерн',
      title: 'AI-B2B пилоты не переходят из demo magic в adoption',
      source: 'Telegram, customer interviews, заметки автора',
      capturedAt: '2026-06-10',
      summary:
        'Несколько команд показывают сильные AI demo, но после пилота usage не становится регулярным. В заметках повторяются причины: не встроен workflow, нет evals, непонятны границы уверенности и нет rollback path.',
      rawNote:
        'Хороший материал для TG-поста: не спорить про модели, а показать разрыв между демо и продуктом. Это лучше относится к GTM/adoption, чем к support automation.'
    },
    sourceSignals: evaluatedSourceSignals,
    insightCard: null,
    contentPlanItem: null,
    contentPlanItems: [],
    contentPlanSettings: {
      postsPerWeek: 3,
      planningHorizonDays: 14,
      defaultPlatform: 'Telegram',
      allowedFormats: [
        'Исследовательская заметка',
        'Разбор мифа',
        'Практический фреймворк',
        'Postmortem пилота'
      ]
    },
    planWeightWarnings: [],
    postBrief: null,
    postDraft: null,
    editorialChecks: [],
    editorNotes: [],
    finalText: null,
    releasePackage: null,
    editorialLearningNote: null,
    externalSources: demoExternalSources,
    importCandidates: demoImportCandidates,
    archiveRecords: demoArchiveRecords,
    bulkImportActions: [],
    activeSection: 'memory',
    updatedAt: new Date().toISOString()
  };

  const selectedSourceSignal = evaluatedSourceSignals[0];
  const workspaceWithSelectedSignal = {
    ...workspace,
    sourceSignal: selectedSourceSignal
  };

  return {
    ...workspaceWithSelectedSignal,
    contentPlanItems: createBroadcastPlan(workspaceWithSelectedSignal)
  };
}
