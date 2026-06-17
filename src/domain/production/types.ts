import type { ApprovalStatus, DraftStatus } from '../shared/types';

// Production artifacts keep the downstream HITL flow from brief to learning note.
export type EditorialCheckType = 'style' | 'antiAi' | 'factCheck' | 'policy';
export type EditorialCheckStatus = 'passed' | 'warning' | 'failed';
export type ReleaseStatus = 'draft' | 'ready' | 'exported';
export type ReleaseTarget = 'telegram' | 'linkedin';
export type AnalyticsStatus = 'draft' | 'captured';
export type EditorialWorkStage = 'brief' | 'draft' | 'final' | 'readyForRelease';
export type EditorialWorkStatus = 'todo' | 'inProgress' | 'approved' | 'blocked';

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
  topicId?: string;
  topicTitle?: string;
  fabulaId?: string;
  fabulaTitle?: string;
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

export interface EditorialWorkItem {
  id: string;
  contentPlanItemId: string;
  postCandidateId?: string;
  sourceSignalId?: string;
  title: string;
  platform: string;
  date: string;
  time: string;
  topicId?: string;
  topicTitle?: string;
  fabulaId?: string;
  fabulaTitle?: string;
  stage: EditorialWorkStage;
  status: EditorialWorkStatus;
  brief: PostBrief | null;
  draft: PostDraft | null;
  editorialChecks: EditorialCheck[];
  editorNotes: EditorNote[];
  finalText: FinalText | null;
}

export interface ReleaseChecklistItem {
  id: string;
  label: string;
  done: boolean;
}

export interface ReleasePackage {
  id: string;
  finalTextId: string;
  targets: ReleaseTarget[];
  markdown: string;
  checklist: ReleaseChecklistItem[];
  status: ReleaseStatus;
  updatedAt: string;
}

export interface ManualMetricSnapshot {
  views: number;
  reactions: number;
  comments: number;
  saves: number;
  leads: number;
}

export interface EditorialLearningNote {
  id: string;
  releasePackageId: string;
  metricSnapshot: ManualMetricSnapshot;
  observedResult: string;
  audienceReaction: string;
  workingTheses: string;
  trustRubrics: string;
  qualityAudienceTopics: string;
  strongerVoice: string;
  repeatFormats: string;
  seriesCandidates: string;
  status: AnalyticsStatus;
  updatedAt: string;
  capturedAt: string | null;
}
