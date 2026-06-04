export type ApprovalStatus = 'draft' | 'approved' | 'rejected';
export type DraftStatus = 'draft' | 'revised';
export type EditorialCheckType = 'style' | 'antiAi' | 'factCheck' | 'policy';
export type EditorialCheckStatus = 'passed' | 'warning' | 'failed';

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

export interface PostDraft {
  id: string;
  briefId: string;
  title: string;
  body: string;
  version: number;
  status: DraftStatus;
  updatedAt: string;
}

export interface EditorialCheck {
  id: string;
  type: EditorialCheckType;
  title: string;
  status: EditorialCheckStatus;
  summary: string;
  findings: string[];
}

export interface EditorNote {
  id: string;
  agent: string;
  tone: string;
  text: string;
  target: string;
}

export interface FinalText {
  id: string;
  draftId: string;
  title: string;
  body: string;
  approvalStatus: ApprovalStatus;
  approvedAt: string;
}

export interface WorkspaceState {
  editorialModel: EditorialModel;
  sourceSignal: SourceSignal;
  insightCard: InsightCard | null;
  contentPlanItem: ContentPlanItem | null;
  postBrief: PostBrief | null;
  postDraft: PostDraft | null;
  editorialChecks: EditorialCheck[];
  editorNotes: EditorNote[];
  finalText: FinalText | null;
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

export function reviseDraft(postDraft: PostDraft, body: string): PostDraft {
  return {
    ...postDraft,
    body,
    version: postDraft.version + 1,
    status: 'revised',
    updatedAt: new Date().toISOString()
  };
}

export function approveFinalText(postDraft: PostDraft): FinalText {
  return {
    id: `final-${postDraft.id}`,
    draftId: postDraft.id,
    title: postDraft.title,
    body: postDraft.body,
    approvalStatus: 'approved',
    approvedAt: new Date().toISOString()
  };
}

export function markCheckResolved(check: EditorialCheck): EditorialCheck {
  return { ...check, status: 'passed' };
}
