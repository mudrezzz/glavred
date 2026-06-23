import type { AuthorPositionAssertion } from '../author-memory/types';
import type { FabulaResearchStrategy } from './researchStrategy';
import type { FabulaSizeIntent } from '../planning/publicationSize';
import type { EditorialEntityStatus, WeightRange } from '../shared/types';

// Editorial model contains structured rules and catalogs that validate future posts.
export type EditorialSetupStatus = 'draft' | 'needsReview' | 'validated';
export type EditorialRuleGroup =
  | 'author'
  | 'audience'
  | 'positioning'
  | 'styleVoice'
  | 'styleLanguage'
  | 'styleRhythm'
  | 'antiAiPattern'
  | 'goal'
  | 'forbiddenTopic';
export type ValidatorStatus = 'green' | 'yellow' | 'red';
export type EditorialValidationStatus = ValidatorStatus;
export type ValidatorTargetType =
  | 'projectProfile'
  | 'editorialRule'
  | 'authorPositionAssertion'
  | 'topic'
  | 'fabula'
  | 'topicFabulaMatrix'
  | 'editorialSetup';
export type ValidatorSuggestionSeverity = 'info' | 'warning' | 'critical';

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

export interface ProjectProfile {
  name: string;
  description: string;
  setupStatus: EditorialSetupStatus;
}

export interface EditorialRule {
  id: string;
  group: EditorialRuleGroup;
  title: string;
  statement: string;
  status: EditorialEntityStatus;
  evidenceNoteId?: string;
}

export interface EditorialValidationItem {
  id: string;
  status: EditorialValidationStatus;
  title: string;
  summary: string;
  recommendation: string;
}

export interface EditorialValidationSummary {
  status: EditorialValidationStatus;
  title: string;
  summary: string;
  items: EditorialValidationItem[];
}

export interface ValidatorEvidence {
  id: string;
  type: string;
  title: string;
  quote: string;
  sourceId: string;
  reason: string;
}

export interface ValidatorSuggestion {
  id: string;
  title: string;
  description: string;
  severity: ValidatorSuggestionSeverity;
}

export interface ValidatorDefinition {
  id: string;
  title: string;
  description: string;
  targetTypes: ValidatorTargetType[];
}

export interface ValidatorResult {
  id: string;
  validatorId: string;
  targetType: ValidatorTargetType;
  targetId: string;
  status: ValidatorStatus;
  score: number;
  summary: string;
  evidence: ValidatorEvidence[];
  suggestions: ValidatorSuggestion[];
}

export interface ValidatorRun {
  id: string;
  revision: number;
  checkedAt: string;
  results: ValidatorResult[];
}

export interface EditorialValidationRun {
  id: string;
  revision: number;
  checkedAt: string;
  results: ValidatorResult[];
  aggregateStatus: ValidatorStatus;
  aggregateScore: number;
  summary: EditorialValidationSummary;
}

export interface Topic {
  id: string;
  title: string;
  description: string;
  purpose: string;
  audienceValue: string;
  authorStance: string;
  rules: string[];
  forbiddenAngles: string[];
  weightRange: WeightRange;
  status: EditorialEntityStatus;
}

export interface Fabula {
  id: string;
  title: string;
  description: string;
  dramaturgy: string;
  structure: string[];
  proofRequirements: string[];
  rules: string[];
  weightRange: WeightRange;
  sizeIntent: FabulaSizeIntent;
  researchStrategy: FabulaResearchStrategy;
  status: EditorialEntityStatus;
}

export interface TopicFabulaMatrixEntry {
  topicId: string;
  fabulaId: string;
  enabled: boolean;
}

export interface TopicFabulaWarning {
  targetType: 'topic' | 'fabula';
  targetId: string;
  title: string;
  message: string;
}

export interface CompatibleTopicFabula {
  topic: Topic;
  fabula: Fabula;
}

export type EditorialValidationContext = {
  assertions: AuthorPositionAssertion[];
  rules: EditorialRule[];
  topics: Topic[];
  fabulas: Fabula[];
  matrix: TopicFabulaMatrixEntry[];
};
