import type { ContentPlanItem, ContentPlanSettings, PublishSlot } from '../../domain/editorialWorkspace';

export function groupBroadcastItemsByDate(items: ContentPlanItem[]): Map<string, ContentPlanItem[]> {
  const groups = new Map<string, ContentPlanItem[]>();
  items.forEach((item) => {
    if (!item.date) return;
    groups.set(item.date, [...(groups.get(item.date) ?? []), item]);
  });
  return groups;
}

export function getInitialBroadcastCalendarDate(
  items: ContentPlanItem[],
  settings: ContentPlanSettings
): string {
  return items.find((item) => item.date)?.date ?? settings.publishSlots[0]?.date ?? '';
}

export function withBroadcastItemSlots(
  settings: ContentPlanSettings,
  items: ContentPlanItem[]
): ContentPlanSettings {
  const slotsByDate = new Map<string, PublishSlot>();

  settings.publishSlots.forEach((slot) => slotsByDate.set(slot.date, slot));
  items.forEach((item) => {
    if (!item.date) return;
    slotsByDate.set(item.date, {
      date: item.date,
      time: item.time || settings.publishingTimes[0] || '10:00'
    });
  });

  return {
    ...settings,
    publishSlots: Array.from(slotsByDate.values()).sort((left, right) =>
      left.date.localeCompare(right.date)
    )
  };
}
