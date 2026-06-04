import { describe, expect, it } from 'vitest';
import {
  approveFinalText,
  approvePlanItem,
  approvePostBrief,
  markLearningNoteCaptured,
  markReleaseExported,
  markReleaseReady,
  rejectPlanItem,
  rejectPostBrief,
  reviseDraft,
  toggleReleaseChecklistItem,
  updateLearningNote
} from './editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  createContentPlanItem,
  createEditorNotes,
  createEditorialLearningNote,
  createInsightCard,
  createPostBrief,
  createPostDraft,
  createReleasePackage,
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

  it('creates a release package from approved final text with platform targets and markdown', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = approveFinalText(draft);
    const releasePackage = createReleasePackage(finalText, planItem);

    expect(releasePackage.targets).toEqual(['telegram', 'linkedin']);
    expect(releasePackage.markdown).toContain(finalText.title);
    expect(releasePackage.markdown).toContain(finalText.body);
    expect(releasePackage.markdown).toContain('Telegram + LinkedIn');
    expect(releasePackage.status).toBe('draft');
  });

  it('does not create a release package from a non-approved final text', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = { ...approveFinalText(draft), approvalStatus: 'draft' as const };

    expect(() => createReleasePackage(finalText, planItem)).toThrow(/approved final text/i);
  });

  it('marks release ready only after checklist completion and then exported', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = approveFinalText(draft);
    const releasePackage = createReleasePackage(finalText, planItem);

    expect(markReleaseReady(releasePackage).status).toBe('draft');

    const completed = releasePackage.checklist.reduce(
      (current, item) => (item.done ? current : toggleReleaseChecklistItem(current, item.id)),
      releasePackage
    );

    expect(markReleaseReady(completed).status).toBe('ready');
    expect(markReleaseExported(completed).status).toBe('exported');
  });

  it('creates analytics scaffold only after manual export', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = approveFinalText(draft);
    const releasePackage = createReleasePackage(finalText, planItem);
    const exported = markReleaseExported(releasePackage);
    const note = createEditorialLearningNote(exported, finalText, planItem);

    expect(() => createEditorialLearningNote(releasePackage, finalText, planItem)).toThrow(/manual export/i);
    expect(note.releasePackageId).toBe(exported.id);
    expect(note.metricSnapshot).toEqual({ views: 0, reactions: 0, comments: 0, saves: 0, leads: 0 });
    expect(note.status).toBe('draft');
  });

  it('captures and reopens editorial learning notes after edits', () => {
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = approveFinalText(draft);
    const exported = markReleaseExported(createReleasePackage(finalText, planItem));
    const note = createEditorialLearningNote(exported, finalText, planItem);
    const captured = markLearningNoteCaptured(note);
    const updated = updateLearningNote(captured, {
      observedResult: 'Тезис про хаос процессов собрал комментарии основателей.'
    });

    expect(captured.status).toBe('captured');
    expect(captured.capturedAt).not.toBeNull();
    expect(updated.status).toBe('draft');
    expect(updated.capturedAt).toBeNull();
    expect(updated.observedResult).toContain('хаос процессов');
  });
});
