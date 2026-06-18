import {
  createBroadcastPlan,
  createWorkspaceInsightCard
} from '../application/editorialServices';
import {
  applyPlanWarnings,
  detectBroadcastPlanConflicts,
  normalizeContentPlanSettings,
  updateContentPlanItem,
  type ContentPlanItem,
  type ContentPlanSettings,
  type WorkspaceState
} from '../domain/editorialWorkspace';

export function buildAddInsightToPlanPatch(workspace: WorkspaceState): Partial<WorkspaceState> {
  const insightCard = workspace.insightCard ?? createWorkspaceInsightCard(workspace);
  const nextWorkspace = { ...workspace, insightCard };
  const generatedItems = createBroadcastPlan(nextWorkspace);
  const planWeightWarnings = detectBroadcastPlanConflicts(nextWorkspace, generatedItems);
  const contentPlanItems = applyPlanWarnings(generatedItems, planWeightWarnings);

  return { insightCard, contentPlanItems, planWeightWarnings, contentPlanItem: null, activeSection: 'plan' };
}

export function buildGenerateBroadcastPlanPatch(workspace: WorkspaceState): Partial<WorkspaceState> {
  const insightCard = workspace.insightCard ?? createWorkspaceInsightCard(workspace);
  const nextWorkspace = { ...workspace, insightCard };
  const generatedItems = createBroadcastPlan(nextWorkspace);
  const planWeightWarnings = detectBroadcastPlanConflicts(nextWorkspace, generatedItems);
  const contentPlanItems = applyPlanWarnings(generatedItems, planWeightWarnings);

  return { insightCard, contentPlanItems, planWeightWarnings, contentPlanItem: null };
}

export function buildSaveContentPlanSettingsPatch(
  workspace: WorkspaceState,
  contentPlanSettings: ContentPlanSettings
): Partial<WorkspaceState> {
  return {
    contentPlanSettings: normalizeContentPlanSettings(contentPlanSettings, workspace.contentPlanSettings),
    contentPlanItems: [],
    contentPlanItem: null,
    planWeightWarnings: [],
    editorialWorkItems: [],
    selectedEditorialWorkItemId: null,
    postBrief: null,
    postDraft: null,
    editorialChecks: [],
    editorNotes: [],
    finalText: null,
    postVisual: null,
    releasePackage: null,
    editorialLearningNote: null
  };
}

export function buildUpdatePlanItemPatch(
  workspace: WorkspaceState,
  item: ContentPlanItem
): Partial<WorkspaceState> {
  const updatedItems = updateContentPlanItem(workspace.contentPlanItems, item);
  const planWeightWarnings = detectBroadcastPlanConflicts(workspace, updatedItems);
  const contentPlanItems = applyPlanWarnings(updatedItems, planWeightWarnings);

  return { contentPlanItems, planWeightWarnings };
}
