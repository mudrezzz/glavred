import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  completeTopicFabulaMatrix,
  createDefaultRadarEditorialFilters,
  evaluateSignalAgainstRadarFilters,
  getValidatorRunScore,
  getValidatorRunStatus,
  normalizeContentPlanSettings,
  normalizeWeightRange,
  summarizeValidatorRun,
  type EditorialValidationRun,
  type RadarDefinition,
  type SourceSignal,
  type WorkspaceSection,
  type WorkspaceState,
  type WorkspaceStore
} from '../domain/editorialWorkspace';
import { normalizeFabulaResearchStrategy } from '../domain/editorial-model/researchStrategy';
import { normalizeFabulaResearchDepth } from '../domain/editorial-model/researchDepth';
import { normalizeFabulaSizeIntent } from '../domain/planning/publicationSize';

const STORAGE_KEY = 'glavred.workspace.v1';

export class LocalWorkspaceStore implements WorkspaceStore {
  constructor(private readonly storage: Storage = window.localStorage) {}

  load(): WorkspaceState {
    const raw = this.storage.getItem(STORAGE_KEY);

    if (!raw) {
      return createDemoWorkspace();
    }

    try {
      return normalizeWorkspace(JSON.parse(raw) as Partial<WorkspaceState>);
    } catch {
      return createDemoWorkspace();
    }
  }

  save(workspace: WorkspaceState): void {
    this.storage.setItem(STORAGE_KEY, JSON.stringify(workspace));
  }

  reset(): WorkspaceState {
    const workspace = createDemoWorkspace();
    this.save(workspace);
    return workspace;
  }
}

export function normalizeWorkspace(saved: Partial<WorkspaceState>): WorkspaceState {
  const demo = createDemoWorkspace();
  const topics = (saved.topics ?? demo.topics).map((topic) => ({
    ...topic,
    weightRange: normalizeWeightRange(topic.weightRange)
  }));
  const fabulas = (saved.fabulas ?? demo.fabulas).map((fabula) => ({
    ...fabula,
    weightRange: normalizeWeightRange(fabula.weightRange),
    sizeIntent: normalizeFabulaSizeIntent(fabula.sizeIntent),
    researchDepth: normalizeFabulaResearchDepth(fabula.researchDepth),
    researchStrategy: normalizeFabulaResearchStrategy(fabula.researchStrategy)
  }));
  const contentPlanItems = (saved.contentPlanItems ?? (saved.contentPlanItem ? [saved.contentPlanItem] : demo.contentPlanItems)).map(
    (item) => ({
      ...item,
      time: item.time ?? demo.contentPlanSettings.publishingTimes[0],
      manualOverride: item.manualOverride ?? false,
      sourceSignalId: item.sourceSignalId ?? saved.sourceSignal?.id ?? demo.sourceSignal.id,
      publicationSizeProfileId: item.publicationSizeProfileId,
      weightWarningIds: item.weightWarningIds ?? []
    })
  );
  const radars = (saved.radars ?? demo.radars).map((radar) => normalizeRadar(radar));
  const sourceSignal = normalizeSourceSignal(saved.sourceSignal ?? demo.sourceSignal, demo.sourceSignal);
  const sourceSignals = (saved.sourceSignals ?? demo.sourceSignals).map((signal) => {
    const normalizedSignal = normalizeSourceSignal(signal, sourceSignal);
    const radar = radars.find((candidate) => candidate.id === normalizedSignal.radarId);
    return radar
      ? evaluateSignalAgainstRadarFilters(normalizedSignal, radar, { ...demo, ...saved, radars } as WorkspaceState)
      : normalizedSignal;
  });
  const activeSection = normalizeWorkspaceSection(saved.activeSection);
  const postCandidates = (saved.postCandidates ?? []).map((candidate) => normalizePostCandidate(candidate));
  const postCandidate = saved.postCandidate ? normalizePostCandidate(saved.postCandidate) : null;
  const editorialWorkItems = (saved.editorialWorkItems ?? []).map((item) => normalizeEditorialWorkItem(item));
  const selectedEditorialWorkItemId = editorialWorkItems.some((item) => item.id === saved.selectedEditorialWorkItemId)
    ? saved.selectedEditorialWorkItemId ?? null
    : null;

  return {
    ...demo,
    ...saved,
    authorNotes: (saved.authorNotes ?? demo.authorNotes).map((note) => ({
      ...note,
      attachments: note.attachments ?? []
    })),
    authorMemoryEvents: saved.authorMemoryEvents ?? demo.authorMemoryEvents,
    authorPositionAssertions: saved.authorPositionAssertions ?? demo.authorPositionAssertions,
    editorialModel: saved.editorialModel ?? demo.editorialModel,
    projectProfile: saved.projectProfile ?? demo.projectProfile,
    editorialRules: saved.editorialRules ?? demo.editorialRules,
    editorialSetupRevision: saved.editorialSetupRevision ?? demo.editorialSetupRevision,
    editorialValidationRun: normalizeEditorialValidationRun(saved.editorialValidationRun),
    topics,
    fabulas,
    topicFabulaMatrix: completeTopicFabulaMatrix(topics, fabulas, saved.topicFabulaMatrix ?? demo.topicFabulaMatrix),
    radars,
    sourceSignal,
    sourceSignals,
    postCandidates,
    postCandidate,
    insightCard: saved.insightCard ?? null,
    contentPlanItem: saved.contentPlanItem ?? null,
    contentPlanItems,
    contentPlanSettings: normalizeContentPlanSettings(saved.contentPlanSettings, demo.contentPlanSettings),
    planWeightWarnings: saved.planWeightWarnings ?? [],
    editorialWorkItems,
    selectedEditorialWorkItemId,
    postBrief: saved.postBrief ?? null,
    postDraft: saved.postDraft ?? null,
    editorialChecks: saved.editorialChecks ?? [],
    editorNotes: saved.editorNotes ?? [],
    finalText: saved.finalText ?? null,
    postVisual: saved.postVisual ? normalizePostVisual(saved.postVisual) : null,
    releasePackage: saved.releasePackage ?? null,
    editorialLearningNote: saved.editorialLearningNote ?? null,
    externalSources: saved.externalSources ?? demo.externalSources,
    importCandidates: saved.importCandidates ?? demo.importCandidates,
    archiveRecords: saved.archiveRecords ?? demo.archiveRecords,
    bulkImportActions: saved.bulkImportActions ?? [],
    activeSection: activeSection ?? demo.activeSection,
    updatedAt: saved.updatedAt ?? demo.updatedAt
  };
}

