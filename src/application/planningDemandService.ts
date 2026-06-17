import { getBroadcastSlotCount, type BroadcastGridDemandSummary, type WorkspaceState } from '../domain/editorialWorkspace';
import { createPostCandidates } from './postCandidateService';

export function summarizeBroadcastGridDemand(
  workspace: WorkspaceState,
  startDate = new Date()
): BroadcastGridDemandSummary {
  const slotCount = getBroadcastSlotCount(workspace.contentPlanSettings, startDate);
  const availableCandidateCount = createPostCandidates(workspace).length;
  const approvedConceptIds = new Set(
    workspace.postCandidates
      .filter((candidate) => candidate.approvalStatus === 'approved')
      .map((candidate) => candidate.id)
  );
  if (workspace.postCandidate?.approvalStatus === 'approved') {
    approvedConceptIds.add(workspace.postCandidate.id);
  }

  const minNeededCandidates = slotCount * workspace.contentPlanSettings.minCandidatesPerSlot;
  const maxUsefulCandidates = slotCount * workspace.contentPlanSettings.maxCandidatesPerSlot;
  const deficit = Math.max(0, minNeededCandidates - availableCandidateCount);
  const surplus = Math.max(0, availableCandidateCount - maxUsefulCandidates);

  return {
    slotCount,
    availableCandidateCount,
    approvedConceptCount: approvedConceptIds.size,
    minNeededCandidates,
    maxUsefulCandidates,
    deficit,
    surplus,
    status: deficit > 0 ? 'deficit' : surplus > 0 ? 'surplus' : 'balanced'
  };
}
