import { describe, expect, it } from 'vitest';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  createBroadcastPlan,
  createPostCandidates,
  summarizeBroadcastGridDemand
} from './editorialServices';
import { createPublishWindows, normalizeContentPlanSettings } from '../domain/editorialWorkspace';

describe('planning service', () => {
  const startDate = new Date('2026-06-17T00:00:00.000Z');

  it('builds publish windows from the current date, period, days, and times', () => {
    const settings = normalizeContentPlanSettings({
      period: 'week',
      postsPerWeek: 3,
      publishingDays: [3, 5],
      publishingTimes: ['09:00', '17:30'],
      minCandidatesPerSlot: 1,
      maxCandidatesPerSlot: 2,
      defaultPlatform: 'Telegram',
      signalSelectionPolicy: 'hitl-only'
    });

    expect(createPublishWindows(settings, startDate)).toEqual([
      { date: '2026-06-17', time: '09:00' },
      { date: '2026-06-17', time: '17:30' },
      { date: '2026-06-19', time: '09:00' },
      { date: '2026-06-19', time: '17:30' }
    ]);
  });

  it('creates broadcast slots from configured publish windows instead of hardcoded dates', () => {
    const workspace = createDemoWorkspace();
    const settings = normalizeContentPlanSettings({
      ...workspace.contentPlanSettings,
      period: 'week',
      postsPerWeek: 2,
      publishingDays: [3, 5],
      publishingTimes: ['11:00'],
      publishSlots: []
    });
    const items = createBroadcastPlan({ ...workspace, contentPlanSettings: settings }, startDate);

    expect(items).toHaveLength(2);
    expect(items.map((item) => `${item.date} ${item.time}`)).toEqual(['2026-06-17 11:00', '2026-06-19 11:00']);
    expect(items.every((item) => item.format === item.fabulaTitle)).toBe(true);
  });

  it('summarizes candidate deficit and approved concepts separately', () => {
    const workspace = createDemoWorkspace();
    const [approvedCandidate] = createPostCandidates(workspace);
    const settings = normalizeContentPlanSettings({
      ...workspace.contentPlanSettings,
      period: 'week',
      postsPerWeek: 3,
      publishingDays: [3, 5],
      publishingTimes: ['11:00'],
      publishSlots: [],
      minCandidatesPerSlot: 2,
      maxCandidatesPerSlot: 3
    });
    const summary = summarizeBroadcastGridDemand(
      {
        ...workspace,
        contentPlanSettings: settings,
        postCandidates: [{ ...approvedCandidate, approvalStatus: 'approved' }],
        postCandidate: { ...approvedCandidate, approvalStatus: 'approved' }
      },
      startDate
    );

    expect(summary.slotCount).toBe(2);
    expect(summary.availableCandidateCount).toBeGreaterThanOrEqual(2);
    expect(summary.approvedConceptCount).toBe(1);
    expect(summary.minNeededCandidates).toBe(4);
    expect(summary.status).toBe('deficit');
  });

  it('uses explicit calendar publish slots before recurring day rules', () => {
    const workspace = createDemoWorkspace();
    const settings = normalizeContentPlanSettings({
      ...workspace.contentPlanSettings,
      period: 'week',
      publishingDays: [1],
      publishingTimes: ['11:00'],
      publishSlots: [
        { date: '2026-06-20', time: '09:00' },
        { date: '2026-06-21', time: '12:30' }
      ]
    });
    const items = createBroadcastPlan({ ...workspace, contentPlanSettings: settings }, startDate);

    expect(items.map((item) => `${item.date} ${item.time}`)).toEqual(['2026-06-20 09:00', '2026-06-21 12:30']);
  });
});
