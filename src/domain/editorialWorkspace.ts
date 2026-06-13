export type ApprovalStatus = 'draft' | 'approved' | 'rejected';
export type DraftStatus = 'draft' | 'revised';
export type EditorialCheckType = 'style' | 'antiAi' | 'factCheck' | 'policy';
export type EditorialCheckStatus = 'passed' | 'warning' | 'failed';
export type ReleaseStatus = 'draft' | 'ready' | 'exported';
export type ReleaseTarget = 'telegram' | 'linkedin';
export type AnalyticsStatus = 'draft' | 'captured';
export type AuthorNoteType = 'thought' | 'linkReaction' | 'manualCorrection';
export type AuthorPositionAssertionType = 'persona' | 'style' | 'audience' | 'topic' | 'principle';
export type AuthorPositionAssertionStatus = 'inferred' | 'confirmed';
export type ExternalSourceType =
  | 'telegramChannel'
  | 'socialProfile'
  | 'blogSite'
  | 'document'
  | 'articleArchive'
  | 'manualUpload';
export type ExternalSourceStatus = 'planned' | 'connected' | 'needsReview' | 'imported' | 'paused' | 'failed';
export type ImportMode = 'manualOnly' | 'reviewedQueue' | 'archiveOnly' | 'bulkArchive';
export type EvidencePolicy = 'canSupportAssertions' | 'archiveOnly' | 'ignored';
export type ImportReviewStatus =
  | 'new'
  | 'acceptedToMemory'
  | 'acceptedToArchive'
  | 'bulkAcceptedToArchive'
  | 'rejected'
  | 'ignoredForEvidence';
export type ImportCandidateGroupType = 'source' | 'status' | 'duplicateRisk' | 'evidencePolicy' | 'tag';
export type ImportRiskLevel = 'low' | 'medium' | 'high';
export type BulkImportActionType = 'bulkAcceptToArchive' | 'bulkReject';
export type EditorialEntityStatus = 'active' | 'paused';
export type EditorialSetupStatus = 'draft' | 'needsReview' | 'validated';
export type RadarSourceType = 'authorMemory' | 'archive' | 'externalSource' | 'manualResearch';
export type RadarAcceptancePolicy = 'manual' | 'automatic' | 'automaticWithReview';
export type RadarTriggerMode = 'scheduled' | 'manual' | 'deficitDriven';
export type RadarStatus = 'active' | 'paused' | 'needsReview';
export type SignalReviewStatus = 'new' | 'approved' | 'rejected' | 'archived' | 'corrected';
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

export interface AuthorNote {
  id: string;
  type: AuthorNoteType;
  title: string;
  body: string;
  sourceUrl: string;
  tags: string[];
  attachments: AuthorAttachment[];
  capturedAt: string;
  targetType?: 'assertion' | 'evidence';
  targetId?: string;
  targetTitle?: string;
}

export interface AuthorAttachment {
  id: string;
  fileName: string;
  mimeType: string;
  sizeBytes: number;
  dataUrl: string;
  createdAt: string;
  localOnly: boolean;
}

export interface AuthorMemoryEvent {
  id: string;
  noteId: string;
  type: AuthorNoteType;
  summary: string;
  detectedSignals: string[];
  createdAt: string;
}

export interface EvidenceLink {
  noteId: string;
  quote: string;
  reason: string;
}

export interface AuthorPositionAssertion {
  id: string;
  type: AuthorPositionAssertionType;
  title: string;
  statement: string;
  confidence: number;
  evidence: EvidenceLink[];
  status: AuthorPositionAssertionStatus;
}

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

