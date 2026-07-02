import type { WorkspaceState } from '../workspace/types';
import type { Fabula, Topic, TopicFabulaMatrixEntry } from '../editorial-model/types';
import { isTopicFabulaEnabled } from '../editorial-model/transitions';
import { publicationChannelLabel, resolvePlanItemPublicationChannel } from '../publication-channels/transitions';
import type { ContentPlanItem, PlanWeightWarning } from './types';

// Broadcast-plan transitions keep manual overrides explicit and validation deterministic.
export function approvePlanItem(planItem: ContentPlanItem): ContentPlanItem {
  return { ...planItem, approvalStatus: 'approved' };
}

export function rejectPlanItem(planItem: ContentPlanItem): ContentPlanItem {
  return { ...planItem, approvalStatus: 'rejected' };
}

export function updateContentPlanItem(
  items: ContentPlanItem[],
  updatedItem: ContentPlanItem
): ContentPlanItem[] {
  return items.map((item) => (item.id === updatedItem.id ? updatedItem : item));
}

export function approveContentPlanSlot(items: ContentPlanItem[], itemId: string): ContentPlanItem[] {
  return items.map((item) =>
    item.id === itemId ? approvePlanItem(item) : item
  );
}

export function applyPlanWarnings(
  items: ContentPlanItem[],
  warnings: PlanWeightWarning[]
): ContentPlanItem[] {
  return items.map((item) => ({
    ...item,
    weightWarningIds: warnings
      .filter((warning) => warning.targetType === 'slot' && warning.targetId === item.id)
      .map((warning) => warning.id)
  }));
}

export function detectBroadcastPlanConflicts(
  workspace: Pick<WorkspaceState, 'topics' | 'fabulas' | 'topicFabulaMatrix' | 'publicationChannels'>,
  items: ContentPlanItem[]
): PlanWeightWarning[] {
  const activeItems = items.filter((item) => item.approvalStatus !== 'rejected');
  const warnings: PlanWeightWarning[] = [];
  const topicUsage = usageShare(activeItems, (item) => item.topicId);
  const fabulaUsage = usageShare(activeItems, (item) => item.fabulaId);

  activeItems.forEach((item) => {
    if (!item.date || !item.time || !item.platform || !item.format || !item.topicId || !item.fabulaId) {
      warnings.push({
        id: `slot-incomplete-${item.id}`,
        severity: 'red',
        targetType: 'slot',
        targetId: item.id,
        message: 'Слот неполный: нужны дата, время, площадка, формат, тема и фабула.'
      });
    }

    const topic = workspace.topics.find((candidate) => candidate.id === item.topicId);
    const fabula = workspace.fabulas.find((candidate) => candidate.id === item.fabulaId);
    const channel = resolvePlanItemPublicationChannel(item, workspace.publicationChannels);

    if (channel?.status === 'paused') {
      warnings.push({
        id: `slot-paused-channel-${item.id}`,
        severity: 'yellow',
        targetType: 'slot',
        targetId: item.id,
        message: `Слот использует канал "${publicationChannelLabel(channel)}", который сейчас на паузе.`
      });
    }

    if (topic?.status === 'paused') {
      warnings.push({
        id: `slot-paused-topic-${item.id}`,
        severity: 'yellow',
        targetType: 'slot',
        targetId: item.id,
        message: `Слот использует тему "${topic.title}", которая сейчас на паузе.`
      });
    }

    if (fabula?.status === 'paused') {
      warnings.push({
        id: `slot-paused-fabula-${item.id}`,
        severity: 'yellow',
        targetType: 'slot',
        targetId: item.id,
        message: `Слот использует фабулу "${fabula.title}", которая сейчас на паузе.`
      });
    }

    if (item.topicId && item.fabulaId && !isTopicFabulaEnabled(workspace.topicFabulaMatrix, item.topicId, item.fabulaId)) {
      warnings.push({
        id: `slot-matrix-${item.id}`,
        severity: 'red',
        targetType: 'slot',
        targetId: item.id,
        message: 'Тема и фабула не включены в матрице совместимости.'
      });
    }
  });

  workspace.topics
    .filter((topic) => topic.status === 'active')
    .forEach((topic) => {
      const share = topicUsage.get(topic.id) ?? 0;
      if (share < topic.weightRange.min || share > topic.weightRange.max) {
        warnings.push({
          id: `topic-weight-${topic.id}`,
          severity: share === 0 ? 'red' : 'yellow',
          targetType: 'topic',
          targetId: topic.id,
          message: `Тема "${topic.title}" занимает ${Math.round(share)}% сетки при диапазоне ${topic.weightRange.min}-${topic.weightRange.max}%.`
        });
      }
    });

  workspace.fabulas
    .filter((fabula) => fabula.status === 'active')
    .forEach((fabula) => {
      const share = fabulaUsage.get(fabula.id) ?? 0;
      if (share < fabula.weightRange.min || share > fabula.weightRange.max) {
        warnings.push({
          id: `fabula-weight-${fabula.id}`,
          severity: share === 0 ? 'red' : 'yellow',
          targetType: 'fabula',
          targetId: fabula.id,
          message: `Фабула "${fabula.title}" занимает ${Math.round(share)}% сетки при диапазоне ${fabula.weightRange.min}-${fabula.weightRange.max}%.`
        });
      }
    });

  return warnings;
}

function usageShare(items: ContentPlanItem[], getId: (item: ContentPlanItem) => string | undefined): Map<string, number> {
  const counts = new Map<string, number>();
  const total = Math.max(items.length, 1);
  items.forEach((item) => {
    const id = getId(item);
    if (!id) return;
    counts.set(id, (counts.get(id) ?? 0) + 1);
  });
  return new Map(Array.from(counts.entries()).map(([id, count]) => [id, (count / total) * 100]));
}
