import type { ArchiveRecord, AuthorExternalSource, ImportedMemoryCandidate } from '../domain/editorialWorkspace';

export const demoExternalSources: AuthorExternalSource[] = [
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

export const demoImportCandidates: ImportedMemoryCandidate[] = [
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

export const demoArchiveRecords: ArchiveRecord[] = [
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
