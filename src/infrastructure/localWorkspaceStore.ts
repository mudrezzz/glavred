import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  completeTopicFabulaMatrix,
  createDefaultRadarEditorialFilters,
  getValidatorRunScore,
  getValidatorRunStatus,
  normalizeContentPlanSettings,
  normalizeFoundMaterials,
  normalizeRadarRuns,
  normalizeSourceRegistry,
  normalizePostDraftVersions,
  normalizeWeightRange,
  attachRadarSourceHandles,
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
import {
  PUBLICATION_PLATFORM_LABELS,
  applyPublicationChannelToPlanItem,
  applyPublicationChannelToSettings,
  createPublicationChannel,
  normalizePublicationChannels,
  resolveDefaultPublicationChannel,
  resolvePlanItemPublicationChannel
} from '../domain/publication-channels/transitions';
import {
  deriveEditorialModelSummary,
  synthesizeEditorialRulesFromModel
} from '../domain/editorial-contract/summary';

const STORAGE_KEY = 'glavred.workspace.v1';

export class LocalWorkspaceStore implements WorkspaceStore {
  constructor(private readonly storage: Storage = window.localStorage) {}

  load(): WorkspaceState {
    const raw = this.storage.getItem(STORAGE_KEY);

    if (!raw) {
      return createDemoWorkspace({ includeSeededHitlLearning: true });
    }

    try {
      return normalizeWorkspace(JSON.parse(raw) as Partial<WorkspaceState>);
    } catch {
      return createDemoWorkspace({ includeSeededHitlLearning: true });
    }
  }

  save(workspace: WorkspaceState): void {
    this.storage.setItem(STORAGE_KEY, JSON.stringify(workspace));
  }

  reset(): WorkspaceState {
    const workspace = createDemoWorkspace({ includeSeededHitlLearning: true });
    this.save(workspace);
    return workspace;
  }
}

