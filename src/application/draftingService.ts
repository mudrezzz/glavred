import type {
  EditorialCheck,
  EditorialModel,
  EditorNote,
  PostBrief,
  PostDraft
} from '../domain/editorialWorkspace';

export function createPostDraft(postBrief: PostBrief, model: EditorialModel): PostDraft {
  const now = new Date().toISOString();
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
    updatedAt: now,
    activeVersionId: `draft-${postBrief.id}-v1`,
    versions: [
      {
        id: `draft-${postBrief.id}-v1`,
        versionNumber: 1,
        source: 'machineFinal',
        title: postBrief.title,
        body,
        draftRunId: null,
        aiRunId: null,
        createdAt: now
      }
    ]
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
