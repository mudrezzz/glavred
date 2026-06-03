import { describe, expect, it } from 'vitest';
import { EditorialWorkflow, MVP_MODULES } from './editorialWorkflow';

describe('EditorialWorkflow', () => {
  it('keeps the editorial loop in source-to-analytics order', () => {
    const workflow = EditorialWorkflow.default();

    expect(workflow.stages().map((stage) => stage.id)).toEqual([
      'source_radar',
      'insight_cards',
      'content_plan',
      'post_brief',
      'draft',
      'editorial_checks',
      'export',
      'learning'
    ]);
  });

  it('marks human approval gates for plan, brief, and final editorial checks', () => {
    const workflow = EditorialWorkflow.default();

    expect(workflow.approvalGates().map((stage) => stage.id)).toEqual([
      'content_plan',
      'post_brief',
      'editorial_checks'
    ]);
  });

  it('returns the next stage or null at the end of the loop', () => {
    const workflow = EditorialWorkflow.default();

    expect(workflow.nextStage('content_plan')?.id).toBe('post_brief');
    expect(workflow.nextStage('learning')).toBeNull();
  });

  it('keeps the first MVP perimeter to five brief-defined modules', () => {
    expect(MVP_MODULES.map((module) => module.id)).toEqual([
      'editorial_bible',
      'sources_and_insights',
      'content_plan',
      'post_brief',
      'draft_and_review'
    ]);
  });
});
