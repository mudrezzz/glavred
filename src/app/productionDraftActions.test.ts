import { describe, expect, it } from 'vitest';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { buildApprovePlanSlotPatch } from './editorialWorkQueueActions';
import { buildApproveBriefWithGeneratedDraftPatch } from './productionDraftActions';

describe('production draft actions', () => {
  it('syncs a backend generated draft into the selected editorial work item', () => {
    const workspace = createDemoWorkspace();
    const withBrief = { ...workspace, ...buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id) };

    const patch = buildApproveBriefWithGeneratedDraftPatch(withBrief, {
      id: `draft-${withBrief.postBrief!.id}`,
      briefId: withBrief.postBrief!.id,
      title: 'Backend title',
      body: 'Backend body',
      version: 1,
      status: 'draft',
      updatedAt: '2026-06-18T00:00:00+00:00'
    });

    expect(patch.postBrief?.approvalStatus).toBe('approved');
    expect(patch.postDraft?.body).toBe('Backend body');
    expect(patch.editorialChecks?.length).toBeGreaterThan(0);
    expect(patch.editorNotes?.length).toBeGreaterThan(0);
    expect(patch.editorialWorkItems?.[0].draft?.body).toBe('Backend body');
    expect(patch.editorialWorkItems?.[0].stage).toBe('draft');
    expect(patch.finalText).toBeNull();
    expect(patch.postVisual).toBeNull();
  });
});
