import type {
  AuthorMemoryEvent,
  AuthorNote,
  AuthorPositionAssertion,
  ContentPlanItem,
  ContentPlanSettings,
  EditorialCheck,
  EditorialLearningNote,
  EditorialModel,
  EditorNote,
  Fabula,
  FinalText,
  InsightCard,
  PostBrief,
  PostDraft,
  ReleasePackage,
  ReleaseTarget,
  SourceSignal,
  Topic,
  TopicFabulaMatrixEntry,
  WorkspaceState
} from '../domain/editorialWorkspace';
import {
  applyPlanWarnings,
  detectBroadcastPlanConflicts,
  isTopicFabulaEnabled,
  selectCompatibleTopicFabula
} from '../domain/editorialWorkspace';

export function createAuthorMemoryEvent(note: AuthorNote): AuthorMemoryEvent {
  return {
    id: `memory-${note.id}`,
    noteId: note.id,
    type: note.type,
    summary: summarizeAuthorNote(note),
    detectedSignals: detectAuthorSignals(note),
    createdAt: new Date().toISOString()
  };
}

export function inferAuthorPositionAssertions(
  notes: AuthorNote[],
  events: AuthorMemoryEvent[]
): AuthorPositionAssertion[] {
  const evidence = (noteIds: string[], reason: string) =>
    Array.from(new Set(noteIds))
      .map((noteId) => notes.find((note) => note.id === noteId))
      .filter((note): note is AuthorNote => Boolean(note))
      .map((note) => ({
        noteId: note.id,
        quote: excerpt(note.body),
        reason
      }));

  const signalNotes = (signal: string) =>
    events.filter((event) => event.detectedSignals.includes(signal)).map((event) => event.noteId);

  const workflowNotes = signalNotes('workflow-risk');
  const evalNotes = signalNotes('evals');
  const adoptionNotes = signalNotes('adoption');
  const trustNotes = signalNotes('trust');
  const confidenceNotes = signalNotes('confidence-boundaries');

  return [
    {
      id: 'assertion-persona-ai-product-manager',
      type: 'persona',
      title: 'AI Product Manager с исследовательской оптикой',
      statement:
        'Автор смотрит на AI-B2B продукт как на исследование workflow, adoption, доверия и экономики внедрения, а не как на демонстрацию модели.',
      confidence: confidenceFor([...workflowNotes, ...adoptionNotes, ...trustNotes]),
      evidence: evidence(
        [...workflowNotes, ...adoptionNotes, ...trustNotes],
        'Заметки фиксируют продуктовую, а не инструментальную оптику автора.'
      ),
      status: 'inferred'
    },
    {
      id: 'assertion-style-research-notes',
      type: 'style',
      title: 'Стиль: исследовательские заметки без демо-магии',
      statement:
        'Тон должен быть спокойным, наблюдательным и проверяющим: меньше хайпа, больше границ применимости, evidence и честных trade-offs.',
      confidence: confidenceFor([...evalNotes, ...trustNotes, ...confidenceNotes]),
      evidence: evidence(
        [...evalNotes, ...trustNotes, ...confidenceNotes],
        'Evidence показывает интерес автора к проверкам, границам уверенности и доверию.'
      ),
      status: 'inferred'
    },
    {
      id: 'assertion-audience-ai-b2b-builders',
      type: 'audience',
      title: 'Аудитория: строители AI-B2B продуктов',
      statement:
        'Блог должен говорить с AI PM, founders, CPO и B2B SaaS командами, которым нужно довести AI-функцию от пилота до повторяемого adoption.',
      confidence: confidenceFor([...adoptionNotes, ...workflowNotes]),
      evidence: evidence(
        [...adoptionNotes, ...workflowNotes],
        'Заметки явно привязаны к GTM, adoption и продуктовым решениям после пилота.'
      ),
      status: 'inferred'
    },
    {
      id: 'assertion-topic-ai-b2b-product-system',
      type: 'topic',
      title: 'Главная тема: система AI-B2B продукта',
      statement:
        'Сильные темы автора: workflow risk, evals как продуктовая функция, trust loop, adoption после пилота и объяснение границ уверенности.',
      confidence: confidenceFor([...workflowNotes, ...evalNotes, ...trustNotes, ...confidenceNotes]),
      evidence: evidence(
        [...workflowNotes, ...evalNotes, ...trustNotes, ...confidenceNotes],
        'Повторяются темы workflow, evals, trust loop и confidence boundaries.'
      ),
      status: 'inferred'
    },
    {
      id: 'assertion-principle-no-demo-magic',
      type: 'principle',
      title: 'Принцип: демо не равно продукт',
      statement:
        'AI-фича становится продуктом только тогда, когда у нее есть evals, объяснимые границы, rollback, adoption loop и понятная экономика внедрения.',
      confidence: confidenceFor([...evalNotes, ...adoptionNotes, ...confidenceNotes]),
      evidence: evidence(
        [...evalNotes, ...adoptionNotes, ...confidenceNotes],
        'Заметки противопоставляют красивое демо реальному productization.'
      ),
      status: 'inferred'
    }
  ];
}

