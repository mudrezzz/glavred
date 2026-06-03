export type ApprovalStatus = 'draft' | 'approved' | 'rejected';

export interface EditorialModel {
  author: string;
  audience: string;
  positioning: string;
  fabula: string;
  rubrics: string[];
  styleRules: string[];
  forbiddenTopics: string[];
  goals: string[];
}

export interface SourceSignal {
  id: string;
  type: string;
  title: string;
  source: string;
  capturedAt: string;
  summary: string;
  rawNote: string;
}

export interface InsightCard {
  id: string;
  signalId: string;
  title: string;
  whyItMatters: string;
  audienceRelevance: string;
  authorPosition: string;
  rubric: string;
  urgency: string;
  score: number;
  banalityRisk: number;
  factGaps: string[];
}

export interface ContentPlanItem {
  id: string;
  insightId: string;
  title: string;
  platform: string;
  date: string;
  priority: string;
  format: string;
  expectedEffect: string;
  approvalStatus: ApprovalStatus;
}

export interface PostBrief {
  id: string;
  planItemId: string;
  title: string;
  rubric: string;
  audience: string;
  thesis: string;
  conflict: string;
  authorPosition: string;
  evidence: string[];
  examples: string[];
  structure: string[];
  cta: string;
  risks: string[];
  sources: string[];
  approvalStatus: ApprovalStatus;
}

export interface WorkspaceState {
  editorialModel: EditorialModel;
  sourceSignal: SourceSignal;
  insightCard: InsightCard | null;
  contentPlanItem: ContentPlanItem | null;
  postBrief: PostBrief | null;
  activeSection: WorkspaceSection;
  updatedAt: string;
}

export type WorkspaceSection =
  | 'editorialModel'
  | 'radar'
  | 'plan'
  | 'brief'
  | 'edit'
  | 'release'
  | 'analytics';

export interface WorkspaceStore {
  load(): WorkspaceState;
  save(workspace: WorkspaceState): void;
  reset(): WorkspaceState;
}

export function approvePlanItem(planItem: ContentPlanItem): ContentPlanItem {
  return { ...planItem, approvalStatus: 'approved' };
}

export function rejectPlanItem(planItem: ContentPlanItem): ContentPlanItem {
  return { ...planItem, approvalStatus: 'rejected' };
}

export function approvePostBrief(postBrief: PostBrief): PostBrief {
  return { ...postBrief, approvalStatus: 'approved' };
}

export function rejectPostBrief(postBrief: PostBrief): PostBrief {
  return { ...postBrief, approvalStatus: 'rejected' };
}

