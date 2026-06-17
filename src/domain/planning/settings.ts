import type { ContentPlanSettings, PlanningPeriod, PublishSlot, SignalSelectionPolicy } from './types';

const PERIOD_DAYS: Record<PlanningPeriod, number> = {
  week: 7,
  month: 30,
  quarter: 90
};

const VALID_POLICIES: SignalSelectionPolicy[] = ['hitl-only', 'automatic', 'automatic-with-review'];
const VALID_PERIODS: PlanningPeriod[] = ['week', 'month', 'quarter'];

export const DEFAULT_CONTENT_PLAN_SETTINGS: ContentPlanSettings = {
  period: 'month',
  postsPerWeek: 3,
  planningHorizonDays: PERIOD_DAYS.month,
  publishingDays: [1, 3, 5],
  publishingTimes: ['10:00'],
  publishSlots: [],
  minCandidatesPerSlot: 1,
  maxCandidatesPerSlot: 2,
  defaultPlatform: 'Telegram',
  signalSelectionPolicy: 'hitl-only'
};

export function getPlanningHorizonDays(period: PlanningPeriod): number {
  return PERIOD_DAYS[period];
}

export function normalizeContentPlanSettings(
  saved: Partial<ContentPlanSettings> | null | undefined,
  fallback: ContentPlanSettings = DEFAULT_CONTENT_PLAN_SETTINGS
): ContentPlanSettings {
  const period = normalizePeriod(saved?.period, saved?.planningHorizonDays, fallback.period);
  const postsPerWeek = clampInteger(saved?.postsPerWeek, fallback.postsPerWeek, 1, 21);
  const publishingDays = normalizePublishingDays(saved?.publishingDays, fallback.publishingDays);
  const publishingTimes = normalizePublishingTimes(saved?.publishingTimes, fallback.publishingTimes);
  const publishSlots = normalizePublishSlots(saved?.publishSlots, publishingTimes);
  const minCandidatesPerSlot = clampInteger(saved?.minCandidatesPerSlot, fallback.minCandidatesPerSlot, 1, 10);
  const maxCandidatesPerSlot = Math.max(
    minCandidatesPerSlot,
    clampInteger(saved?.maxCandidatesPerSlot, fallback.maxCandidatesPerSlot, 1, 20)
  );
  const defaultPlatform = typeof saved?.defaultPlatform === 'string' && saved.defaultPlatform.trim()
    ? saved.defaultPlatform.trim()
    : fallback.defaultPlatform;
  const signalSelectionPolicy = VALID_POLICIES.includes(saved?.signalSelectionPolicy as SignalSelectionPolicy)
    ? (saved?.signalSelectionPolicy as SignalSelectionPolicy)
    : fallback.signalSelectionPolicy;

  return {
    period,
    postsPerWeek,
    planningHorizonDays: getPlanningHorizonDays(period),
    publishingDays,
    publishingTimes,
    publishSlots,
    minCandidatesPerSlot,
    maxCandidatesPerSlot,
    defaultPlatform,
    signalSelectionPolicy
  };
}

function normalizePeriod(
  period: PlanningPeriod | undefined,
  legacyHorizonDays: number | undefined,
  fallback: PlanningPeriod
): PlanningPeriod {
  if (VALID_PERIODS.includes(period as PlanningPeriod)) return period as PlanningPeriod;
  if (typeof legacyHorizonDays === 'number') {
    if (legacyHorizonDays <= 7) return 'week';
    if (legacyHorizonDays <= 31) return 'month';
    return 'quarter';
  }
  return fallback;
}

function normalizePublishingDays(days: number[] | undefined, fallback: number[]): number[] {
  const normalized = Array.from(new Set((days ?? []).filter((day) => Number.isInteger(day) && day >= 0 && day <= 6)))
    .sort((left, right) => left - right);
  return normalized.length > 0 ? normalized : fallback;
}

function normalizePublishingTimes(times: string[] | undefined, fallback: string[]): string[] {
  const normalized = Array.from(new Set((times ?? []).map((time) => time.trim()).filter(isValidTime)));
  return normalized.length > 0 ? normalized : fallback;
}

function normalizePublishSlots(slots: PublishSlot[] | undefined, fallbackTimes: string[]): PublishSlot[] {
  const normalized = (slots ?? [])
    .filter((slot) => typeof slot?.date === 'string' && isValidDate(slot.date))
    .map((slot) => ({
      date: slot.date,
      time: isValidTime(slot.time) ? slot.time : fallbackTimes[0] ?? '10:00'
    }));

  const unique = new Map<string, PublishSlot>();
  normalized.forEach((slot) => unique.set(slot.date, slot));
  return Array.from(unique.values()).sort((left, right) => left.date.localeCompare(right.date));
}

function isValidDate(date: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(date) && !Number.isNaN(new Date(`${date}T00:00:00Z`).getTime());
}

function isValidTime(time: string): boolean {
  return /^([01]\d|2[0-3]):[0-5]\d$/.test(time);
}

function clampInteger(value: number | undefined, fallback: number, min: number, max: number): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) return fallback;
  return Math.min(max, Math.max(min, Math.round(value)));
}
