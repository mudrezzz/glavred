import type { ApprovalStatus } from '../shared/types';

// Planning keeps the broadcast grid compatible with the older single-slot flow.
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
  topicId?: string;
  topicTitle?: string;
  fabulaId?: string;
  fabulaTitle?: string;
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
  topicId?: string;
  topicTitle?: string;
  fabulaId?: string;
  fabulaTitle?: string;
  manualOverride?: boolean;
  sourceSignalId?: string;
  weightWarningIds?: string[];
}

export interface ContentPlanSettings {
  postsPerWeek: number;
  planningHorizonDays: number;
  defaultPlatform: string;
  allowedFormats: string[];
}

export interface PlanWeightWarning {
  id: string;
  severity: 'green' | 'yellow' | 'red';
  message: string;
  targetType: 'topic' | 'fabula' | 'slot' | 'matrix';
  targetId: string;
}
