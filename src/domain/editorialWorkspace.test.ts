import { describe, expect, it } from 'vitest';
import {
  approveFinalText,
  approvePlanItem,
  approvePostBrief,
  rejectPlanItem,
  rejectPostBrief,
  reviseDraft
} from './editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  createContentPlanItem,
  createEditorNotes,
  createInsightCard,
  createPostBrief,
  createPostDraft,
  runEditorialChecks
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

  it('creates a deterministic draft with thesis, conflict, and CTA from an approved brief', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);

    expect(draft.briefId).toBe(brief.id);
    expect(draft.body).toContain(brief.thesis);
    expect(draft.body).toContain(brief.conflict);
    expect(draft.body).toContain(brief.cta);
  });

  it('creates four editorial checks in a stable order with fact-check warnings', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const checks = runEditorialChecks(draft, brief, workspace.editorialModel);
    const notes = createEditorNotes(checks);

    expect(checks.map((check) => check.type)).toEqual(['style', 'antiAi', 'factCheck', 'policy']);
    expect(checks.find((check) => check.type === 'factCheck')?.status).toBe('warning');
    expect(notes).toHaveLength(4);
  });

  it('revises a draft and approves final text from the current draft body', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const revised = reviseDraft(draft, `${draft.body}\n\nРучная правка главного редактора.`);
    const finalText = approveFinalText(revised);

    expect(revised.version).toBe(2);
    expect(revised.status).toBe('revised');
    expect(finalText.approvalStatus).toBe('approved');
    expect(finalText.body).toContain('Ручная правка');
  });
});
