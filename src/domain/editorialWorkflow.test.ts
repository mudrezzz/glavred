import { describe, expect, it } from 'vitest';
import { EditorialWorkflow } from './editorialWorkflow';

describe('EditorialWorkflow', () => {
  it('keeps the editorial loop in source-to-analytics order', () => {
    const workflow = EditorialWorkflow.default();

    expect(workflow.stages().map((stage) => stage.id)).toEqual([
      'sources',
      'insights',
      'plan',
      'brief',
      'draft',
      'editing',
      'release',
      'analytics'
    ]);
  });

  it('marks human approval gates for plan, brief, and editing', () => {
    const workflow = EditorialWorkflow.default();

    expect(
      workflow
        .stages()
        .filter((stage) => stage.requiresApproval)
        .map((stage) => stage.id)
    ).toEqual(['plan', 'brief', 'editing']);
  });

  it('returns the next stage or null at the end of the loop', () => {
    const workflow = EditorialWorkflow.default();

    expect(workflow.nextStage('plan')?.id).toBe('brief');
    expect(workflow.nextStage('analytics')).toBeNull();
  });
});