export function createInsightCard(
  signal: SourceSignal,
  model: EditorialModel,
  topics: Topic[] = [],
  fabulas: Fabula[] = [],
  matrix: TopicFabulaMatrixEntry[] = []
): InsightCard {
  const score = signal.summary.toLowerCase().includes('workflow') ? 0.92 : 0.78;
  const pair = selectCompatibleTopicFabula(topics, fabulas, matrix);
  const rubric = pair?.topic.title ?? model.rubrics[0] ?? 'Product research notes';

  return {
    id: 'insight-ai-demo-to-adoption',
    signalId: signal.id,
    title: 'AI-B2B пилоты ломаются между красивым демо и повторяемым adoption',
    whyItMatters:
      'Сигнал ложится на позицию автора: AI-фича становится продуктом не в момент демо, а когда команда научилась измерять качество, встраивать workflow и доводить пользователя до повторяемого результата.',
    audienceRelevance: model.audience,
    authorPosition:
      'Слабое место AI-B2B продукта обычно не модель, а отсутствие product loop: evals, trust, adoption, rollback и ясная экономика внедрения.',
    rubric,
    urgency: 'Вечнозеленая тема с актуальным рынком AI-пилотов',
    score,
    banalityRisk: 0.18,
    factGaps: [
      'Нужен публичный пример AI-B2B пилота, который не дошел до регулярного использования после демо',
      'Нужен отчет или интервью о роли evals, trust и change management в adoption AI-функций'
    ],
    topicId: pair?.topic.id,
    topicTitle: pair?.topic.title,
    fabulaId: pair?.fabula.id,
    fabulaTitle: pair?.fabula.title
  };
}

export function createContentPlanItem(insight: InsightCard): ContentPlanItem {
  return {
    id: 'plan-ai-demo-to-adoption',
    insightId: insight.id,
    title: insight.title,
    platform: 'Telegram',
    date: '2026-06-12',
    priority: 'Высокий',
    format: 'Исследовательская заметка',
    expectedEffect:
      'Показать AI PM и founders, что productization начинается после вау-демо: с evals, adoption loop и доверия пользователя.',
    approvalStatus: 'draft',
    topicId: insight.topicId,
    topicTitle: insight.topicTitle ?? insight.rubric,
    fabulaId: insight.fabulaId,
    fabulaTitle: insight.fabulaTitle,
    sourceSignalId: insight.signalId,
    manualOverride: false,
    weightWarningIds: []
  };
}

