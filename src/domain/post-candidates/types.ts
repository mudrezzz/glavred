import type { ApprovalStatus } from '../shared/types';

export interface PostCandidate {
  id: string;
  sourceSignalId: string;
  topicId: string;
  fabulaId: string;
  audience: string;
  value: string;
  goal: string;
  platform: string;
  format: string;
  title: string;
  thesis: string;
  evidenceSummary: string;
  confidence: number;
  risks: string[];
  approvalStatus: ApprovalStatus;
}
