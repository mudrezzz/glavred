import {
  approveContentPlanSlot,
  applyPlanWarnings,
  createEditorialWorkItem,
  detectBroadcastPlanConflicts,
  syncEditorialWorkItemArtifacts,
  upsertEditorialWorkItem,
  type ContentPlanItem,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import { createPostBrief, createWorkspaceInsightCard } from '../application/editorialServices';

export function buildApprovePlanSlotPatch(workspace: WorkspaceState, itemId: string): Partial<WorkspaceState> {
  const approvedItems = approveContentPlanSlot(workspace.contentPlanItems, itemId);
  const planWeightWarnings = detectBroadcastPlanConflicts(workspace, approvedItems);
  const contentPlanItems = applyPlanWarnings(approvedItems, planWeightWarnings);
  const contentPlanItem = contentPlanItems.find((item) => item.id === itemId) ?? null;

  if (!contentPlanItem) {
    return { contentPlanItems, contentPlanItem, planWeightWarnings };
  }

  const editorialWorkItem = createEditorialWorkItem(
    contentPlanItem,
    {},
    workspace.postCandidate?.id
  );
  const editorialWorkItems = upsertEditorialWorkItem(workspace.editorialWorkItems, editorialWorkItem);

  return {
    contentPlanItems,
    contentPlanItem,
    planWeightWarnings,
    editorialWorkItems,
    selectedEditorialWorkItemId: workspace.selectedEditorialWorkItemId ?? editorialWorkItem.id
  };
}

export function buildPrepareBriefPatch(workspace: WorkspaceState, item: ContentPlanItem): Partial<WorkspaceState> {
  const insightCard = workspace.insightCard ?? createWorkspaceInsightCard(workspace);
  const postBrief = createPostBrief(
    item,
    insightCard,
    workspace.editorialModel,
    workspace.topics,
    workspace.fabulas,
    workspace.topicFabulaMatrix
  );
  const editorialWorkItem = createEditorialWorkItem(
    item,
    {
      brief: postBrief,
      draft: null,
      editorialChecks: [],
      editorNotes: [],
      finalText: null
    },
    workspace.postCandidate?.id
  );

  return {
    insightCard,
    contentPlanItem: item,
    editorialWorkItems: upsertEditorialWorkItem(workspace.editorialWorkItems, editorialWorkItem),
    selectedEditorialWorkItemId: editorialWorkItem.id,
    postBrief,
    postDraft: null,
    editorialChecks: [],
    editorNotes: [],
    finalText: null,
    releasePackage: null,
    editorialLearningNote: null,
    activeSection: 'edit'
  };
}

export function buildSelectEditorialWorkItemPatch(
  workspace: WorkspaceState,
  workItemId: string
): Partial<WorkspaceState> {
  const syncedItems = syncSelectedEditorialWorkItem(workspace);
  const selected = syncedItems.find((item) => item.id === workItemId);
  const contentPlanItem =
    workspace.contentPlanItems.find((item) => item.id === selected?.contentPlanItemId) ??
    workspace.contentPlanItem;

  return {
    editorialWorkItems: syncedItems,
    selectedEditorialWorkItemId: selected?.id ?? null,
    contentPlanItem,
    postBrief: selected?.brief ?? null,
    postDraft: selected?.draft ?? null,
    editorialChecks: selected?.editorialChecks ?? [],
    editorNotes: selected?.editorNotes ?? [],
    finalText: selected?.finalText ?? null,
    releasePackage: null,
    editorialLearningNote: null,
    activeSection: 'edit'
  };
}

export function withEditorialWorkItemSync(
  workspace: WorkspaceState,
  patch: Partial<WorkspaceState>
): Partial<WorkspaceState> {
  const nextWorkspace = { ...workspace, ...patch };

  return {
    ...patch,
    editorialWorkItems: syncSelectedEditorialWorkItem(nextWorkspace)
  };
}

function syncSelectedEditorialWorkItem(workspace: WorkspaceState) {
  return syncEditorialWorkItemArtifacts(
    workspace.editorialWorkItems,
    workspace.selectedEditorialWorkItemId,
    {
      brief: workspace.postBrief,
      draft: workspace.postDraft,
      editorialChecks: workspace.editorialChecks,
      editorNotes: workspace.editorNotes,
      finalText: workspace.finalText
    }
  );
}
