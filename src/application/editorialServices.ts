import type {
  ContentPlanItem,
  EditorialModel,
  InsightCard,
  PostBrief,
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

