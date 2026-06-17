import type { EditorialWorkItem } from '../../domain/editorialWorkspace';

export type EditorialWorkQueueViewMode = 'list' | 'groups';
export type EditorialWorkGroupMode = 'stage' | 'date' | 'platform' | 'status';

export type EditorialWorkQueueFilters = {
  stage: EditorialWorkItem['stage'] | 'all';
  status: EditorialWorkItem['status'] | 'all';
  platform: string;
  topicId: string;
  fabulaId: string;
  query: string;
};

export type EditorialWorkGroup = {
  id: string;
  title: string;
  items: EditorialWorkItem[];
};

export const defaultEditorialWorkQueueFilters: EditorialWorkQueueFilters = {
  stage: 'all',
  status: 'all',
  platform: 'all',
  topicId: 'all',
  fabulaId: 'all',
  query: ''
};

export function filterEditorialWorkItems(
  items: EditorialWorkItem[],
  filters: EditorialWorkQueueFilters
): EditorialWorkItem[] {
  const query = filters.query.trim().toLowerCase();

  return items.filter((item) => {
    if (filters.stage !== 'all' && item.stage !== filters.stage) return false;
    if (filters.status !== 'all' && item.status !== filters.status) return false;
    if (filters.platform !== 'all' && item.platform !== filters.platform) return false;
    if (filters.topicId !== 'all' && item.topicId !== filters.topicId) return false;
    if (filters.fabulaId !== 'all' && item.fabulaId !== filters.fabulaId) return false;

    if (!query) return true;

    return [item.title, item.topicTitle, item.fabulaTitle, item.platform]
      .filter(Boolean)
      .some((value) => value!.toLowerCase().includes(query));
  });
}

export function groupEditorialWorkItems(
  items: EditorialWorkItem[],
  groupMode: EditorialWorkGroupMode
): EditorialWorkGroup[] {
  const groups = new Map<string, EditorialWorkItem[]>();

  items.forEach((item) => {
    const key = getGroupKey(item, groupMode);
    groups.set(key, [...(groups.get(key) ?? []), item]);
  });

  return Array.from(groups.entries()).map(([title, groupItems]) => ({
    id: `${groupMode}-${title}`,
    title,
    items: groupItems
  }));
}

export function stageLabel(stage: EditorialWorkItem['stage']): string {
  const labels: Record<EditorialWorkItem['stage'], string> = {
    brief: 'Фабула',
    draft: 'Драфт',
    final: 'Финал',
    readyForRelease: 'Готов к выпуску'
  };
  return labels[stage];
}

export function workStatusLabel(status: EditorialWorkItem['status']): string {
  const labels: Record<EditorialWorkItem['status'], string> = {
    todo: 'В очереди',
    inProgress: 'В работе',
    approved: 'Утвержден',
    blocked: 'Блокер'
  };
  return labels[status];
}

export function getEditorialWorkWarnings(item: EditorialWorkItem): string[] {
  const warnings = [];
  if (!item.brief) warnings.push('Фабула еще не подготовлена');
  if (item.editorialChecks.some((check) => check.status === 'warning' || check.status === 'failed')) {
    warnings.push('Есть редакторские предупреждения');
  }
  return warnings;
}

function getGroupKey(item: EditorialWorkItem, groupMode: EditorialWorkGroupMode): string {
  if (groupMode === 'date') return item.date || 'Без даты';
  if (groupMode === 'platform') return item.platform || 'Без площадки';
  if (groupMode === 'status') return workStatusLabel(item.status);
  return stageLabel(item.stage);
}