export function createBroadcastPlan(workspace: WorkspaceState): ContentPlanItem[] {
  const settings = workspace.contentPlanSettings;
  const slotCount = Math.max(1, Math.round((settings.postsPerWeek * settings.planningHorizonDays) / 7));
  const existingInsight =
    workspace.insightCard ??
    createInsightCard(
      workspace.sourceSignal,
      workspace.editorialModel,
      workspace.topics,
      workspace.fabulas,
      workspace.topicFabulaMatrix
    );
  const pairs = getBroadcastPairs(workspace.topics, workspace.fabulas, workspace.topicFabulaMatrix);
  const formats = settings.allowedFormats.length > 0 ? settings.allowedFormats : ['Исследовательская заметка'];
  const dates = ['2026-06-15', '2026-06-17', '2026-06-19', '2026-06-22', '2026-06-24', '2026-06-26'];

  const items = Array.from({ length: slotCount }, (_, index) => {
    const pair = pairs[index % pairs.length];
    const format = formats[index % formats.length];
    const date = dates[index % dates.length];
    const priority = index === 0 ? 'Высокий' : index % 3 === 0 ? 'Средний' : 'Нормальный';

    return {
      id: `broadcast-slot-${index + 1}`,
      insightId: existingInsight.id,
      title: createPlanTitle(pair.topic.title, pair.fabula.title),
      platform: settings.defaultPlatform,
      date,
      priority,
      format,
      expectedEffect: createExpectedEffect(pair.topic.title, pair.fabula.title),
      approvalStatus: 'draft' as const,
      topicId: pair.topic.id,
      topicTitle: pair.topic.title,
      fabulaId: pair.fabula.id,
      fabulaTitle: pair.fabula.title,
      sourceSignalId: existingInsight.signalId,
      manualOverride: false,
      weightWarningIds: []
    };
  });

  return applyPlanWarnings(items, detectBroadcastPlanConflicts(workspace, items));
}

function getBroadcastPairs(
  topics: Topic[],
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[]
): Array<{ topic: Topic; fabula: Fabula }> {
  const activeTopics = topics.filter((topic) => topic.status === 'active');
  const activeFabulas = fabulas.filter((fabula) => fabula.status === 'active');
  const pairs = activeTopics.flatMap((topic) =>
    activeFabulas
      .filter((fabula) => isTopicFabulaEnabled(matrix, topic.id, fabula.id))
      .map((fabula) => ({ topic, fabula }))
  );

  if (pairs.length > 0) return pairs;

  const fallback = selectCompatibleTopicFabula(topics, fabulas, matrix);
  return fallback ? [fallback] : [{ topic: topics[0], fabula: fabulas[0] }].filter((pair) => pair.topic && pair.fabula);
}

function createPlanTitle(topicTitle: string, fabulaTitle: string): string {
  return `${topicTitle}: ${fabulaTitle}`;
}

function createExpectedEffect(topicTitle: string, fabulaTitle: string): string {
  return `Проверить, как тема "${topicTitle}" раскрывается через сценарий "${fabulaTitle}" и поддерживает позицию AI Product Manager без demo magic.`;
}

