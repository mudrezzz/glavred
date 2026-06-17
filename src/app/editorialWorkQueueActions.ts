import {
  approveContentPlanSlot,
  applyPlanWarnings,
  createEditorialWorkItem,
  detectBroadcastPlanConflicts,
  replacePostCandidate,
  syncEditorialWorkItemArtifacts,
  upsertEditorialWorkItem,
  type ContentPlanItem,
  type PostCandidate,
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

  const insightCard = workspace.insightCard ?? createWorkspaceInsightCard(workspace);
  const postBrief = createPostBrief(
    contentPlanItem,
    insightCard,
    workspace.editorialModel,
    workspace.topics,
    workspace.fabulas,
    workspace.topicFabulaMatrix
  );
  const editorialWorkItem = createEditorialWorkItem(contentPlanItem, { brief: postBrief }, workspace.postCandidate?.id);
  const editorialWorkItems = upsertEditorialWorkItem(workspace.editorialWorkItems, editorialWorkItem);

  return {
    insightCard,
    contentPlanItems,
    contentPlanItem,
    planWeightWarnings,
    editorialWorkItems,
    selectedEditorialWorkItemId: editorialWorkItem.id,
    postBrief,
    postDraft: null,
    editorialChecks: [],
    editorNotes: [],
    finalText: null,
    releasePackage: null,
    editorialLearningNote: null
  };
}

export function buildReturnEditorialWorkItemToCandidatesPatch(
  workspace: WorkspaceState,
  workItemId: string
): Partial<WorkspaceState> {
  const workItem = workspace.editorialWorkItems.find((item) => item.id === workItemId);
  if (!workItem) return {};

  const draftItems = workspace.contentPlanItems.map((item) =>
    item.id === workItem.contentPlanItemId ? { ...item, approvalStatus: 'draft' as const } : item
  );
  const planWeightWarnings = detectBroadcastPlanConflicts(workspace, draftItems);
  const contentPlanItems = applyPlanWarnings(draftItems, planWeightWarnings);
  const editorialWorkItems = workspace.editorialWorkItems.filter((item) => item.id !== workItemId);
  const selected =
    workspace.selectedEditorialWorkItemId === workItemId
      ? editorialWorkItems[0] ?? null
      : editorialWorkItems.find((item) => item.id === workspace.selectedEditorialWorkItemId) ?? null;
  const postCandidate = getReturnedCandidate(workspace, workItem.postCandidateId);

  return {
    contentPlanItems,
    contentPlanItem: selected ? contentPlanItems.find((item) => item.id === selected.contentPlanItemId) ?? null : null,
    planWeightWarnings,
    editorialWorkItems,
    selectedEditorialWorkItemId: selected?.id ?? null,
    postCandidates: postCandidate ? replacePostCandidate(workspace.postCandidates, postCandidate) : workspace.postCandidates,
    postCandidate: postCandidate && workspace.postCandidate?.id === postCandidate.id ? postCandidate : workspace.postCandidate,
    postBrief: selected?.brief ?? null,
    postDraft: selected?.draft ?? null,
    editorialChecks: selected?.editorialChecks ?? [],
    editorNotes: selected?.editorNotes ?? [],
    finalText: selected?.finalText ?? null,
    releasePackage: null,
    editorialLearningNote: null
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

function getReturnedCandidate(workspace: WorkspaceState, postCandidateId: string | undefined): PostCandidate | null {
  if (!postCandidateId) return null;
  const candidate = [workspace.postCandidate, ...workspace.postCandidates]
    .filter(Boolean)
    .find((item) => item?.id === postCandidateId);
  return candidate ? { ...candidate, approvalStatus: 'draft' } : null;
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
