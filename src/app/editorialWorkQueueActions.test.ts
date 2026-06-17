import { describe, expect, it } from 'vitest';
import { createPostDraft } from '../application/editorialServices';
import { approvePostBrief } from '../domain/editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  buildApprovePlanSlotPatch,
  buildPrepareBriefPatch,
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
    expect(firstPatch.editorialWorkItems).toHaveLength(1);
    expect(firstPatch.editorialWorkItems?.[0].id).toBe(`editorial-work-${item.id}`);
    expect(firstPatch.selectedEditorialWorkItemId).toBe(`editorial-work-${item.id}`);
    expect(secondPatch.editorialWorkItems).toHaveLength(1);
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