export function createPostBrief(
  planItem: ContentPlanItem,
  insight: InsightCard,
  model: EditorialModel,
  topics: Topic[] = [],
  fabulas: Fabula[] = [],
  matrix: TopicFabulaMatrixEntry[] = []
): PostBrief {
  const pair =
    planItem.topicId && planItem.fabulaId
      ? {
          topic: topics.find((topic) => topic.id === planItem.topicId),
          fabula: fabulas.find((fabula) => fabula.id === planItem.fabulaId)
        }
      : selectCompatibleTopicFabula(topics, fabulas, matrix);
  const topic = pair?.topic ?? topics.find((item) => item.id === insight.topicId);
  const fabula = pair?.fabula ?? fabulas.find((item) => item.id === insight.fabulaId);

  return {
    id: 'brief-ai-demo-to-adoption',
    planItemId: planItem.id,
    title: 'Почему AI-B2B демо еще не продукт',
    rubric: topic?.title ?? insight.rubric,
    audience: model.audience,
    thesis:
      'AI-B2B продукт начинается не с впечатляющего демо, а с доказуемого workflow improvement, evals и доверия пользователя к границам системы.',
    conflict:
      'Команды празднуют момент, когда модель впервые красиво отвечает в демо, но настоящий риск появляется позже: пользователь не понимает, когда фиче верить, как встроить ее в работу и что делать при ошибке.',
    authorPosition: insight.authorPosition,
    evidence: [
      'Авторская заметка: workflow risk важнее выбора модели, потому что плохой сценарий ускоряется вместе с AI',
      'Авторская заметка: evals должны быть продуктовой функцией, а не внутренней таблицей команды',
      'Реакция на интервью: AI-фича должна объяснять границы уверенности, иначе enterprise users не переносят ее в регулярную работу'
    ],
    examples: [
      'Sales copilot выглядит сильным в демо, но менеджеры не используют подсказки, если не видят источник уверенности и способ отката',
      'Support automation снижает нагрузку только тогда, когда команда заранее описала escalation path и критерии качества ответа'
    ],
    structure: [
      ...(fabula
        ? [`Фабула: ${fabula.title}. ${fabula.dramaturgy}`]
        : []),
      'Лид: красивое AI demo почти всегда обманывает команду ощущением готового продукта',
      'Поворот: продукт начинается после демо, когда появляются evals, trust loop и adoption work',
      'Разбор: где ломается путь от pilot к регулярному использованию',
      'Практический критерий: что проверить перед тем, как считать AI-фичу продуктовой',
      'Вывод: AI PM должен проектировать не ответ модели, а систему доверия и использования'
    ],
    cta: 'Предложить читателю проверить одну AI-фичу: есть ли у нее evals, понятные границы уверенности и rollback path.',
    risks: [
      'Не звучать как противник быстрых прототипов: демо полезно, но не равно productization',
      'Не уйти в академичность без практического критерия для AI PM',
      'Подтвердить публичными примерами или явно пометить наблюдения как research notes автора'
    ],
    sources: [planItem.platform, 'Авторская память', 'Customer interviews о внедрении AI-функций'],
    approvalStatus: 'draft',
    topicId: topic?.id ?? insight.topicId,
    topicTitle: topic?.title ?? insight.topicTitle,
    fabulaId: fabula?.id ?? insight.fabulaId,
    fabulaTitle: fabula?.title ?? insight.fabulaTitle
  };
}

export function createPostDraft(postBrief: PostBrief, model: EditorialModel): PostDraft {
  const body = [
    postBrief.title,
    '',
    'Красивое AI-демо почти всегда создает ложное ощущение готового продукта.',
    '',
    `Тезис: ${postBrief.thesis}`,
    '',
    `Конфликт: ${postBrief.conflict}`,
    '',
    `Моя позиция: ${postBrief.authorPosition}`,
    '',
    'Что должно быть до уверенного rollout:',
    ...postBrief.evidence.map((item, index) => `${index + 1}. ${item}`),
    '',
    'Как это выглядит в B2B:',
    ...postBrief.examples.map((item) => `- ${item}`),
    '',
    'Структура заметки:',
    ...postBrief.structure.map((item) => `- ${item}`),
    '',
    `Для аудитории: ${model.audience}`,
    '',
    `Вывод и CTA: ${postBrief.cta}`
  ].join('\n');

  return {
    id: `draft-${postBrief.id}`,
    briefId: postBrief.id,
    title: postBrief.title,
    body,
    version: 1,
    status: 'draft',
    updatedAt: new Date().toISOString()
  };
}

