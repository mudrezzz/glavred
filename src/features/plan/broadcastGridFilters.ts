import type { ContentPlanItem, PlanWeightWarning } from '../../domain/editorialWorkspace';

export type BroadcastGridViewMode = 'list' | 'groups' | 'calendar';
export type BroadcastGridGroupMode = 'date' | 'topic' | 'fabula' | 'status' | 'risk';

export interface BroadcastGridFilters {
  status: 'all' | ContentPlanItem['approvalStatus'];
  platform: string;
  topicId: string;
  fabulaId: string;
  risk: 'all' | 'warning' | 'clear';
  query: string;
}

export const DEFAULT_BROADCAST_GRID_FILTERS: BroadcastGridFilters = {
  status: 'all',
  platform: 'all',
  topicId: 'all',
  fabulaId: 'all',
  risk: 'all',
  query: ''
};

export function filterBroadcastItems(
  items: ContentPlanItem[],
  warnings: PlanWeightWarning[],
  filters: BroadcastGridFilters
): ContentPlanItem[] {
  const warningIds = new Set(warnings.filter((warning) => warning.severity !== 'green').map((warning) => warning.targetId));
  const query = filters.query.trim().toLowerCase();

  return items.filter((item) => {
    const hasWarning = warningIds.has(item.id);
    if (filters.status !== 'all' && item.approvalStatus !== filters.status) return false;
    if (filters.platform !== 'all' && item.platform !== filters.platform) return false;
    if (filters.topicId !== 'all' && item.topicId !== filters.topicId) return false;
    if (filters.fabulaId !== 'all' && item.fabulaId !== filters.fabulaId) return false;
    if (filters.risk === 'warning' && !hasWarning) return false;
    if (filters.risk === 'clear' && hasWarning) return false;
    if (!query) return true;
    return [item.title, item.expectedEffect, item.platform, item.topicTitle, item.fabulaTitle]
      .filter(Boolean)
      .some((value) => value!.toLowerCase().includes(query));
  });
}

export function groupBroadcastItems(
  items: ContentPlanItem[],
  warnings: PlanWeightWarning[],
  groupMode: BroadcastGridGroupMode
): Array<{ id: string; title: string; items: ContentPlanItem[] }> {
  const warningIds = new Set(warnings.filter((warning) => warning.severity !== 'green').map((warning) => warning.targetId));
  const groups = new Map<string, ContentPlanItem[]>();

  items.forEach((item) => {
    const id = getGroupId(item, groupMode, warningIds.has(item.id));
    groups.set(id, [...(groups.get(id) ?? []), item]);
  });

  return Array.from(groups.entries()).map(([id, groupedItems]) => ({
    id,
    title: getGroupTitle(id, groupMode),
    items: groupedItems
  }));
}

function getGroupId(item: ContentPlanItem, mode: BroadcastGridGroupMode, hasWarning: boolean): string {
  if (mode === 'date') return item.date || 'none';
  if (mode === 'topic') return item.topicTitle || 'Без темы';
  if (mode === 'fabula') return item.fabulaTitle || 'Без фабулы';
  if (mode === 'status') return item.approvalStatus;
  return hasWarning ? 'warning' : 'clear';
}

function getGroupTitle(id: string, mode: BroadcastGridGroupMode): string {
  if (mode === 'risk') return id === 'warning' ? 'С предупреждениями' : 'Без предупреждений';
  if (mode === 'date' && id !== 'none') return new Date(`${id}T00:00:00`).toLocaleDateString('ru-RU', { day: '2-digit', month: 'long' });
  if (mode === 'date') return 'Без даты';
  return id;
}
