import { getPlanningHorizonDays } from './settings';
import type { ContentPlanSettings, PublishWindow } from './types';

export function createPublishWindows(settings: ContentPlanSettings, startDate = new Date()): PublishWindow[] {
  if (settings.publishSlots.length > 0) {
    return settings.publishSlots.map((slot) => ({ date: slot.date, time: slot.time }));
  }

  const horizonDays = getPlanningHorizonDays(settings.period);
  const start = toUtcDate(startDate);
  const windows: PublishWindow[] = [];

  for (let offset = 0; offset < horizonDays; offset += 1) {
    const date = new Date(start);
    date.setUTCDate(start.getUTCDate() + offset);
    if (!settings.publishingDays.includes(date.getUTCDay())) continue;

    settings.publishingTimes.forEach((time) => {
      windows.push({ date: formatDate(date), time });
    });
  }

  return windows;
}

export function getBroadcastSlotCount(settings: ContentPlanSettings, startDate = new Date()): number {
  if (settings.publishSlots.length > 0) {
    return settings.publishSlots.length;
  }

  const horizonDays = getPlanningHorizonDays(settings.period);
  const targetSlots = Math.max(1, Math.round((settings.postsPerWeek * horizonDays) / 7));
  const availableWindows = createPublishWindows(settings, startDate).length;

  return Math.max(1, Math.min(targetSlots, availableWindows || targetSlots));
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
