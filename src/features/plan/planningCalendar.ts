import type { ContentPlanSettings, PublishSlot } from '../../domain/editorialWorkspace';
import { getPlanningHorizonDays } from '../../domain/editorialWorkspace';

export interface CalendarDay {
  date: string;
  dayOfMonth: number;
  inPeriod: boolean;
  isSelected: boolean;
  isToday: boolean;
}

export interface CalendarMonth {
  key: string;
  title: string;
  weeks: CalendarDay[][];
}

export interface PublishSelectionSummary {
  extra: number;
  remaining: number;
  selected: number;
  target: number;
}

export function createPlanningCalendarMonths(
  settings: ContentPlanSettings,
  startDate = getCalendarStartDate(settings)
): CalendarMonth[] {
  const start = toUtcDate(startDate);
  const horizonDays = getPlanningHorizonDays(settings.period);
  const end = addDays(start, horizonDays - 1);
  const selectedDates = new Set(settings.publishSlots.map((slot) => slot.date));
  const monthCount = settings.period === 'quarter' ? 3 : 1;

  return Array.from({ length: monthCount }, (_, index) => {
    const monthStart = settings.period === 'week'
      ? start
      : new Date(Date.UTC(start.getUTCFullYear(), start.getUTCMonth() + index, 1));
    const gridStart = addDays(monthStart, -getMondayBasedDay(monthStart));
    const monthEnd = new Date(Date.UTC(monthStart.getUTCFullYear(), monthStart.getUTCMonth() + 1, 0));
    const weeks: CalendarDay[][] = [];
    const weekLimit = settings.period === 'week' ? 1 : Math.ceil((getMondayBasedDay(monthStart) + monthEnd.getUTCDate()) / 7);

    for (let weekIndex = 0; weekIndex < weekLimit; weekIndex += 1) {
      weeks.push(Array.from({ length: 7 }, (_, dayIndex) => {
        const date = addDays(gridStart, weekIndex * 7 + dayIndex);
        const id = formatDate(date);
        return {
          date: id,
          dayOfMonth: date.getUTCDate(),
          inPeriod: date >= start && date <= end,
          isSelected: selectedDates.has(id),
          isToday: id === formatDate(toUtcDate(new Date()))
        };
      }));
    }

    return {
      key: formatMonthKey(monthStart),
      title: monthStart.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric', timeZone: 'UTC' }),
      weeks
    };
  });
}

export function getPublishSelectionSummary(settings: ContentPlanSettings): PublishSelectionSummary {
  const target = Math.max(1, Math.round((settings.postsPerWeek * getPlanningHorizonDays(settings.period)) / 7));
  const selected = settings.publishSlots.length;
  return {
    extra: Math.max(0, selected - target),
    remaining: Math.max(0, target - selected),
    selected,
    target
  };
}

export function getCalendarStartDate(settings: ContentPlanSettings): Date {
  const firstSlot = settings.publishSlots[0]?.date;
  return firstSlot ? new Date(`${firstSlot}T00:00:00Z`) : toUtcDate(new Date());
}

export function togglePublishSlot(settings: ContentPlanSettings, date: string, time: string): PublishSlot[] {
  const exists = settings.publishSlots.some((slot) => slot.date === date);
  if (exists) {
    return settings.publishSlots.filter((slot) => slot.date !== date);
  }
  return [...settings.publishSlots, { date, time }].sort((left, right) => left.date.localeCompare(right.date));
}

export function getWeekdaysFromSlots(slots: PublishSlot[]): number[] {
  const days = new Set<number>();
  slots.forEach((slot) => days.add(new Date(`${slot.date}T00:00:00Z`).getUTCDay()));
  return Array.from(days).sort((left, right) => left - right);
}

function getMondayBasedDay(date: Date): number {
  return (date.getUTCDay() + 6) % 7;
}

function addDays(date: Date, offset: number): Date {
  const next = new Date(date);
  next.setUTCDate(next.getUTCDate() + offset);
  return next;
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

function formatMonthKey(date: Date): string {
  return `${date.getUTCFullYear()}-${date.getUTCMonth() + 1}`;
}
