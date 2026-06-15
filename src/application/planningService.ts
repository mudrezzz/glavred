import type {
  ContentPlanItem,
  EditorialModel,
  Fabula,
  InsightCard,
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