export function runEditorialChecks(
  draft: PostDraft,
  postBrief: PostBrief,
  model: EditorialModel
): EditorialCheck[] {
  const normalizedBody = draft.body.toLowerCase();
  const hasFactGaps =
    postBrief.evidence.some((item) => item.toLowerCase().includes('публич')) ||
    postBrief.sources.some((item) => item.toLowerCase().includes('interview'));
  const mentionsForbiddenTopic = model.forbiddenTopics.some((topic) =>
    normalizedBody.includes(topic.toLowerCase())
  );

  return [
    {
      id: 'check-style',
      type: 'style',
      title: 'Стиль',
      status: draft.body.length > 700 ? 'passed' : 'warning',
      summary: 'Текст держит исследовательский голос AI Product Manager и не уходит в рекламный тон.',
      findings: [
        `Сверено с правилами: ${model.styleRules.slice(0, 2).join(', ')}.`,
        'Главный тезис вынесен в начало, структура читается как research note.'
      ]
    },
    {
      id: 'check-anti-ai',
      type: 'antiAi',
      title: 'Анти-AI',
      status: 'passed',
      summary: 'Стерильных вводных и обобщенного AI-тона не найдено.',
      findings: [
        'Есть авторская позиция, конфликт и практические B2B-примеры.',
        'Драфт не начинается с пустой фразы вроде "в современном мире".'
      ]
    },
    {
      id: 'check-fact',
      type: 'factCheck',
      title: 'Фактчек',
      status: hasFactGaps ? 'warning' : 'passed',
      summary: hasFactGaps
        ? 'Есть места, которые лучше подтвердить внешним примером или явно оставить как авторское наблюдение.'
        : 'Критичных неподтвержденных фактов не найдено.',
      findings: hasFactGaps
        ? [
            'Нужен публичный пример AI-B2B пилота, который не дошел до регулярного использования.',
            'Customer interview лучше цитировать обезличенно или заменить на проверяемый источник.'
          ]
        : ['Текст опирается на утвержденную фабулу и авторские наблюдения.']
    },
    {
      id: 'check-policy',
      type: 'policy',
      title: 'Политика',
      status: mentionsForbiddenTopic ? 'failed' : 'passed',
      summary: mentionsForbiddenTopic
        ? 'Драфт задел одну из запретных тем редакционной модели.'
        : 'Запретные темы и позиционирование соблюдены.',
      findings: mentionsForbiddenTopic
        ? ['Проверьте формулировки рядом с запретными темами редакционной модели.']
        : ['Текст остается в рамках AI product management и B2B product research.']
    }
  ];
}

export function createEditorNotes(checks: EditorialCheck[]): EditorNote[] {
  const factCheck = checks.find((check) => check.type === 'factCheck');
  const policy = checks.find((check) => check.type === 'policy');

  return [
    {
      id: 'note-chief-editor',
      agent: 'Главный редактор',
      tone: 'жестко, но по делу',
      target: 'лид',
      text: 'Лид держит конфликт. Перед финалом проверьте, не смягчил ли автор тезис про разницу между демо и продуктом.'
    },
    {
      id: 'note-style-editor',
      agent: 'Стиль-редактор',
      tone: 'исследовательски',
      target: 'структура',
      text: 'Формат research note подходит TG-блогу AI PM. Не превращайте заметку в чеклист без авторского наблюдения.'
    },
    {
      id: 'note-fact-editor',
      agent: 'Фактчек',
      tone: factCheck?.status === 'warning' ? 'требует внимания' : 'спокойно',
      target: 'доказательства',
      text:
        factCheck?.status === 'warning'
          ? 'Перед выпуском добавьте публичный пример или явно пометьте customer interview как обезличенное наблюдение.'
          : 'Фактических блокеров нет.'
    },
    {
      id: 'note-policy-editor',
      agent: 'Policy review',
      tone: policy?.status === 'failed' ? 'блокер' : 'без блокеров',
      target: 'риски',
      text:
        policy?.status === 'failed'
          ? 'Есть пересечение с запретами редакционной модели, финальное утверждение лучше отложить.'
          : 'Запретные темы не задеты, позиция автора сохранена.'
    }
  ];
}