export function normalizeWorkspace(saved: Partial<WorkspaceState>): WorkspaceState {
  const demo = createDemoWorkspace();
  const baseEditorialModel = saved.editorialModel ?? demo.editorialModel;
  const baseEditorialRules = saved.editorialRules ??
    (saved.editorialModel ? [] : demo.editorialRules);
  const editorialRules = synthesizeEditorialRulesFromModel(baseEditorialModel, baseEditorialRules);
  const editorialModel = deriveEditorialModelSummary(baseEditorialModel, editorialRules);
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
  let baseContentPlanSettings = normalizeContentPlanSettings(saved.contentPlanSettings, demo.contentPlanSettings);
  if (!saved.contentPlanSettings?.defaultChannelId && saved.contentPlanSettings?.defaultPlatform) {
    baseContentPlanSettings = { ...baseContentPlanSettings, defaultChannelId: undefined };
  }
  let publicationChannels = normalizePublicationChannels(
    saved.publicationChannels,
    baseContentPlanSettings.defaultPlatform,
    (saved.projectProfile ?? demo.projectProfile).name === 'AI Design Patterns' ? 'en' : 'ru',
    baseContentPlanSettings.defaultPublicationSizeProfileId
  );
  if (!baseContentPlanSettings.defaultChannelId && !hasChannelLabel(publicationChannels, baseContentPlanSettings.defaultPlatform)) {
    publicationChannels = [
      createPublicationChannel({
        id: `channel-${baseContentPlanSettings.defaultPlatform.toLowerCase().replace(/[^a-z0-9а-яё]+/gi, '-')}`,
        title: baseContentPlanSettings.defaultPlatform,
        language: (saved.projectProfile ?? demo.projectProfile).name === 'AI Design Patterns' ? 'en' : 'ru',
        defaultPublicationSizeProfileId: baseContentPlanSettings.defaultPublicationSizeProfileId
      }),
      ...publicationChannels
    ];
  }
  const contentPlanSettings = applyPublicationChannelToSettings(
    baseContentPlanSettings,
    resolveDefaultPublicationChannel(baseContentPlanSettings, publicationChannels)
  );
  const contentPlanItems = (saved.contentPlanItems ?? (saved.contentPlanItem ? [saved.contentPlanItem] : demo.contentPlanItems)).map(
    (item) => {
      const normalizedItem = {
        ...item,
        time: item.time ?? demo.contentPlanSettings.publishingTimes[0],
        manualOverride: item.manualOverride ?? false,
        sourceSignalId: item.sourceSignalId ?? saved.sourceSignal?.id ?? demo.sourceSignal.id,
        publicationSizeProfileId: item.publicationSizeProfileId,
        weightWarningIds: item.weightWarningIds ?? []
      };
      const channel = resolvePlanItemPublicationChannel(normalizedItem, publicationChannels);
      return channel ? applyPublicationChannelToPlanItem(normalizedItem, channel) : normalizedItem;
    }
  );
  const baseRadars = (saved.radars ?? demo.radars).map((radar) => normalizeRadar(radar));
  const authorNotes = (saved.authorNotes ?? demo.authorNotes).map((note) => normalizeAuthorNote(note));
  const externalSources = saved.externalSources ?? demo.externalSources;
  const importCandidates = saved.importCandidates ?? demo.importCandidates;
  const archiveRecords = saved.archiveRecords ?? demo.archiveRecords;
  const sourceRegistry = normalizeSourceRegistry(saved.sourceRegistry ?? demo.sourceRegistry, {
    radars: baseRadars,
    externalSources,
    authorNotes,
    archiveRecords,
    importCandidates,
    updatedAt: saved.updatedAt ?? demo.updatedAt
  });
  const radars = baseRadars.map((radar) => attachRadarSourceHandles(radar, sourceRegistry));
  const demoSignalsById = new Map(demo.sourceSignals.map((signal) => [signal.id, signal]));
  const selectedSignalSource = saved.sourceSignal ?? demo.sourceSignal;
  const sourceSignal = normalizeSourceSignal(
    selectedSignalSource,
    demoSignalsById.get(selectedSignalSource.id) ?? selectedSignalSource
  );
  const sourceSignals = removeCrossRunSignalContamination(
    (saved.sourceSignals ?? demo.sourceSignals).map((signal) =>
      normalizeSourceSignal(signal, demoSignalsById.get(signal.id) ?? signal)
    ),
    saved.radarRuns ?? demo.radarRuns
  );
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
    authorNotes,
    authorMemoryEvents: saved.authorMemoryEvents ?? demo.authorMemoryEvents,
    authorPositionAssertions: saved.authorPositionAssertions ?? demo.authorPositionAssertions,
    editorialModel,
    projectProfile: saved.projectProfile ?? demo.projectProfile,
    editorialRules,
    editorialSetupRevision: saved.editorialSetupRevision ?? demo.editorialSetupRevision,
    editorialValidationRun: normalizeEditorialValidationRun(saved.editorialValidationRun),
    topics,
    fabulas,
    topicFabulaMatrix: completeTopicFabulaMatrix(topics, fabulas, saved.topicFabulaMatrix ?? demo.topicFabulaMatrix),
    sourceRegistry,
    radarRuns: normalizeRadarRuns(saved.radarRuns ?? demo.radarRuns, sourceRegistry),
    foundMaterials: normalizeFoundMaterials(saved.foundMaterials ?? demo.foundMaterials, sourceRegistry),
    radars,
    sourceSignal,
    sourceSignals,
    postCandidates,
    postCandidate,
    insightCard: saved.insightCard ?? null,
    contentPlanItem: saved.contentPlanItem ?? null,
    contentPlanItems,
    contentPlanSettings,
    publicationChannels,
    planWeightWarnings: saved.planWeightWarnings ?? [],
    editorialWorkItems,
    selectedEditorialWorkItemId,
    postBrief: saved.postBrief ?? null,
    postDraft: saved.postDraft ? normalizePostDraftVersions(saved.postDraft) : null,
    editorialChecks: saved.editorialChecks ?? [],
    editorNotes: saved.editorNotes ?? [],
    finalText: saved.finalText ?? null,
    postVisual: saved.postVisual ? normalizePostVisual(saved.postVisual) : null,
    releasePackage: saved.releasePackage ?? null,
    editorialLearningNote: saved.editorialLearningNote ?? null,
    externalSources,
    importCandidates,
    archiveRecords,
    bulkImportActions: saved.bulkImportActions ?? [],
    activeSection: activeSection ?? demo.activeSection,
    updatedAt: saved.updatedAt ?? demo.updatedAt
  };
}

function normalizeAuthorNote(note: WorkspaceState['authorNotes'][number]): WorkspaceState['authorNotes'][number] {
  if (note.type !== 'editorialLearning') {
    return { ...note, attachments: note.attachments ?? [] };
  }

  return {
    ...note,
    attachments: [],
    tags: Array.from(new Set([...(note.tags ?? []), 'editorial-learning'])),
    editorialLearning: note.editorialLearning ?? {
      status: 'pendingReview',
      finalTextId: note.targetId ?? note.id,
      draftId: '',
      draftRunId: null,
      selectedVersionId: '',
      selectedVersionNumber: 1,
      selectedVersionSource: 'machineFinal',
      machineFinalVersionId: null,
      humanRevisionCount: 0,
      manualEditCount: 0,
      rejectedVersionIds: [],
      comments: [],
      qualitySummaries: [],
      unresolvedRisks: [],
      suggestedMemoryTakeaway: note.body
    }
  };
}

