import { createEditorNotes, createPostDraft, runEditorialChecks } from '../application/editorialServices';
import { approvePostBrief, normalizePostDraftVersions, type PostDraft, type WorkspaceState } from '../domain/editorialWorkspace';
import { withEditorialWorkItemSync } from './editorialWorkQueueActions';

export function buildApproveBriefWithGeneratedDraftPatch(
  workspace: WorkspaceState,
  generatedDraft: PostDraft
): Partial<WorkspaceState> {
  if (!workspace.postBrief) return {};

  const postBrief = approvePostBrief(workspace.postBrief);
  const postDraft: PostDraft = normalizePostDraftVersions({
    ...generatedDraft,
    id: generatedDraft.id || `draft-${postBrief.id}`,
    briefId: postBrief.id,
    title: generatedDraft.title || postBrief.title,
    status: generatedDraft.status ?? 'draft',
    version: generatedDraft.version || 1,
    updatedAt: generatedDraft.updatedAt || new Date().toISOString()
  });
  const editorialChecks = runEditorialChecks(postDraft, postBrief, workspace.editorialModel);
  const editorNotes = createEditorNotes(editorialChecks);

  return withEditorialWorkItemSync(workspace, {
    postBrief,
    postDraft,
    editorialChecks,
    editorNotes,
    finalText: null,
    postVisual: null,
    releasePackage: null,
    editorialLearningNote: null
  });
}

export function buildApproveBriefWithLocalFallbackDraftPatch(
  workspace: WorkspaceState,
  error: string
): Partial<WorkspaceState> {
  if (!workspace.postBrief) return {};
  const postBrief = approvePostBrief(workspace.postBrief);
  const postDraft: PostDraft = {
    ...createPostDraft(postBrief, workspace.editorialModel),
    generation: {
      source: 'localFallback',
      aiRunId: null,
      provider: null,
      model: null,
      fallbackUsed: true,
      createdAt: new Date().toISOString(),
      error
    }
  };
  return buildApproveBriefWithGeneratedDraftPatch({ ...workspace, postBrief }, postDraft);
}
