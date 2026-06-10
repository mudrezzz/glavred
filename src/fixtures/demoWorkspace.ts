import { createAuthorMemoryEvent, inferAuthorPositionAssertions } from '../application/editorialServices';
import type { AuthorNote, WorkspaceState } from '../domain/editorialWorkspace';

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

export function createDemoWorkspace(): WorkspaceState {
  const authorMemoryEvents = demoAuthorNotes.map(createAuthorMemoryEvent);
  const authorPositionAssertions = inferAuthorPositionAssertions(demoAuthorNotes, authorMemoryEvents);

  return {
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
    insightCard: null,
    contentPlanItem: null,
    postBrief: null,
    postDraft: null,
    editorialChecks: [],
    editorNotes: [],
    finalText: null,
    releasePackage: null,
    editorialLearningNote: null,
    activeSection: 'memory',
    updatedAt: new Date().toISOString()
  };
}