function hasChannelLabel(channels: WorkspaceState['publicationChannels'], label: string): boolean {
  return channels.some((channel) => channel.title === label || PUBLICATION_PLATFORM_LABELS[channel.platform] === label);
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
    draft: item.draft ? normalizePostDraftVersions(item.draft) : null,
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
  const declaredLegacy = signal.legacyIntegrityStatus === 'needsReExtraction';
  const currentContract = !declaredLegacy && Boolean(signal.editorialLanguage && signal.utilityReport);
  const legacyUtilityEvaluation = !currentContract && (signal.filterStatus || (signal.filterEvaluations ?? []).length > 0)
    ? {
        status: signal.filterStatus,
        evaluations: signal.filterEvaluations ?? [],
        source: 'legacy-client-keyword-evaluator' as const,
        canonical: false as const
      }
    : signal.legacyUtilityEvaluation;
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
    duplicateRisk: signal.duplicateRisk,
    authorCorrection: signal.authorCorrection ?? fallback.authorCorrection ?? '',
    filterEvaluations: currentContract ? signal.filterEvaluations ?? [] : undefined,
    filterStatus: currentContract ? signal.filterStatus : undefined,
    utilityReport: currentContract ? signal.utilityReport : undefined,
    relationshipReport: currentContract
      ? signal.relationshipReport ?? signal.utilityReport?.relationshipReport ?? undefined
      : undefined,
    utilityRevision: currentContract ? signal.utilityRevision : undefined,
    reviewRevision: signal.reviewRevision ?? 0,
    reviewHistory: signal.reviewHistory ?? [],
    legacyIntegrityStatus: currentContract ? signal.legacyIntegrityStatus ?? 'current' : 'needsReExtraction',
    legacyUtilityEvaluation
  };
}

function removeCrossRunSignalContamination(signals: SourceSignal[], runs: WorkspaceState['radarRuns']): SourceSignal[] {
  const radarByRunId = new Map(runs.map((run) => [run.id, run.radarId]));
  return signals.map((signal) => {
    const runRadarId = signal.radarRunId ? radarByRunId.get(signal.radarRunId) : undefined;
    if (!runRadarId || !signal.radarId || runRadarId === signal.radarId) return signal;
    return {
      ...signal,
      radarRunId: undefined,
      utilityReport: undefined,
      relationshipReport: undefined,
      utilityRevision: undefined,
      legacyIntegrityStatus: 'needsReExtraction'
    };
  });
}

function normalizeRadar(radar: RadarDefinition): RadarDefinition {
  const localizedRadar = localizeLegacyIndustrialRadar(radar);
  const sourceDiscoveryMode =
    localizedRadar.sourceDiscoveryMode ??
    (localizedRadar.sources && localizedRadar.sources.length > 0 ? 'specifiedAndAdditional' : 'autonomous');
  return {
    ...localizedRadar,
    sourceDiscoveryMode,
    sourceLanguagePolicy: localizedRadar.sourceLanguagePolicy ?? 'editorialAndEnglish',
    filters: localizedRadar.filters ?? createDefaultRadarEditorialFilters(localizedRadar.id, []),
    rules: localizedRadar.rules ?? [
      {
        id: `rule-${localizedRadar.id}`,
        operator: 'and',
        negate: false,
        statement: localizedRadar.scope,
        status: 'active'
      }
    ],
    sources: localizedRadar.sources ?? []
  };
}

function localizeLegacyIndustrialRadar(radar: RadarDefinition): RadarDefinition {
  if (radar.id !== 'ai-pattern-radar-industrial-cases' || radar.title !== 'Industrial AI cases') return radar;
  return {
    ...radar,
    title: 'Промышленные AI-кейсы',
    scope: 'Публичные кейсы industrial AI, материалы по ТОиР/EAM, инженерные блоги и технические заметки вендоров с достаточной детализацией.',
    filters: (radar.filters ?? []).map((filter) =>
      filter.id === 'ai-pattern-radar-industrial-cases-filter-industrial'
        ? {
            ...filter,
            instruction: 'Сигнал должен быть полезен для разбора паттернов industrial AI, ТОиР/EAM, Decision Intelligence, гибридного AI или открытой книги паттернов.'
          }
        : filter
    ),
    notes: 'Контрольный радар для мастерской промышленных AI-паттернов «Сборочная».'
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
