import { describe, expect, it } from 'vitest';
import { blockedInfoFromCompletedRun } from './draftRunBlocked';
import { draftFromCompletedRun, type DraftRunResponse, type DraftRunStepStatus } from './draftRunClient';

describe('draftRunClient blocked runs', () => {
  it('detects a quality-blocked completed run', () => {
    const run = makeBlockedRun();

    expect(blockedInfoFromCompletedRun(run)).toEqual({
      runId: 'draft-run-blocked',
      feasibilityStatus: 'needs_human_decision',
      reason: 'Missing source signal.',
      findings: ['Draft run has no linked source signal.']
    });
    expect(() => draftFromCompletedRun(run)).toThrow('completed without final draft');
  });
});

function makeBlockedRun(): DraftRunResponse {
  return {
    id: 'draft-run-blocked',
    status: 'succeeded',
    steps: [
      step('context', 'succeeded'),
      {
        ...step('feasibility', 'succeeded'),
        artifactPayload: {
          status: 'needs_human_decision',
          summary: 'Missing source signal.',
          findings: [{ title: 'Missing source signal', detail: 'Draft run has no linked source signal.' }]
        }
      },
      {
        ...step('complete', 'succeeded'),
        artifactPayload: { status: 'blocked', blockedBy: 'feasibility' }
      }
    ],
    finalDraft: null,
    error: null,
    createdAt: '2026-06-19T00:00:00.000Z',
    updatedAt: '2026-06-19T00:00:00.000Z'
  };
}

function step(key: string, status: DraftRunStepStatus) {
  return {
    key,
    status,
    title: key,
    artifactPayload: {},
    error: null,
    startedAt: null,
    completedAt: null
  };
}
