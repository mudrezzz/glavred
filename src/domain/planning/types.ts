import type { ApprovalStatus } from '../shared/types';
import type { PublicationSizeProfile } from './publicationSize';

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
  channelId?: string;
  date: string;
  time: string;
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
  publicationSizeProfileId?: string;
  weightWarningIds?: string[];
}

export type PlanningPeriod = 'week' | 'month' | 'quarter';
export type SignalSelectionPolicy = 'hitl-only' | 'automatic' | 'automatic-with-review';

export interface ContentPlanSettings {
  period: PlanningPeriod;
  postsPerWeek: number;
  planningHorizonDays: number;
  publishingDays: number[];
  publishingTimes: string[];
  publishSlots: PublishSlot[];
  minCandidatesPerSlot: number;
  maxCandidatesPerSlot: number;
  defaultPlatform: string;
  defaultChannelId?: string;
  signalSelectionPolicy: SignalSelectionPolicy;
  publicationSizeProfiles: PublicationSizeProfile[];
  defaultPublicationSizeProfileId: string;
  publicationSizeDefaultsVersion: number;
}

export interface PlanWeightWarning {
  id: string;
  severity: 'green' | 'yellow' | 'red';
  message: string;
  targetType: 'topic' | 'fabula' | 'slot' | 'matrix';
  targetId: string;
}

export interface PublishWindow {
  date: string;
  time: string;
}

export interface PublishSlot {
  date: string;
  time: string;
}

export interface BroadcastGridDemandSummary {
  slotCount: number;
  availableCandidateCount: number;
  approvedConceptCount: number;
  minNeededCandidates: number;
  maxUsefulCandidates: number;
  deficit: number;
  surplus: number;
  status: 'deficit' | 'balanced' | 'surplus';
}
