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
export type EditorialValidationStatus = 'green' | 'yellow' | 'red';

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

export interface EditorialValidationRun {
  id: string;
  revision: number;
  checkedAt: string;
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
  sourceSignal: SourceSignal;
  insightCard: InsightCard | null;
  contentPlanItem: ContentPlanItem | null;
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

export function validateEditorialSetup(workspace: WorkspaceState): EditorialValidationSummary {
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
