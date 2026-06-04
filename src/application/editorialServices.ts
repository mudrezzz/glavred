import type {
  ContentPlanItem,
  EditorialLearningNote,
  EditorialCheck,
  EditorialModel,
  EditorNote,
  FinalText,
  InsightCard,
  PostBrief,
  PostDraft,
  ReleasePackage,
  ReleaseTarget,
  SourceSignal
} from '../domain/editorialWorkspace';

export function createInsightCard(signal: SourceSignal, model: EditorialModel): InsightCard {
  const score = signal.summary.toLowerCase().includes('процесс') ? 0.91 : 0.74;

  return {
    id: 'insight-ai-process-chaos',
    signalId: signal.id,
    title: 'AI-пилоты проваливаются, когда команды автоматизируют хаос',
    whyItMatters:
      'Сигнал точно ложится на фабулу автора: ценность AI появляется не от покупки инструментов, а от перестройки процессов.',
    audienceRelevance: model.audience,
    authorPosition:
      'Выигрывают не те, кто быстрее подключил инструмент, а те, кто навел порядок в работе до автоматизации.',
    rubric: 'Разборы',
    urgency: 'Вечнозеленая тема с актуальным рыночным поводом',
    score,
    banalityRisk: 0.22,
    factGaps: [
      'Нужен один подтвержденный пример провала AI-пилота из публичного источника',
      'Нужна цифра или отчет о доле команд, внедряющих AI без процессных изменений'
    ]
  };
}

export function createContentPlanItem(insight: InsightCard): ContentPlanItem {
  return {
    id: 'plan-ai-process-chaos',
    insightId: insight.id,
    title: insight.title,
    platform: 'Telegram + LinkedIn',
    date: '2026-06-05',
    priority: 'Высокий',
    format: 'Разбор',
    expectedEffect:
      'Усилить репутацию автора как практичного операционного эксперта и собрать обсуждение от основателей.',
    approvalStatus: 'draft'
  };
}

export function createPostBrief(
  planItem: ContentPlanItem,
  insight: InsightCard,
  model: EditorialModel
): PostBrief {
  return {
    id: 'brief-ai-process-chaos',
    planItemId: planItem.id,
    title: 'Почему AI-пилоты проваливаются, когда команда автоматизирует хаос',
    rubric: insight.rubric,
    audience: model.audience,
    thesis:
      'AI не чинит беспорядок в процессах. Он делает его быстрее, дороже и заметнее.',
    conflict:
      'Рынок обсуждает инструменты и модели, но игнорирует операционную дисциплину, без которой AI-пилоты превращаются в имитацию прогресса.',
    authorPosition: insight.authorPosition,
    evidence: [
      'Повторяющийся паттерн из рыночных постов: пилот запущен, но процесс не изменен',
      'Наблюдение автора: автоматизация работает только там, где уже описаны роли, входы и решения',
      'Факт-геп из радара: нужен внешний отчет или публичный кейс для усиления тезиса'
    ],
    examples: [
      'Команда подключила AI к хаотичному найму и получила больше быстрых, но непроверенных кандидатов',
      'Отдел продаж автоматизировал follow-up, не договорившись о критериях качества лида'
    ],
    structure: [
      'Лид: рынок снова спорит, какой AI-инструмент выбрать',
      'Поворот: проблема не в инструменте, а в процессе, который он ускоряет',
      'Разбор: что именно ломается в AI-пилотах без операционной базы',
      'Практический критерий: когда процесс готов к автоматизации',
      'Вывод: сначала дисциплина, потом AI'
    ],
    cta: 'Предложить читателю проверить один процесс перед следующим AI-пилотом.',
    risks: [
      'Не звучать как противник AI-инструментов',
      'Не уйти в абстрактный консалтинг без практического критерия',
      'Подтвердить фактические обобщения источниками'
    ],
    sources: [planItem.platform, 'Рыночные посты о провалах AI-пилотов', 'Заметки автора'],
    approvalStatus: 'draft'
  };
}

export function createPostDraft(postBrief: PostBrief, model: EditorialModel): PostDraft {
  const body = [
    postBrief.title,
    '',
    'Рынок снова спорит, какой AI-инструмент выбрать. Но в большинстве проваленных пилотов проблема начинается раньше: команда пытается автоматизировать процесс, который еще не описан.',
    '',
    `Тезис: ${postBrief.thesis}`,
    '',
    `Конфликт: ${postBrief.conflict}`,
    '',
    `Моя позиция: ${postBrief.authorPosition}`,
    '',
    'Что важно проверить перед новым пилотом:',
    ...postBrief.evidence.map((item, index) => `${index + 1}. ${item}`),
    '',
    'Как это выглядит на практике:',
    ...postBrief.examples.map((item) => `- ${item}`),
    '',
    'Структура решения:',
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
  const hasFactGaps =
    postBrief.evidence.some((item) => item.toLowerCase().includes('факт')) ||
    postBrief.sources.some((item) => item.toLowerCase().includes('рыночн'));
  const mentionsForbiddenTopic = model.forbiddenTopics.some((topic) =>
    draft.body.toLowerCase().includes(topic.toLowerCase())
  );

  return [
    {
      id: 'check-style',
      type: 'style',
      title: 'Стиль',
      status: draft.body.length > 700 ? 'passed' : 'warning',
      summary: 'Текст держит спокойный практический голос автора и не уходит в витринный тон.',
      findings: [
        `Сверено с правилами: ${model.styleRules.slice(0, 2).join(', ')}.`,
        'Главный тезис вынесен в начало, структура читается как разбор.'
      ]
    },
    {
      id: 'check-anti-ai',
      type: 'antiAi',
      title: 'Анти-AI',
      status: 'passed',
      summary: 'Стерильных вводных и обобщенного AI-тона не найдено.',
      findings: [
        'Есть авторская позиция, конфликт и практические примеры.',
        'Драфт не начинается с пустой фразы вроде "в современном мире".'
      ]
    },
    {
      id: 'check-fact',
      type: 'factCheck',
      title: 'Фактчек',
      status: hasFactGaps ? 'warning' : 'passed',
      summary: hasFactGaps
        ? 'Есть фактические места, которые лучше подтвердить перед публикацией.'
        : 'Критичных неподтвержденных фактов не найдено.',
      findings: hasFactGaps
        ? [
            'Нужен внешний отчет или публичный кейс для усиления тезиса.',
            'Источники из фабулы стоит проверить перед выпуском.'
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
        : ['Текст остается в рамках практического AI-внедрения для бизнеса.']
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
      text: 'Лид уже держит конфликт. Перед финалом проверьте, не смягчил ли автор главный тезис.'
    },
    {
      id: 'note-style-editor',
      agent: 'Стиль-редактор',
      tone: 'сухо и практично',
      target: 'структура',
      text: 'Список проверок помогает SMB-аудитории. Не превращайте его в абстрактный консалтинг.'
    },
    {
      id: 'note-fact-editor',
      agent: 'Фактчек',
      tone: factCheck?.status === 'warning' ? 'требует внимания' : 'спокойно',
      target: 'доказательства',
      text:
        factCheck?.status === 'warning'
          ? 'Перед выпуском добавьте внешний источник или явно пометьте пример как авторское наблюдение.'
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
    `- Статус: ручной экспорт подготовлен`,
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
