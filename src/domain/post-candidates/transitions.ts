import type { PostCandidate } from './types';

export type PostCandidateEditPatch = Pick<
  PostCandidate,
  'fabulaId' | 'title' | 'thesis' | 'audience' | 'value' | 'goal' | 'platform' | 'evidenceSummary' | 'risks'
>;

export function approvePostCandidate(candidate: PostCandidate): PostCandidate {
  if (candidate.approvalStatus === 'rejected') return candidate;
  return { ...candidate, approvalStatus: 'approved' };
}

export function editPostCandidate(candidate: PostCandidate, patch: PostCandidateEditPatch): PostCandidate {
  return {
    ...candidate,
    ...patch,
    approvalStatus: candidate.approvalStatus === 'approved' ? 'approved' : 'draft'
  };
}

export function rejectPostCandidate(candidate: PostCandidate): PostCandidate {
  return { ...candidate, approvalStatus: 'rejected' };
}

export function replacePostCandidate(
  candidates: PostCandidate[],
  candidate: PostCandidate
): PostCandidate[] {
  return candidates.some((item) => item.id === candidate.id)
    ? candidates.map((item) => (item.id === candidate.id ? candidate : item))
    : [candidate, ...candidates];
}