function normalizePostCandidate(candidate: WorkspaceState['postCandidates'][number]): WorkspaceState['postCandidates'][number] {
  const { format: _legacyFormat, ...current } = candidate as WorkspaceState['postCandidates'][number] & { format?: string };
  return current;
}

type StoredEditorialWorkItem = Omit<WorkspaceState['editorialWorkItems'][number], 'stage'> & {
  stage?: string;
};

function normalizeEditorialWorkItem(item: StoredEditorialWorkItem): WorkspaceState['editorialWorkItems'][number] {
  const stage = item.stage === 'final' ? 'visual' : item.stage ?? 'brief';

  return {
    ...item,
    stage: stage as WorkspaceState['editorialWorkItems'][number]['stage'],
    status: item.status ?? 'todo',
    brief: item.brief ?? null,
    draft: item.draft ?? null,
    editorialChecks: item.editorialChecks ?? [],
    editorNotes: item.editorNotes ?? [],
    finalText: item.finalText ?? null,
    visual: item.visual ? normalizePostVisual(item.visual) : null
  };
}

function normalizePostVisual(visual: NonNullable<WorkspaceState['postVisual']>): NonNullable<WorkspaceState['postVisual']> {
  return {
    ...visual,
    memeReferences: visual.memeReferences ?? [],
    selectedMemeReferenceId: visual.selectedMemeReferenceId ?? null,
    memeReferenceBatch: visual.memeReferenceBatch ?? 0,
    variants: visual.variants ?? [],
    selectedVariantId: visual.selectedVariantId ?? null,
    variantBatch: visual.variantBatch ?? 0
  };
}

function normalizeSourceSignal(signal: SourceSignal, fallback: SourceSignal): SourceSignal {
  return {
    ...fallback,
    ...signal,
    evidence: signal.evidence ?? fallback.evidence ?? [
      {
        id: `evidence-${signal.id}`,
        sourceTitle: signal.source ?? fallback.source,
        sourceUrl: '',
        quote: signal.summary ?? fallback.summary,
        summary: signal.rawNote ?? fallback.rawNote
      }
    ],
    searchNote: signal.searchNote ?? fallback.searchNote ?? '',
    radarId: signal.radarId ?? fallback.radarId,
    reviewStatus: signal.reviewStatus ?? fallback.reviewStatus ?? 'new',
    suggestedTopicId: signal.suggestedTopicId ?? fallback.suggestedTopicId,
    suggestedFabulaId: signal.suggestedFabulaId ?? fallback.suggestedFabulaId,
    suggestedValue: signal.suggestedValue ?? fallback.suggestedValue ?? '',
    duplicateRisk: signal.duplicateRisk ?? fallback.duplicateRisk ?? 'low',
    authorCorrection: signal.authorCorrection ?? fallback.authorCorrection ?? '',
    filterEvaluations: signal.filterEvaluations ?? fallback.filterEvaluations ?? [],
    filterStatus: signal.filterStatus ?? fallback.filterStatus ?? 'passed'
  };
}

function normalizeRadar(radar: RadarDefinition): RadarDefinition {
  const sourceDiscoveryMode =
    radar.sourceDiscoveryMode ??
    (radar.sources && radar.sources.length > 0 ? 'specifiedAndAdditional' : 'autonomous');
  return {
    ...radar,
    sourceDiscoveryMode,
    filters: radar.filters ?? createDefaultRadarEditorialFilters(radar.id, []),
    rules: radar.rules ?? [
      {
        id: `rule-${radar.id}`,
        operator: 'and',
        negate: false,
        statement: radar.scope,
        status: 'active'
      }
    ],
    sources: radar.sources ?? []
  };
}

function normalizeWorkspaceSection(section: WorkspaceSection | 'radar' | undefined): WorkspaceSection | undefined {
  if (section === 'radar') return 'signals';
  return section;
}

function normalizeEditorialValidationRun(
  run: Partial<EditorialValidationRun> | null | undefined
): EditorialValidationRun | null {
  if (!run) return null;

  const results = run.results ?? [];
  const validatorRun = {
    id: run.id ?? `validator-run-${Date.now()}`,
    revision: run.revision ?? 0,
    checkedAt: run.checkedAt ?? new Date().toISOString(),
    results
  };
  const summary = run.summary ?? summarizeValidatorRun(validatorRun);

  return {
    ...validatorRun,
    aggregateStatus: run.aggregateStatus ?? summary.status ?? getValidatorRunStatus(results),
    aggregateScore: run.aggregateScore ?? getValidatorRunScore(results),
    summary
  };
}
