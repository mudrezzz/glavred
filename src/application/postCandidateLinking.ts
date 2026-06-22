import type { ContentPlanItem, PostCandidate, WorkspaceState } from '../domain/editorialWorkspace';

type WorkItem = WorkspaceState['editorialWorkItems'][number];

export function findLinkedPostCandidate(
  workspace: WorkspaceState,
  workItem: WorkItem | null,
  planSlot: ContentPlanItem | null,
  onProblem?: (entity: string, id: string | null, reason: string) => void
): PostCandidate | null {
  const explicitId = workItem?.postCandidateId;
  if (explicitId) return findById(workspace, explicitId, onProblem);

  if (workspace.postCandidate) return workspace.postCandidate;

  const insightCandidate = findByInsightId(workspace, planSlot?.insightId);
  if (insightCandidate) return insightCandidate;

  const exact = approvedCandidates(workspace).filter(
    (candidate) =>
      candidate.sourceSignalId === (workItem?.sourceSignalId ?? planSlot?.sourceSignalId) &&
      candidate.topicId === (workItem?.topicId ?? planSlot?.topicId) &&
      candidate.fabulaId === (workItem?.fabulaId ?? planSlot?.fabulaId)
  );
  if (exact.length === 1) return exact[0];
  if (exact.length > 1) {
    onProblem?.('postCandidate', null, 'Multiple approved candidates match source signal, topic and fabula');
    return null;
  }

  const signalId = workItem?.sourceSignalId ?? planSlot?.sourceSignalId;
  const bySignal = approvedCandidates(workspace).filter((candidate) => candidate.sourceSignalId === signalId);
  if (bySignal.length === 1) return bySignal[0];
  if (bySignal.length > 1) {
    onProblem?.('postCandidate', null, 'Multiple approved candidates match source signal');
  }
  return null;
}

function findById(
  workspace: WorkspaceState,
  candidateId: string,
  onProblem?: (entity: string, id: string | null, reason: string) => void
): PostCandidate | null {
  const candidate =
    workspace.postCandidates.find((item) => item.id === candidateId) ??
    (workspace.postCandidate?.id === candidateId ? workspace.postCandidate : null);
  if (!candidate) onProblem?.('postCandidate', candidateId, 'Post candidate was not found');
  return candidate;
}

function findByInsightId(workspace: WorkspaceState, insightId: string | undefined): PostCandidate | null {
  const candidateId = insightId?.startsWith('insight-') ? insightId.replace(/^insight-/, '') : '';
  if (!candidateId) return null;
  return workspace.postCandidates.find((item) => item.id === candidateId) ?? null;
}

function approvedCandidates(workspace: WorkspaceState): PostCandidate[] {
  return [workspace.postCandidate, ...workspace.postCandidates]
    .filter((candidate): candidate is PostCandidate => Boolean(candidate))
    .filter((candidate, index, candidates) => candidates.findIndex((item) => item.id === candidate.id) === index)
    .filter((candidate) => candidate.approvalStatus === 'approved');
}