export interface WeightRange {
  min: number;
  max: number;
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

export interface RadarDefinition {
  id: string;
  title: string;
  sourceType: RadarSourceType;
  scope: string;
  acceptancePolicy: RadarAcceptancePolicy;
  triggerMode: RadarTriggerMode;
  status: RadarStatus;
  lastRunAt: string;
  notes: string;
}

export interface SourceSignal {
  id: string;
  type: string;
  title: string;
  source: string;
  capturedAt: string;
  summary: string;
  rawNote: string;
  radarId?: string;
  reviewStatus?: SignalReviewStatus;
  suggestedTopicId?: string;
  suggestedFabulaId?: string;
  suggestedValue?: string;
  duplicateRisk?: ImportRiskLevel;
  authorCorrection?: string;
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

export interface AuthorExternalSource {
  id: string;
  type: ExternalSourceType;
  title: string;
  url: string;
  fileReference: string;
  status: ExternalSourceStatus;
  importMode: ImportMode;
  lastCheckedAt: string;
  lastImportedAt: string;
  notes: string;
}

export interface ImportedMemoryCandidate {
  id: string;
  sourceId: string;
  title: string;
  excerpt: string;
  originalUrl: string;
  capturedAt: string;
  detectedTags: string[];
  duplicateRisk: ImportRiskLevel;
  suggestedTarget: string;
  reviewStatus: ImportReviewStatus;
  evidencePolicy: EvidencePolicy;
}

export interface ImportCandidateGroup {
  id: string;
  type: ImportCandidateGroupType;
  title: string;
  candidateIds: string[];
  summary: string;
  riskLevel: ImportRiskLevel;
}

export interface BulkImportAction {
  id: string;
  action: BulkImportActionType;
  candidateIds: string[];
  previousStatuses: Record<string, ImportReviewStatus>;
  createdAt: string;
  canUndo: boolean;
  createdArchiveRecordIds: string[];
}

export interface ArchiveRecord {
  id: string;
  sourceId: string;
  title: string;
  bodyExcerpt: string;
  originalUrl: string;
  publishedAt: string;
  acceptedAt: string;
  acceptanceMode: 'manual' | 'bulk';
  evidencePolicy: EvidencePolicy;
}

export interface ImportCandidateFilters {
  sourceId?: string;
  reviewStatus?: ImportReviewStatus | 'all';
  evidencePolicy?: EvidencePolicy | 'all';
  duplicateRisk?: ImportRiskLevel | 'all';
  query?: string;
}

export interface WorkspaceState {
  authorNotes: AuthorNote[];
  authorMemoryEvents: AuthorMemoryEvent[];
  authorPositionAssertions: AuthorPositionAssertion[];
  editorialModel: EditorialModel;
  projectProfile: ProjectProfile;
  editorialRules: EditorialRule[];
  editorialSetupRevision: number;
  editorialValidationRun: EditorialValidationRun | null;
  topics: Topic[];
  fabulas: Fabula[];
  topicFabulaMatrix: TopicFabulaMatrixEntry[];
  radars: RadarDefinition[];
  sourceSignal: SourceSignal;
  sourceSignals: SourceSignal[];
  insightCard: InsightCard | null;
  contentPlanItem: ContentPlanItem | null;
  contentPlanItems: ContentPlanItem[];
  contentPlanSettings: ContentPlanSettings;
  planWeightWarnings: PlanWeightWarning[];
  postBrief: PostBrief | null;
  postDraft: PostDraft | null;
  editorialChecks: EditorialCheck[];
  editorNotes: EditorNote[];
  finalText: FinalText | null;
  releasePackage: ReleasePackage | null;
  editorialLearningNote: EditorialLearningNote | null;
  externalSources: AuthorExternalSource[];
  importCandidates: ImportedMemoryCandidate[];
  archiveRecords: ArchiveRecord[];
  bulkImportActions: BulkImportAction[];
  activeSection: WorkspaceSection;
  updatedAt: string;
}

export type WorkspaceSection =
  | 'memory'
  | 'editorialModel'
  | 'signals'
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

export function getRulesByGroup(rules: EditorialRule[], group: EditorialRuleGroup): EditorialRule[] {
  return rules.filter((rule) => rule.group === group);
}

export function createEditorialRule(
  group: EditorialRuleGroup,
  title: string,
  statement: string
): EditorialRule {
  return {
    id: `rule-${group}-${Date.now()}`,
    group,
    title,
    statement,
    status: 'active'
  };
}

export function updateEditorialRule(rules: EditorialRule[], rule: EditorialRule): EditorialRule[] {
  return rules.map((item) => (item.id === rule.id ? rule : item));
}

export function deleteEditorialRule(rules: EditorialRule[], ruleId: string): EditorialRule[] {
  return rules.filter((rule) => rule.id !== ruleId);
}

export function validateEditorialSetupLegacy(workspace: WorkspaceState): EditorialValidationSummary {
  const warnings = getTopicFabulaWarnings(workspace.topics, workspace.fabulas, workspace.topicFabulaMatrix);
  const activeRules = workspace.editorialRules.filter((rule) => rule.status === 'active');
  const antiAiRules = getRulesByGroup(activeRules, 'antiAiPattern');
  const goalRules = getRulesByGroup(activeRules, 'goal');
  const styleRules = [
    ...getRulesByGroup(activeRules, 'styleVoice'),
    ...getRulesByGroup(activeRules, 'styleLanguage'),
    ...getRulesByGroup(activeRules, 'styleRhythm')
  ];
  const items: EditorialValidationItem[] = [
    {
      id: 'validation-project-profile',
      status: workspace.projectProfile.name.trim() && workspace.projectProfile.description.trim() ? 'green' : 'yellow',
      title: 'Профиль проекта',
      summary: workspace.projectProfile.name.trim()
        ? `Проект задан как "${workspace.projectProfile.name}".`
        : 'У проекта нет явного названия.',
      recommendation: workspace.projectProfile.name.trim()
        ? 'Использовать название как верхний контекст редакционного кабинета.'
        : 'Добавить название проекта перед настройкой правил.'
    },
    {
      id: 'validation-editorial-rules',
      status: activeRules.length >= 10 ? 'green' : 'yellow',
      title: 'Атомарные правила',
      summary: `${activeRules.length} активных правил описывают издательство.`,
      recommendation:
        activeRules.length >= 10
          ? 'Правил достаточно для первого deterministic review.'
          : 'Добавить правила автора, аудитории, позиции, стиля и целей.'
    },
    {
      id: 'validation-style-anti-ai',
      status: antiAiRules.length > 0 && styleRules.length >= 3 ? 'green' : 'yellow',
      title: 'Стиль и anti-AI',
      summary: `${styleRules.length} style rules, ${antiAiRules.length} anti-AI rules.`,
      recommendation:
        antiAiRules.length > 0
          ? 'Anti-AI правила можно использовать в будущем валидаторе редакторского тона.'
          : 'Добавить хотя бы одно правило против стерильного AI-текста.'
    },
    {
      id: 'validation-topic-fabula-matrix',
      status: warnings.length === 0 ? 'green' : 'red',
      title: 'Матрица тем и фабул',
      summary: warnings.length === 0 ? 'Все активные сущности имеют связки.' : `${warnings.length} сущностей без связок.`,
      recommendation:
        warnings.length === 0
          ? 'Матрица пригодна для планирования.'
          : 'Вернуть хотя бы одну совместимую связку для каждой активной темы и фабулы.'
    },
    {
      id: 'validation-goal-fit',
      status: goalRules.length > 0 ? 'yellow' : 'red',
      title: 'Цели блога',
      summary: goalRules.length > 0 ? `${goalRules.length} целей заданы как правила.` : 'Цели не заданы.',
      recommendation:
        'Следующий слой должен сверить цели с образом автора, аудиторией, темами и будущими метриками.'
    }
  ];
  const status: EditorialValidationStatus = items.some((item) => item.status === 'red')
    ? 'red'
    : items.some((item) => item.status === 'yellow')
      ? 'yellow'
      : 'green';

  return {
    status,
    title: status === 'green' ? 'Редакционная модель согласована' : 'Редакционная модель требует внимания',
    summary:
      'Проверка deterministic: оценивает профиль проекта, атомарность правил, стиль, anti-AI слой, цели и матрицу совместимости.',
    items
  };
}

export function runEditorialSetupValidators(workspace: WorkspaceState): ValidatorRun {
  const results = [
    validateAuthorPositionClarity(workspace),
    validateAntiAiStyleCoverage(workspace),
    validateAudienceValueFit(workspace),
    validateGoalConsistency(workspace),
    validateTopicFabulaCoverage(workspace)
  ];

  return {
    id: `validator-run-${Date.now()}`,
    revision: workspace.editorialSetupRevision ?? 0,
    checkedAt: new Date().toISOString(),
    results
  };
}

export function createEditorialValidationRun(
  workspace: WorkspaceState,
  checkedAt = new Date().toISOString()
): EditorialValidationRun {
  const run = runEditorialSetupValidators(workspace);
  const normalizedRun = { ...run, checkedAt };
  const aggregateStatus = getValidatorRunStatus(normalizedRun.results);
  const aggregateScore = getValidatorRunScore(normalizedRun.results);

  return {
    ...normalizedRun,
    aggregateStatus,
    aggregateScore,
    summary: summarizeValidatorRun(normalizedRun)
  };
}

export function validateEditorialSetup(workspace: WorkspaceState): EditorialValidationSummary {
  return summarizeValidatorRun(runEditorialSetupValidators(workspace));
}

export function summarizeValidatorRun(run: ValidatorRun): EditorialValidationSummary {
  const status = getValidatorRunStatus(run.results);
  const aggregateScore = getValidatorRunScore(run.results);

  return {
    status,
    title: status === 'green' ? 'Редакционная модель согласована' : 'Редакционная модель требует внимания',
    summary: `Проверено ${run.results.length} валидаторов. Средний score: ${Math.round(aggregateScore * 100)}%.`,
    items: run.results.map((result) => ({
      id: result.id,
      status: result.status,
      title: validatorDefinitionTitle(result.validatorId),
      summary: result.summary,
      recommendation: result.suggestions[0]?.description ?? 'Критичных рекомендаций нет.'
    }))
  };
}

export function getValidatorRunStatus(results: ValidatorResult[]): ValidatorStatus {
  if (results.some((result) => result.status === 'red')) return 'red';
  if (results.some((result) => result.status === 'yellow')) return 'yellow';
  return 'green';
}

export function getValidatorRunScore(results: ValidatorResult[]): number {
  if (results.length === 0) return 0;

  return Math.round((results.reduce((sum, result) => sum + result.score, 0) / results.length) * 100) / 100;
}

export function validatorDefinitionTitle(validatorId: string): string {
  return VALIDATOR_DEFINITIONS.find((definition) => definition.id === validatorId)?.title ?? validatorId;
}

export const VALIDATOR_DEFINITIONS: ValidatorDefinition[] = [
  {
    id: 'author-position-clarity',
    title: 'Позиция автора',
    description: 'Проверяет, есть ли ясная авторская позиция и evidence из авторской памяти.',
    targetTypes: ['authorPositionAssertion', 'editorialSetup']
  },
  {
    id: 'anti-ai-style-coverage',
    title: 'Стиль и anti-AI слой',
    description: 'Проверяет, что стиль задан правилами и есть защита от стерильного AI-текста.',
    targetTypes: ['editorialRule', 'editorialSetup']
  },
  {
    id: 'audience-value-fit',
    title: 'Ценность для аудитории',
    description: 'Проверяет связь тем и правил с пользой для AI PM, founders и product leaders.',
    targetTypes: ['editorialRule', 'topic', 'editorialSetup']
  },
  {
    id: 'goal-consistency',
    title: 'Согласованность целей',
    description: 'Проверяет, что цели блога поддержаны автором, аудиторией, темами и будущими метриками.',
    targetTypes: ['projectProfile', 'editorialRule', 'topic', 'editorialSetup']
  },
  {
    id: 'topic-fabula-coverage',
    title: 'Покрытие тем и фабул',
    description: 'Проверяет, что активные темы и фабулы имеют связи в матрице.',
    targetTypes: ['topic', 'fabula', 'topicFabulaMatrix']
  }
];

function validateAuthorPositionClarity(workspace: WorkspaceState): ValidatorResult {
  const assertionsWithEvidence = workspace.authorPositionAssertions.filter((assertion) => assertion.evidence.length > 0);
  const status: ValidatorStatus =
    assertionsWithEvidence.length >= 3 ? 'green' : assertionsWithEvidence.length > 0 ? 'yellow' : 'red';
  const evidence = assertionsWithEvidence.slice(0, 3).map((assertion, index) => ({
    id: `author-position-evidence-${index + 1}`,
    type: assertion.type,
    title: assertion.title,
    quote: assertion.evidence[0]?.quote ?? assertion.statement,
    sourceId: assertion.evidence[0]?.noteId ?? assertion.id,
    reason: assertion.evidence[0]?.reason ?? 'Вывод о позиции автора уже зафиксирован в памяти.'
  }));

  return {
    id: 'validator-author-position-clarity',
    validatorId: 'author-position-clarity',
    targetType: 'authorPositionAssertion',
    targetId: 'author-position',
    status,
    score: status === 'green' ? 0.92 : status === 'yellow' ? 0.62 : 0.2,
    summary:
      status === 'green'
        ? 'Авторская позиция читается через несколько подтвержденных выводов из памяти.'
        : status === 'yellow'
          ? 'Позиция автора есть, но evidence пока недостаточно для уверенной настройки издательства.'
          : 'Позиция автора не подтверждена заметками и правками.',
    evidence,
    suggestions:
      status === 'green'
        ? []
        : [
            {
              id: 'author-position-add-evidence',
              title: 'Добавить evidence из памяти',
              description: 'Зафиксируйте еще несколько мыслей или корректировок, которые объясняют отношение автора к AI-B2B продуктам.',
              severity: status === 'red' ? 'critical' : 'warning'
            }
          ]
  };
}

function validateAntiAiStyleCoverage(workspace: WorkspaceState): ValidatorResult {
  const activeRules = workspace.editorialRules.filter((rule) => rule.status === 'active');
  const antiAiRules = getRulesByGroup(activeRules, 'antiAiPattern');
  const styleRules = [
    ...getRulesByGroup(activeRules, 'styleVoice'),
    ...getRulesByGroup(activeRules, 'styleLanguage'),
    ...getRulesByGroup(activeRules, 'styleRhythm')
  ];
  const status: ValidatorStatus =
    antiAiRules.length > 0 && styleRules.length >= 3
      ? 'green'
      : antiAiRules.length > 0 || styleRules.length >= 2
        ? 'yellow'
        : 'red';
  const evidenceRules = [...antiAiRules, ...styleRules].slice(0, 4);

  return {
    id: 'validator-anti-ai-style-coverage',
    validatorId: 'anti-ai-style-coverage',
    targetType: 'editorialRule',
    targetId: 'style-rules',
    status,
    score: status === 'green' ? 0.88 : status === 'yellow' ? 0.58 : 0.28,
    summary: `${styleRules.length} style rules, ${antiAiRules.length} anti-AI rules.`,
    evidence: evidenceRules.map((rule) => ({
      id: `style-evidence-${rule.id}`,
      type: rule.group,
      title: rule.title,
      quote: rule.statement,
      sourceId: rule.id,
      reason: 'Правило будет использоваться как проверяемое ограничение для будущих драфтов.'
    })),
    suggestions:
      antiAiRules.length > 0
        ? [
            {
              id: 'anti-ai-expand',
              title: 'Развить anti-AI паттерны',
              description: 'Добавьте запреты на пустые вводные, универсальные советы и стерильный тон, чтобы валидатор мог ловить больше типовых AI-приемов.',
              severity: 'info'
            }
          ]
        : [
            {
              id: 'anti-ai-missing',
              title: 'Добавить anti-AI правила',
              description: 'Сейчас стиль не защищен от стерильного AI-текста. Нужны отдельные правила против обобщений и псевдоэкспертной подачи.',
              severity: 'critical'
            }
          ]
  };
}

function validateAudienceValueFit(workspace: WorkspaceState): ValidatorResult {
  const audienceRules = getRulesByGroup(
    workspace.editorialRules.filter((rule) => rule.status === 'active'),
    'audience'
  );
  const activeTopics = workspace.topics.filter((topic) => topic.status === 'active');
  const topicsWithValue = activeTopics.filter((topic) => topic.audienceValue.trim().length > 0);
  const status: ValidatorStatus =
    audienceRules.length > 0 && topicsWithValue.length === activeTopics.length
      ? 'green'
      : topicsWithValue.length > 0
        ? 'yellow'
        : 'red';

  return {
    id: 'validator-audience-value-fit',
    validatorId: 'audience-value-fit',
    targetType: 'topic',
    targetId: 'audience-value',
    status,
    score: status === 'green' ? 0.86 : status === 'yellow' ? 0.6 : 0.25,
    summary: `${topicsWithValue.length} из ${activeTopics.length} активных тем объясняют ценность для аудитории.`,
    evidence: [
      ...audienceRules.slice(0, 2).map((rule) => ({
        id: `audience-rule-${rule.id}`,
        type: rule.group,
        title: rule.title,
        quote: rule.statement,
        sourceId: rule.id,
        reason: 'Правило описывает, кому и зачем нужен блог.'
      })),
      ...topicsWithValue.slice(0, 2).map((topic) => ({
        id: `audience-topic-${topic.id}`,
        type: 'topic',
        title: topic.title,
        quote: topic.audienceValue,
        sourceId: topic.id,
        reason: 'Тема содержит явную ценность для читателя.'
      }))
    ],
    suggestions:
      status === 'green'
        ? []
        : [
            {
              id: 'audience-value-fill-gaps',
              title: 'Дописать ценность тем',
              description: 'У каждой активной темы должна быть проверяемая польза для AI PM, founders или product leaders.',
              severity: status === 'red' ? 'critical' : 'warning'
            }
          ]
  };
}

function validateGoalConsistency(workspace: WorkspaceState): ValidatorResult {
  const activeRules = workspace.editorialRules.filter((rule) => rule.status === 'active');
  const goalRules = getRulesByGroup(activeRules, 'goal');
  const authorRules = getRulesByGroup(activeRules, 'author');
  const audienceRules = getRulesByGroup(activeRules, 'audience');
  const hasSupportingContext = authorRules.length > 0 && audienceRules.length > 0 && workspace.topics.some((topic) => topic.status === 'active');
  const status: ValidatorStatus =
    goalRules.length > 0 && hasSupportingContext ? 'yellow' : goalRules.length > 0 ? 'yellow' : 'red';

  return {
    id: 'validator-goal-consistency',
    validatorId: 'goal-consistency',
    targetType: 'editorialSetup',
    targetId: 'goals',
    status,
    score: status === 'yellow' && hasSupportingContext ? 0.68 : status === 'yellow' ? 0.52 : 0.2,
    summary:
      goalRules.length > 0
        ? 'Цели заданы и поддержаны настройками издательства, но пока не декомпозированы в метрики.'
        : 'Цели блога не заданы как валидируемые правила.',
    evidence: goalRules.slice(0, 3).map((rule) => ({
      id: `goal-evidence-${rule.id}`,
      type: rule.group,
      title: rule.title,
      quote: rule.statement,
      sourceId: rule.id,
      reason: 'Цель участвует в проверке согласованности издательства.'
    })),
    suggestions: [
      {
        id: 'goal-add-metrics',
        title: 'Декомпозировать цель в метрики',
        description: 'Следующий слой должен связать цель блога с метриками: подписки, сохранения, входящие запросы, лиды и качество аудитории.',
        severity: goalRules.length > 0 ? 'warning' : 'critical'
      }
    ]
  };
}

function validateTopicFabulaCoverage(workspace: WorkspaceState): ValidatorResult {
  const warnings = getTopicFabulaWarnings(workspace.topics, workspace.fabulas, workspace.topicFabulaMatrix);
  const status: ValidatorStatus = warnings.length === 0 ? 'green' : 'red';

  return {
    id: 'validator-topic-fabula-coverage',
    validatorId: 'topic-fabula-coverage',
    targetType: 'topicFabulaMatrix',
    targetId: 'topic-fabula-matrix',
    status,
    score: status === 'green' ? 0.94 : Math.max(0.2, 1 - warnings.length / 5),
    summary:
      warnings.length === 0
        ? 'Все активные темы и фабулы имеют хотя бы одну совместимую связку.'
        : `${warnings.length} активных сущностей потеряли связи в матрице.`,
    evidence:
      warnings.length > 0
        ? warnings.map((warning) => ({
            id: `matrix-warning-${warning.targetType}-${warning.targetId}`,
            type: warning.targetType,
            title: warning.title,
            quote: warning.message,
            sourceId: warning.targetId,
            reason: 'Без связи сущность не попадет в контент-план.'
          }))
        : [
            {
              id: 'matrix-coverage-ok',
              type: 'topicFabulaMatrix',
              title: 'Матрица совместимости',
              quote: `${workspace.topics.length} тем, ${workspace.fabulas.length} фабул, ${workspace.topicFabulaMatrix.filter((entry) => entry.enabled).length} активных связей.`,
              sourceId: 'topic-fabula-matrix',
              reason: 'Матрица пригодна для планирования первого контент-потока.'
            }
          ],
    suggestions:
      warnings.length === 0
        ? []
        : [
            {
              id: 'matrix-restore-links',
              title: 'Вернуть совместимые связки',
              description: 'Включите хотя бы одну фабулу для каждой активной темы и хотя бы одну тему для каждой активной фабулы.',
              severity: 'critical'
            }
          ]
  };
}

export function normalizeWeightRange(range: WeightRange): WeightRange {
  const min = clampPercent(range.min);
  const max = clampPercent(range.max);

  return min <= max ? { min, max } : { min: max, max: min };
}

export function createTopicDraft(): Topic {
  return {
    id: `topic-custom-${Date.now()}`,
    title: '',
    description: '',
    purpose: '',
    audienceValue: '',
    authorStance: '',
    rules: [],
    forbiddenAngles: [],
    weightRange: { min: 5, max: 15 },
    status: 'active'
  };
}

export function createFabulaDraft(): Fabula {
  return {
    id: `fabula-custom-${Date.now()}`,
    title: '',
    description: '',
    dramaturgy: '',
    structure: [],
    proofRequirements: [],
    rules: [],
    weightRange: { min: 5, max: 15 },
    status: 'active'
  };
}

export function addTopic(topics: Topic[], topic: Topic): Topic[] {
  return [...topics, { ...topic, weightRange: normalizeWeightRange(topic.weightRange) }];
}

export function addFabula(fabulas: Fabula[], fabula: Fabula): Fabula[] {
  return [...fabulas, { ...fabula, weightRange: normalizeWeightRange(fabula.weightRange) }];
}

export function deleteTopic(
  topics: Topic[],
  matrix: TopicFabulaMatrixEntry[],
  topicId: string
): { topics: Topic[]; matrix: TopicFabulaMatrixEntry[] } {
  return {
    topics: topics.filter((topic) => topic.id !== topicId),
    matrix: matrix.filter((entry) => entry.topicId !== topicId)
  };
}

export function deleteFabula(
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[],
  fabulaId: string
): { fabulas: Fabula[]; matrix: TopicFabulaMatrixEntry[] } {
  return {
    fabulas: fabulas.filter((fabula) => fabula.id !== fabulaId),
    matrix: matrix.filter((entry) => entry.fabulaId !== fabulaId)
  };
}

export function createDefaultTopicFabulaMatrix(
  topics: Topic[],
  fabulas: Fabula[]
): TopicFabulaMatrixEntry[] {
  return topics.flatMap((topic) =>
    fabulas.map((fabula) => ({
      topicId: topic.id,
      fabulaId: fabula.id,
      enabled: true
    }))
  );
}

export function completeTopicFabulaMatrix(
  topics: Topic[],
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[]
): TopicFabulaMatrixEntry[] {
  const existing = new Map(matrix.map((entry) => [`${entry.topicId}:${entry.fabulaId}`, entry.enabled]));

  return topics.flatMap((topic) =>
    fabulas.map((fabula) => {
      const key = `${topic.id}:${fabula.id}`;

      return {
        topicId: topic.id,
        fabulaId: fabula.id,
        enabled: existing.get(key) ?? true
      };
    })
  );
}

export function isTopicFabulaEnabled(
  matrix: TopicFabulaMatrixEntry[],
  topicId: string,
  fabulaId: string
): boolean {
  return matrix.find((entry) => entry.topicId === topicId && entry.fabulaId === fabulaId)?.enabled ?? true;
}

export function selectCompatibleTopicFabula(
  topics: Topic[],
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[]
): CompatibleTopicFabula | null {
  const activeTopics = topics.filter((topic) => topic.status === 'active');
  const activeFabulas = fabulas.filter((fabula) => fabula.status === 'active');

  for (const topic of activeTopics) {
    const fabula = activeFabulas.find((item) => isTopicFabulaEnabled(matrix, topic.id, item.id));

    if (fabula) {
      return { topic, fabula };
    }
  }

  return null;
}

export function getTopicFabulaWarnings(
  topics: Topic[],
  fabulas: Fabula[],
  matrix: TopicFabulaMatrixEntry[]
): TopicFabulaWarning[] {
  const activeTopics = topics.filter((topic) => topic.status === 'active');
  const activeFabulas = fabulas.filter((fabula) => fabula.status === 'active');
  const topicWarnings = activeTopics
    .filter((topic) => !activeFabulas.some((fabula) => isTopicFabulaEnabled(matrix, topic.id, fabula.id)))
    .map((topic) => ({
      targetType: 'topic' as const,
      targetId: topic.id,
      title: topic.title,
      message: 'У темы нет активных фабул. Она не попадет в план, пока матрица не включит хотя бы одну связку.'
    }));
  const fabulaWarnings = activeFabulas
    .filter((fabula) => !activeTopics.some((topic) => isTopicFabulaEnabled(matrix, topic.id, fabula.id)))
    .map((fabula) => ({
      targetType: 'fabula' as const,
      targetId: fabula.id,
      title: fabula.title,
      message: 'Фабула не применима ни к одной активной теме. Она не будет использоваться в планировании.'
    }));

  return [...topicWarnings, ...fabulaWarnings];
}

export function approvePlanItem(planItem: ContentPlanItem): ContentPlanItem {
  return { ...planItem, approvalStatus: 'approved' };
}

export function rejectPlanItem(planItem: ContentPlanItem): ContentPlanItem {
  return { ...planItem, approvalStatus: 'rejected' };
}

export function approveSignal(signal: SourceSignal): SourceSignal {
  return { ...signal, reviewStatus: 'approved' };
}

export function rejectSignal(signal: SourceSignal): SourceSignal {
  return { ...signal, reviewStatus: 'rejected' };
}

export function archiveSignal(signal: SourceSignal): SourceSignal {
  return { ...signal, reviewStatus: 'archived' };
}

export function correctSignal(signal: SourceSignal, patch: Partial<SourceSignal>): SourceSignal {
  return {
    ...signal,
    ...patch,
    reviewStatus: 'corrected',
    authorCorrection:
      patch.authorCorrection ??
      signal.authorCorrection ??
      'Автор скорректировал связку сигнала с темой, фабулой или ценностью.'
  };
}

export function updateContentPlanItem(
  items: ContentPlanItem[],
  updatedItem: ContentPlanItem
): ContentPlanItem[] {
  return items.map((item) => (item.id === updatedItem.id ? updatedItem : item));
}

export function approveContentPlanSlot(items: ContentPlanItem[], itemId: string): ContentPlanItem[] {
  return items.map((item) =>
    item.id === itemId ? approvePlanItem(item) : item
  );
}

export function applyPlanWarnings(
  items: ContentPlanItem[],
  warnings: PlanWeightWarning[]
): ContentPlanItem[] {
  return items.map((item) => ({
    ...item,
    weightWarningIds: warnings
      .filter((warning) => warning.targetType === 'slot' && warning.targetId === item.id)
      .map((warning) => warning.id)
  }));
}

export function detectBroadcastPlanConflicts(
  workspace: Pick<WorkspaceState, 'topics' | 'fabulas' | 'topicFabulaMatrix'>,
  items: ContentPlanItem[]
): PlanWeightWarning[] {
  const activeItems = items.filter((item) => item.approvalStatus !== 'rejected');
  const warnings: PlanWeightWarning[] = [];
  const topicUsage = usageShare(activeItems, (item) => item.topicId);
  const fabulaUsage = usageShare(activeItems, (item) => item.fabulaId);

  activeItems.forEach((item) => {
    if (!item.date || !item.platform || !item.format || !item.topicId || !item.fabulaId) {
      warnings.push({
        id: `slot-incomplete-${item.id}`,
        severity: 'red',
        targetType: 'slot',
        targetId: item.id,
        message: 'Слот неполный: нужны дата, площадка, формат, тема и фабула.'
      });
    }

    const topic = workspace.topics.find((candidate) => candidate.id === item.topicId);
    const fabula = workspace.fabulas.find((candidate) => candidate.id === item.fabulaId);

    if (topic?.status === 'paused') {
      warnings.push({
        id: `slot-paused-topic-${item.id}`,
        severity: 'yellow',
        targetType: 'slot',
        targetId: item.id,
        message: `Слот использует тему "${topic.title}", которая сейчас на паузе.`
      });
    }

    if (fabula?.status === 'paused') {
      warnings.push({
        id: `slot-paused-fabula-${item.id}`,
        severity: 'yellow',
        targetType: 'slot',
        targetId: item.id,
        message: `Слот использует фабулу "${fabula.title}", которая сейчас на паузе.`
      });
    }

    if (item.topicId && item.fabulaId && !isTopicFabulaEnabled(workspace.topicFabulaMatrix, item.topicId, item.fabulaId)) {
      warnings.push({
        id: `slot-matrix-${item.id}`,
        severity: 'red',
        targetType: 'slot',
        targetId: item.id,
        message: 'Тема и фабула не включены в матрице совместимости.'
      });
    }
  });

  workspace.topics
    .filter((topic) => topic.status === 'active')
    .forEach((topic) => {
      const share = topicUsage.get(topic.id) ?? 0;
      if (share < topic.weightRange.min || share > topic.weightRange.max) {
        warnings.push({
          id: `topic-weight-${topic.id}`,
          severity: share === 0 ? 'red' : 'yellow',
          targetType: 'topic',
          targetId: topic.id,
          message: `Тема "${topic.title}" занимает ${Math.round(share)}% сетки при диапазоне ${topic.weightRange.min}-${topic.weightRange.max}%.`
        });
      }
    });

  workspace.fabulas
    .filter((fabula) => fabula.status === 'active')
    .forEach((fabula) => {
      const share = fabulaUsage.get(fabula.id) ?? 0;
      if (share < fabula.weightRange.min || share > fabula.weightRange.max) {
        warnings.push({
          id: `fabula-weight-${fabula.id}`,
          severity: share === 0 ? 'red' : 'yellow',
          targetType: 'fabula',
          targetId: fabula.id,
          message: `Фабула "${fabula.title}" занимает ${Math.round(share)}% сетки при диапазоне ${fabula.weightRange.min}-${fabula.weightRange.max}%.`
        });
      }
    });

  return warnings;
}

function usageShare(items: ContentPlanItem[], getId: (item: ContentPlanItem) => string | undefined): Map<string, number> {
  const counts = new Map<string, number>();
  const total = Math.max(items.length, 1);
  items.forEach((item) => {
    const id = getId(item);
    if (!id) return;
    counts.set(id, (counts.get(id) ?? 0) + 1);
  });
  return new Map(Array.from(counts.entries()).map(([id, count]) => [id, (count / total) * 100]));
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

export function toggleReleaseChecklistItem(
  releasePackage: ReleasePackage,
  itemId: string
): ReleasePackage {
  return {
    ...releasePackage,
    checklist: releasePackage.checklist.map((item) =>
      item.id === itemId ? { ...item, done: !item.done } : item
    ),
    status: 'draft',
    updatedAt: new Date().toISOString()
  };
}

export function markReleaseReady(releasePackage: ReleasePackage): ReleasePackage {
  const allItemsDone = releasePackage.checklist.every((item) => item.done);

  if (!allItemsDone) {
    return { ...releasePackage, status: 'draft', updatedAt: new Date().toISOString() };
  }

  return { ...releasePackage, status: 'ready', updatedAt: new Date().toISOString() };
}

export function markReleaseExported(releasePackage: ReleasePackage): ReleasePackage {
  return { ...releasePackage, status: 'exported', updatedAt: new Date().toISOString() };
}

export function markLearningNoteCaptured(note: EditorialLearningNote): EditorialLearningNote {
  const now = new Date().toISOString();

  return {
    ...note,
    status: 'captured',
    updatedAt: now,
    capturedAt: now
  };
}

export function updateLearningNote(
  note: EditorialLearningNote,
  patch: Partial<Omit<EditorialLearningNote, 'id' | 'releasePackageId' | 'updatedAt' | 'capturedAt'>>
): EditorialLearningNote {
  return {
    ...note,
    ...patch,
    status: 'draft',
    updatedAt: new Date().toISOString(),
    capturedAt: null
  };
}

export function acceptCandidateToMemory(
  candidate: ImportedMemoryCandidate,
  source: AuthorExternalSource
): AuthorNote {
  return {
    id: `note-import-${candidate.id}`,
    type: 'linkReaction',
    title: candidate.title,
    body: candidate.excerpt,
    sourceUrl: candidate.originalUrl || source.url,
    tags: Array.from(new Set([...candidate.detectedTags, 'imported'])),
    attachments: [],
    capturedAt: new Date().toISOString()
  };
}

export function markCandidateAcceptedToMemory(
  candidate: ImportedMemoryCandidate
): ImportedMemoryCandidate {
  return {
    ...candidate,
    reviewStatus: 'acceptedToMemory',
    evidencePolicy: 'canSupportAssertions'
  };
}

export function acceptCandidateToArchive(
  candidate: ImportedMemoryCandidate,
  _source: AuthorExternalSource,
  mode: 'manual' | 'bulk' = 'manual'
): ArchiveRecord {
  return {
    id: `archive-${candidate.id}`,
    sourceId: candidate.sourceId,
    title: candidate.title,
    bodyExcerpt: candidate.excerpt,
    originalUrl: candidate.originalUrl,
    publishedAt: candidate.capturedAt,
    acceptedAt: new Date().toISOString(),
    acceptanceMode: mode,
    evidencePolicy: mode === 'bulk' ? 'archiveOnly' : candidate.evidencePolicy
  };
}

export function markCandidateAcceptedToArchive(
  candidate: ImportedMemoryCandidate,
  mode: 'manual' | 'bulk' = 'manual'
): ImportedMemoryCandidate {
  return {
    ...candidate,
    reviewStatus: mode === 'bulk' ? 'bulkAcceptedToArchive' : 'acceptedToArchive',
    evidencePolicy: 'archiveOnly'
  };
}

export function rejectCandidate(candidate: ImportedMemoryCandidate): ImportedMemoryCandidate {
  return {
    ...candidate,
    reviewStatus: 'rejected',
    evidencePolicy: 'ignored'
  };
}

export function ignoreCandidateForEvidence(candidate: ImportedMemoryCandidate): ImportedMemoryCandidate {
  return {
    ...candidate,
    reviewStatus: 'ignoredForEvidence',
    evidencePolicy: 'ignored'
  };
}

export function bulkAcceptCandidatesToArchive(
  candidates: ImportedMemoryCandidate[],
  sources: AuthorExternalSource[]
): {
  candidates: ImportedMemoryCandidate[];
  archiveRecords: ArchiveRecord[];
  action: BulkImportAction;
} {
  const sourceById = new Map(sources.map((source) => [source.id, source]));
  const changedCandidates = candidates.map((candidate) => markCandidateAcceptedToArchive(candidate, 'bulk'));
  const archiveRecords = candidates.map((candidate) =>
    acceptCandidateToArchive(
      candidate,
      sourceById.get(candidate.sourceId) ?? {
        id: candidate.sourceId,
        type: 'manualUpload',
        title: candidate.sourceId,
        url: '',
        fileReference: '',
        status: 'planned',
        importMode: 'archiveOnly',
        lastCheckedAt: '',
        lastImportedAt: '',
        notes: ''
      },
      'bulk'
    )
  );

  return {
    candidates: changedCandidates,
    archiveRecords,
    action: {
      id: `bulk-archive-${Date.now()}`,
      action: 'bulkAcceptToArchive',
      candidateIds: candidates.map((candidate) => candidate.id),
      previousStatuses: Object.fromEntries(candidates.map((candidate) => [candidate.id, candidate.reviewStatus])),
      createdAt: new Date().toISOString(),
      canUndo: true,
      createdArchiveRecordIds: archiveRecords.map((record) => record.id)
    }
  };
}

export function bulkRejectCandidates(candidates: ImportedMemoryCandidate[]): {
  candidates: ImportedMemoryCandidate[];
  action: BulkImportAction;
} {
  return {
    candidates: candidates.map(rejectCandidate),
    action: {
      id: `bulk-reject-${Date.now()}`,
      action: 'bulkReject',
      candidateIds: candidates.map((candidate) => candidate.id),
      previousStatuses: Object.fromEntries(candidates.map((candidate) => [candidate.id, candidate.reviewStatus])),
      createdAt: new Date().toISOString(),
      canUndo: true,
      createdArchiveRecordIds: []
    }
  };
}

export function undoLastBulkImportAction(workspace: WorkspaceState): WorkspaceState {
  const lastAction = [...workspace.bulkImportActions].reverse().find((action) => action.canUndo);

  if (!lastAction) {
    return workspace;
  }

  return {
    ...workspace,
    importCandidates: workspace.importCandidates.map((candidate) =>
      lastAction.previousStatuses[candidate.id]
        ? { ...candidate, reviewStatus: lastAction.previousStatuses[candidate.id] }
        : candidate
    ),
    archiveRecords: workspace.archiveRecords.filter(
      (record) => !lastAction.createdArchiveRecordIds.includes(record.id)
    ),
    bulkImportActions: workspace.bulkImportActions.filter((action) => action.id !== lastAction.id)
  };
}

export function filterImportCandidates(
  candidates: ImportedMemoryCandidate[],
  filters: ImportCandidateFilters
): ImportedMemoryCandidate[] {
  const query = filters.query?.trim().toLowerCase() ?? '';

  return candidates.filter((candidate) => {
    const matchesSource = !filters.sourceId || filters.sourceId === 'all' || candidate.sourceId === filters.sourceId;
    const matchesStatus =
      !filters.reviewStatus || filters.reviewStatus === 'all' || candidate.reviewStatus === filters.reviewStatus;
    const matchesPolicy =
      !filters.evidencePolicy ||
      filters.evidencePolicy === 'all' ||
      candidate.evidencePolicy === filters.evidencePolicy;
    const matchesRisk =
      !filters.duplicateRisk || filters.duplicateRisk === 'all' || candidate.duplicateRisk === filters.duplicateRisk;
    const haystack = [
      candidate.title,
      candidate.excerpt,
      candidate.originalUrl,
      candidate.suggestedTarget,
      ...candidate.detectedTags
    ]
      .join(' ')
      .toLowerCase();

    return matchesSource && matchesStatus && matchesPolicy && matchesRisk && (!query || haystack.includes(query));
  });
}

export function groupImportCandidates(
  candidates: ImportedMemoryCandidate[],
  mode: ImportCandidateGroupType = 'source'
): ImportCandidateGroup[] {
  const grouped = candidates.reduce<Record<string, ImportedMemoryCandidate[]>>((groups, candidate) => {
    const key =
      mode === 'source'
        ? candidate.sourceId
        : mode === 'status'
          ? candidate.reviewStatus
          : mode === 'duplicateRisk'
            ? candidate.duplicateRisk
            : mode === 'evidencePolicy'
              ? candidate.evidencePolicy
              : candidate.detectedTags[0] ?? 'untagged';

    return {
      ...groups,
      [key]: [...(groups[key] ?? []), candidate]
    };
  }, {});

  return Object.entries(grouped).map(([key, items]) => ({
    id: `${mode}-${key}`,
    type: mode,
    title: key,
    candidateIds: items.map((item) => item.id),
    summary: `${items.length} candidates`,
    riskLevel: items.some((item) => item.duplicateRisk === 'high')
      ? 'high'
      : items.some((item) => item.duplicateRisk === 'medium')
        ? 'medium'
      : 'low'
  }));
}

function clampPercent(value: number): number {
  if (!Number.isFinite(value)) {
    return 0;
  }

  return Math.max(0, Math.min(100, Math.round(value)));
}
