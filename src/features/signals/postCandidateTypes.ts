import type { PostCandidate } from '../../domain/editorialWorkspace';

export type CandidateViewMode = 'list' | 'groups';
export type CandidateGroupMode = 'signal' | 'topic' | 'status' | 'risk';
export type CandidateRiskLevel = 'high' | 'medium' | 'low';

export type PostCandidateFilters = {
  signalId: string;
  status: 'all' | PostCandidate['approvalStatus'];
  topicId: string;
  risk: 'all' | 'withRisks' | CandidateRiskLevel;
  query: string;
};

export type PostCandidateGroup = {
  id: string;
  title: string;
  candidates: PostCandidate[];
};
