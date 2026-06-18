import {
  approvePostCandidate,
  editPostCandidate,
  rejectPostCandidate,
  replacePostCandidate,
  type PostCandidate,
  type PostCandidateEditPatch,
  type WorkspaceState
} from '../domain/editorialWorkspace';

export function buildApproveCandidatePatch(
  current: WorkspaceState,
  candidate: PostCandidate
): Partial<WorkspaceState> {
  const postCandidate = approvePostCandidate(candidate);
  const sourceSignal =
    current.sourceSignals.find((signal) => signal.id === postCandidate.sourceSignalId) ?? current.sourceSignal;
  const currentList = current.postCandidates.length > 0 ? current.postCandidates : [candidate];

  return {
    sourceSignal,
    postCandidates: replacePostCandidate(currentList, postCandidate),
    postCandidate,
    insightCard: null,
    contentPlanItem: null,
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

export function buildRejectCandidatePatch(
  current: WorkspaceState,
  candidate: PostCandidate
): Partial<WorkspaceState> {
  const postCandidate = rejectPostCandidate(candidate);
  const selectedCandidate = current.postCandidate?.id === postCandidate.id ? null : current.postCandidate;

  return {
    postCandidates: replacePostCandidate(current.postCandidates, postCandidate),
    postCandidate: selectedCandidate
  };
}

export function buildEditCandidatePatch(
  current: WorkspaceState,
  candidate: PostCandidate,
  patch: PostCandidateEditPatch
): Partial<WorkspaceState> {
  const postCandidate = editPostCandidate(candidate, patch);
  const selectedCandidate = current.postCandidate?.id === postCandidate.id ? postCandidate : current.postCandidate;

  return {
    postCandidates: replacePostCandidate(current.postCandidates, postCandidate),
    postCandidate: selectedCandidate
  };
}
