import type {
  ContentPlanItem,
  EditorialModel,
  Fabula,
  InsightCard,
  PostBrief,
  Topic,
  TopicFabulaMatrixEntry
} from '../domain/editorialWorkspace';
import { selectCompatibleTopicFabula } from '../domain/editorialWorkspace';

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
