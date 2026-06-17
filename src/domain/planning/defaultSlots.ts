import { getPlanningHorizonDays } from './settings';
import type { ContentPlanSettings, PublishSlot } from './types';

export function createDefaultPublishSlots(settings: ContentPlanSettings, startDate = new Date()): PublishSlot[] {
  const slots: PublishSlot[] = [];
  const start = toUtcDate(startDate);

  for (let offset = 0; offset < getPlanningHorizonDays(settings.period); offset += 1) {
    const date = new Date(start);
    date.setUTCDate(start.getUTCDate() + offset);
    if (!settings.publishingDays.includes(date.getUTCDay())) continue;
    slots.push({ date: formatDate(date), time: settings.publishingTimes[0] ?? '10:00' });
  }

  return slots.slice(0, Math.max(1, Math.round((settings.postsPerWeek * getPlanningHorizonDays(settings.period)) / 7)));
}

function toUtcDate(date: Date): Date {
  return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
}

function formatDate(date: Date): string {
  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, '0');
  const day = String(date.getUTCDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}
