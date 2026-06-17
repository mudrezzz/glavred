import { describe, expect, it } from 'vitest';
import { createPostDraft } from '../application/editorialServices';
import { approvePostBrief } from '../domain/editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  buildApproveBriefAndCreateDraftPatch,
  buildApprovePlanSlotPatch,
  buildPrepareBriefPatch,
  buildReturnEditorialWorkItemToCandidatesPatch,
  buildSelectEditorialWorkItemPatch,
  withEditorialWorkItemSync
} from './editorialWorkQueueActions';

describe('editorial work queue actions', () => {
  it('approves a plan slot into one stable editorial work item', () => {
    const workspace = createDemoWorkspace();
    const item = workspace.contentPlanItems[0];
    const firstPatch = buildApprovePlanSlotPatch(workspace, item.id);
    const secondPatch = buildApprovePlanSlotPatch({ ...workspace, ...firstPatch }, item.id);

    expect(firstPatch.contentPlanItem?.id).toBe(item.id);
    expect(firstPatch.postBrief?.planItemId).toBe(item.id);
    expect(firstPatch.editorialWorkItems).toHaveLength(1);
    expect(firstPatch.editorialWorkItems?.[0].id).toBe(`editorial-work-${item.id}`);
    expect(firstPatch.editorialWorkItems?.[0].brief?.id).toBe(firstPatch.postBrief?.id);
    expect(firstPatch.selectedEditorialWorkItemId).toBe(`editorial-work-${item.id}`);
    expect(secondPatch.editorialWorkItems).toHaveLength(1);
  });

  it('keeps selected work item artifacts tied to the chosen plan slot', () => {
    const workspace = createDemoWorkspace();
    const firstPatch = buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id);
    const withFirst = { ...workspace, ...firstPatch };
    const secondPatch = buildApprovePlanSlotPatch(withFirst, workspace.contentPlanItems[1].id);
    const withSecond = { ...withFirst, ...secondPatch };
    const firstSelected = buildSelectEditorialWorkItemPatch(withSecond, firstPatch.selectedEditorialWorkItemId!);
    const secondSelected = buildSelectEditorialWorkItemPatch(
      { ...withSecond, ...firstSelected },
      secondPatch.selectedEditorialWorkItemId!
    );

    expect(firstPatch.postBrief?.id).toBe(`brief-${workspace.contentPlanItems[0].id}`);
    expect(secondPatch.postBrief?.id).toBe(`brief-${workspace.contentPlanItems[1].id}`);
    expect(firstSelected.postBrief?.title).toBe(workspace.contentPlanItems[0].title);
    expect(secondSelected.postBrief?.title).toBe(workspace.contentPlanItems[1].title);
    expect(firstSelected.postBrief?.title).not.toBe(secondSelected.postBrief?.title);
  });

  it('approves a brief and creates the first draft in the selected work item', () => {
    const workspace = createDemoWorkspace();
    const approved = buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id);
    const current = { ...workspace, ...approved };
    const patch = buildApproveBriefAndCreateDraftPatch(current);

    expect(patch.postBrief?.approvalStatus).toBe('approved');
    expect(patch.postDraft?.briefId).toBe(patch.postBrief?.id);
    expect(patch.editorialChecks?.length).toBeGreaterThan(0);
    expect(patch.editorNotes?.length).toBeGreaterThan(0);
    expect(patch.editorialWorkItems?.[0].brief?.approvalStatus).toBe('approved');
    expect(patch.editorialWorkItems?.[0].draft?.id).toBe(patch.postDraft?.id);
    expect(patch.editorialWorkItems?.[0].stage).toBe('draft');
  });

  it('returns an editorial work item to candidates and clears production artifacts', () => {
    const workspace = createDemoWorkspace();
    const item = workspace.contentPlanItems[0];
    const approved = buildApprovePlanSlotPatch(workspace, item.id);
    const current = { ...workspace, ...approved };
    const patch = buildReturnEditorialWorkItemToCandidatesPatch(current, approved.selectedEditorialWorkItemId!);

    expect(patch.contentPlanItems?.find((planItem) => planItem.id === item.id)?.approvalStatus).toBe('draft');
    expect(patch.editorialWorkItems).toEqual([]);
    expect(patch.selectedEditorialWorkItemId).toBeNull();
    expect(patch.postBrief).toBeNull();
    expect(patch.postDraft).toBeNull();
    expect(patch.finalText).toBeNull();
  });

  it('prepares a brief inside the selected work item and opens editing', () => {
    const workspace = createDemoWorkspace();
    const item = workspace.contentPlanItems[0];
    const patch = buildPrepareBriefPatch(workspace, item);

    expect(patch.activeSection).toBe('edit');
    expect(patch.postBrief?.planItemId).toBe(item.id);
    expect(patch.editorialWorkItems).toHaveLength(1);
    expect(patch.editorialWorkItems?.[0].brief?.id).toBe(patch.postBrief?.id);
    expect(patch.postDraft).toBeNull();
    expect(patch.finalText).toBeNull();
  });

  it('saves current compatibility artifacts before selecting another work item', () => {
    const workspace = createDemoWorkspace();
    const first = buildPrepareBriefPatch(workspace, workspace.contentPlanItems[0]);
    const second = buildPrepareBriefPatch(
      { ...workspace, ...first },
      workspace.contentPlanItems[1]
    );
    const selected = { ...workspace, ...second };
    const approvedBrief = approvePostBrief(selected.postBrief!);
    const postDraft = createPostDraft(approvedBrief, workspace.editorialModel);
    const syncedWorkspace = {
      ...selected,
      postBrief: approvedBrief,
      postDraft,
      editorialWorkItems: withEditorialWorkItemSync(selected, { postBrief: approvedBrief, postDraft }).editorialWorkItems!
    };
    const patch = buildSelectEditorialWorkItemPatch(syncedWorkspace, first.selectedEditorialWorkItemId!);

    expect(patch.selectedEditorialWorkItemId).toBe(first.selectedEditorialWorkItemId);
    expect(patch.postBrief?.id).toBe(first.postBrief?.id);
    expect(patch.postDraft).toBeNull();
    expect(patch.editorialWorkItems?.find((item) => item.id === second.selectedEditorialWorkItemId)?.draft?.id).toBe(postDraft.id);
  });
});
