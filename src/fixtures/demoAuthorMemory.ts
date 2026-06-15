import type { AuthorNote } from '../domain/editorialWorkspace';

export const demoAuthorNotes: AuthorNote[] = [
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
