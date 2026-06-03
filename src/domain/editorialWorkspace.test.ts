import { describe, expect, it } from 'vitest';
import {
  approvePlanItem,
  approvePostBrief,
  rejectPlanItem,
  rejectPostBrief
} from './editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  createContentPlanItem,
  createInsightCard,
  createPostBrief
} from '../application/editorialServices';

describe('editorial workspace domain', () => {
  it('keeps approval transitions explicit for plan items and post briefs', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = createPostBrief(planItem, insight, workspace.editorialModel);

    expect(approvePlanItem(planItem).approvalStatus).toBe('approved');
    expect(rejectPlanItem(planItem).approvalStatus).toBe('rejected');
    expect(approvePostBrief(brief).approvalStatus).toBe('approved');
    expect(rejectPostBrief(brief).approvalStatus).toBe('rejected');
  });

  it('creates deterministic outputs for the founder-blog demo signal', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = createPostBrief(planItem, insight, workspace.editorialModel);

    expect(insight.title).toContain('AI-пилоты');
    expect(insight.score).toBeGreaterThan(0.8);
    expect(planItem.approvalStatus).toBe('draft');
    expect(brief.thesis).toContain('AI не чинит беспорядок');
  });
});