export function createReleasePackage(
  finalText: FinalText,
  contentPlanItem: ContentPlanItem | null
): ReleasePackage {
  if (finalText.approvalStatus !== 'approved') {
    throw new Error('Release package can be created only from approved final text.');
  }

  const targets = resolveReleaseTargets(contentPlanItem?.platform ?? '');
  const platformLabel = contentPlanItem?.platform ?? targets.join(' + ');
  const markdown = [
    `# ${finalText.title}`,
    '',
    finalText.body,
    '',
    '---',
    '',
    '## Метаданные выпуска',
    '',
    `- Площадки: ${platformLabel}`,
    `- Формат: ${contentPlanItem?.format ?? 'Ручной выпуск'}`,
    `- Дата плана: ${contentPlanItem?.date ?? 'не задана'}`,
    '- Статус: ручной экспорт подготовлен',
    `- Утверждено: ${finalText.approvedAt}`
  ].join('\n');

  return {
    id: `release-${finalText.id}`,
    finalTextId: finalText.id,
    targets,
    markdown,
    checklist: [
      { id: 'final-approved', label: 'Финальный текст утвержден', done: true },
      { id: 'warnings-reviewed', label: 'Фактические warnings просмотрены', done: false },
      { id: 'target-selected', label: 'Площадка выбрана', done: targets.length > 0 },
      { id: 'cta-reviewed', label: 'CTA проверен', done: false },
      { id: 'manual-exported', label: 'Текст скопирован или Markdown скачан', done: false }
    ],
    status: 'draft',
    updatedAt: new Date().toISOString()
  };
}

export function createEditorialLearningNote(
  releasePackage: ReleasePackage,
  finalText: FinalText,
  contentPlanItem: ContentPlanItem | null
): EditorialLearningNote {
  if (releasePackage.status !== 'exported') {
    throw new Error('Editorial learning note can be created only after manual export.');
  }

  return {
    id: `learning-${releasePackage.id}`,
    releasePackageId: releasePackage.id,
    metricSnapshot: {
      views: 0,
      reactions: 0,
      comments: 0,
      saves: 0,
      leads: 0
    },
    observedResult: '',
    audienceReaction: '',
    workingTheses: '',
    trustRubrics: contentPlanItem?.format ?? '',
    qualityAudienceTopics: '',
    strongerVoice: finalText.title,
    repeatFormats: contentPlanItem?.format ?? '',
    seriesCandidates: '',
    status: 'draft',
    updatedAt: new Date().toISOString(),
    capturedAt: null
  };
}

function summarizeAuthorNote(note: AuthorNote): string {
  const prefix: Record<AuthorNote['type'], string> = {
    thought: 'Мысль автора',
    linkReaction: 'Реакция на источник',
    manualCorrection: 'Ручная корректировка'
  };

  const title = note.title.trim() || excerpt(note.body);
  return `${prefix[note.type]}: ${title}`;
}

function detectAuthorSignals(note: AuthorNote): string[] {
  const normalized = `${note.title} ${note.body} ${note.tags.join(' ')}`.toLowerCase();
  const signals: string[] = [];

  if ((note.attachments ?? []).length > 0) {
    signals.push('attached-material');
  }

  if (matches(normalized, ['workflow', 'процесс', 'сценар', 'risk', 'риск'])) {
    signals.push('workflow-risk');
  }

  if (matches(normalized, ['eval', 'оценк', 'метрик', 'провер', 'quality'])) {
    signals.push('evals');
  }

  if (matches(normalized, ['adoption', 'gtm', 'пилот', 'внедрен', 'rollout'])) {
    signals.push('adoption');
  }

  if (matches(normalized, ['trust', 'довер', 'enterprise', 'rollback', 'evidence'])) {
    signals.push('trust');
  }

  if (matches(normalized, ['уверенн', 'confidence', 'границ', 'не знает', 'объясн'])) {
    signals.push('confidence-boundaries');
  }

  return signals.length > 0 ? signals : ['author-observation'];
}

function matches(value: string, needles: string[]): boolean {
  return needles.some((needle) => value.includes(needle));
}

function excerpt(value: string): string {
  return value.length > 180 ? `${value.slice(0, 177)}...` : value;
}

function confidenceFor(noteIds: string[]): number {
  const unique = new Set(noteIds);
  return Math.min(0.95, 0.62 + unique.size * 0.08);
}

function resolveReleaseTargets(platform: string): ReleaseTarget[] {
  const normalized = platform.toLowerCase();
  const targets: ReleaseTarget[] = [];

  if (normalized.includes('telegram')) {
    targets.push('telegram');
  }

  if (normalized.includes('linkedin')) {
    targets.push('linkedin');
  }

  return targets.length > 0 ? targets : ['telegram'];
}
