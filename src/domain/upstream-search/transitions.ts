import type { AuthorExternalSource, AuthorNote, ImportedMemoryCandidate } from '../author-memory/types';
import type { ArchiveRecord } from '../imports/types';
import type { RadarDefinition, RadarSearchSource, RadarSearchSourceType } from '../signals/types';
import type {
  FoundMaterial,
  FoundMaterialType,
  RadarRun,
  RadarRunBudget,
  RadarRunOperation,
  SourceCapability,
  SourceHandle,
  SourceHandleType,
  SourceRegistry
} from './types';

export type SourceRegistryContext = {
  radars: RadarDefinition[];
  externalSources: AuthorExternalSource[];
  authorNotes: AuthorNote[];
  archiveRecords: ArchiveRecord[];
  importCandidates: ImportedMemoryCandidate[];
  updatedAt: string;
};

export type RadarRunContext = SourceRegistryContext & {
  registry: SourceRegistry;
  existingRunCount: number;
  now: string;
};

export function normalizeSourceRegistry(
  registry: SourceRegistry | undefined,
  context: SourceRegistryContext
): SourceRegistry {
  const handlesById = new Map<string, SourceHandle>();
  const addHandle = (handle: SourceHandle) => {
    handlesById.set(handle.id, normalizeSourceHandle(handle));
  };

  (registry?.handles ?? []).forEach(addHandle);
  context.radars.flatMap((radar) => radar.sources ?? []).forEach((source) => addHandle(sourceHandleFromRadarSource(source)));
  context.externalSources.forEach((source) => addHandle(sourceHandleFromExternalSource(source)));

  if (context.authorNotes.length > 0) addHandle(projectInternalHandle('source-author-memory', 'Author memory', 'authorMemory'));
  if (context.archiveRecords.length > 0) addHandle(projectInternalHandle('source-archive', 'Archive and previous materials', 'archive'));
  if (context.importCandidates.length > 0) addHandle(projectInternalHandle('source-import-queue', 'Import queue', 'manualNotes'));

  return {
    id: registry?.id ?? 'source-registry-project',
    handles: Array.from(handlesById.values()),
    updatedAt: registry?.updatedAt ?? context.updatedAt
  };
}

export function attachRadarSourceHandles(radar: RadarDefinition, registry: SourceRegistry): RadarDefinition {
  const legacyIds = (radar.sources ?? [])
    .map((source) => sourceHandleIdFromRadarSource(source))
    .filter((id) => registry.handles.some((handle) => handle.id === id));
  const defaults = defaultHandleIdsForRadar(radar, registry);
  const sourceHandleIds = unique([...(radar.sourceHandleIds ?? []), ...legacyIds, ...defaults]);
  return { ...radar, sourceHandleIds };
}

export function normalizeRadarRuns(runs: RadarRun[] | undefined, registry: SourceRegistry): RadarRun[] {
  if (!runs?.length) return [];
  const handleIds = new Set(registry.handles.map((handle) => handle.id));
  const lifecycleOperationKinds = new Set(['signalExtraction', 'signalScoring']);
  return runs.map((run) => ({
    ...run,
    operations: run.operations.filter((operation) =>
      handleIds.has(operation.sourceHandleId) || lifecycleOperationKinds.has(operation.kind)
    ),
    foundMaterialIds: run.foundMaterialIds ?? [],
    skippedReasons: run.skippedReasons ?? [],
    warnings: run.warnings ?? [],
    errors: run.errors ?? []
  }));
}

export function normalizeFoundMaterials(materials: FoundMaterial[] | undefined, registry: SourceRegistry): FoundMaterial[] {
  if (!materials?.length) return [];
  const handleIds = new Set(registry.handles.map((handle) => handle.id));
  return materials.filter((material) => handleIds.has(material.sourceHandleId));
}

export function runDeterministicRadar(radar: RadarDefinition, context: RadarRunContext): {
  radar: RadarDefinition;
  run: RadarRun;
  foundMaterials: FoundMaterial[];
} {
  const startedAt = context.now;
  const runId = `radar-run-${radar.id}-${context.existingRunCount + 1}`;
  const budget = createDefaultRadarRunBudget();
  const handles = resolveRadarHandles(radar, context.registry);
  const operations: RadarRunOperation[] = [];
  const foundMaterials: FoundMaterial[] = [];
  const skippedReasons: string[] = [];
  const warnings: string[] = [];

  handles.slice(0, budget.maxOperations).forEach((handle, index) => {
    const operationId = `${runId}-op-${index + 1}`;
    const materialForHandle = createFoundMaterialForHandle(handle, radar, context, runId, startedAt);
    budget.usedOperations += 1;

    if (handle.status !== 'active') {
      const skippedReason = `source-handle-${handle.status}`;
      skippedReasons.push(skippedReason);
      operations.push(createSkippedOperation(operationId, runId, handle.id, handle.title, startedAt, skippedReason));
      return;
    }

    if (!materialForHandle) {
      const skippedReason = providerSkippedReason(handle);
      skippedReasons.push(skippedReason);
      operations.push(createSkippedOperation(operationId, runId, handle.id, handle.title, startedAt, skippedReason, handle.locator));
      if (handle.capabilities.canSearch) budget.usedExternalQueries += 1;
      if (handle.capabilities.canReadUrl) budget.usedUrlReads += 1;
      return;
    }

    if (foundMaterials.length >= budget.maxFoundMaterials) {
      const skippedReason = 'budget-max-found-materials';
      skippedReasons.push(skippedReason);
      operations.push(createSkippedOperation(operationId, runId, handle.id, handle.title, startedAt, skippedReason));
      return;
    }

    foundMaterials.push(materialForHandle);
    budget.usedFoundMaterials += 1;
    budget.usedInternalItems += handle.capabilities.canScanInternal ? 1 : 0;
    operations.push({
      id: operationId,
      runId,
      sourceHandleId: handle.id,
      kind: handle.capabilities.canScanInternal ? 'internalScan' : 'metadataOnly',
      label: handle.title,
      status: 'succeeded',
      startedAt,
      completedAt: startedAt,
      target: handle.locator,
      foundMaterialIds: [materialForHandle.id]
    });
  });

  if (handles.length > budget.maxOperations) warnings.push('budget-max-operations-hit');
  if (handles.length === 0) warnings.push('no-source-handles');

  const foundMaterialIds = foundMaterials.map((material) => material.id);
  const run: RadarRun = {
    id: runId,
    radarId: radar.id,
    status: foundMaterialIds.length > 0 && skippedReasons.length > 0 ? 'partial' : foundMaterialIds.length > 0 ? 'succeeded' : 'partial',
    startedAt,
    completedAt: startedAt,
    budget,
    operations,
    foundMaterialIds,
    skippedReasons: unique(skippedReasons),
    warnings,
    errors: []
  };

  return {
    radar: { ...radar, lastRunAt: startedAt, sourceHandleIds: handles.map((handle) => handle.id) },
    run,
    foundMaterials
  };
}

export function summarizeRadarRun(run: RadarRun | undefined): { found: number; skipped: number; status: string } {
  if (!run) return { found: 0, skipped: 0, status: 'not-run' };
  return {
    found: run.foundMaterialIds.length,
    skipped: run.operations.filter((operation) => operation.status === 'skipped').length,
    status: run.status
  };
}

function normalizeSourceHandle(handle: SourceHandle): SourceHandle {
  return {
    ...handle,
    status: handle.status ?? 'active',
    obligation: handle.obligation ?? 'preferred',
    capabilities: handle.capabilities ?? capabilitiesForHandleType(handle.type),
    tags: handle.tags ?? [],
    notes: handle.notes ?? ''
  };
}

function sourceHandleFromRadarSource(source: RadarSearchSource): SourceHandle {
  const type = handleTypeFromRadarSourceType(source.type);
  return {
    id: sourceHandleIdFromRadarSource(source),
    type,
    title: source.title || source.value || source.id,
    locator: source.value,
    status: source.status === 'active' ? 'active' : 'paused',
    obligation: type === 'authorMemory' || type === 'archive' ? 'internalOnly' : 'preferred',
    capabilities: capabilitiesForHandleType(type),
    notes: source.notes,
    tags: ['legacy-radar-source'],
    legacySourceId: source.id
  };
}

function sourceHandleFromExternalSource(source: AuthorExternalSource): SourceHandle {
  return {
    id: stableId('source-external', source.id || source.title || source.url),
    type: 'externalUrl',
    title: source.title || source.url,
    locator: source.url,
    status: source.status === 'paused' ? 'paused' : 'active',
    obligation: 'preferred',
    capabilities: capabilitiesForHandleType('externalUrl'),
    notes: source.notes,
    tags: ['external-source']
  };
}

function projectInternalHandle(id: string, title: string, type: SourceHandleType): SourceHandle {
  return {
    id,
    type,
    title,
    locator: id,
    status: 'active',
    obligation: 'internalOnly',
    capabilities: capabilitiesForHandleType(type),
    notes: '',
    tags: ['project-internal']
  };
}

function handleTypeFromRadarSourceType(type: RadarSearchSourceType): SourceHandleType {
  const map: Record<RadarSearchSourceType, SourceHandleType> = {
    authorArchive: 'archive',
    externalUrl: 'externalUrl',
    mcpServer: 'sourcePlaceholder',
    api: 'sourcePlaceholder',
    searchKeywords: 'openWebQuery',
    manualSource: 'manualNotes',
    socialProfile: 'socialProfile',
    document: 'document',
    openWeb: 'openWebQuery'
  };
  return map[type];
}

function sourceHandleIdFromRadarSource(source: RadarSearchSource): string {
  return stableId('source-radar', source.id || source.title || source.value);
}

function defaultHandleIdsForRadar(radar: RadarDefinition, registry: SourceRegistry): string[] {
  const internalIds = registry.handles
    .filter((handle) => handle.capabilities.canScanInternal)
    .map((handle) => handle.id);
  if (radar.sourceType === 'authorMemory') {
    return internalIds.filter((id) => id === 'source-author-memory');
  }
  if (radar.sourceType === 'archive') {
    return internalIds.filter((id) => id === 'source-archive');
  }
  if (radar.sources.length > 0 || radar.sourceDiscoveryMode === 'specifiedOnly') return [];
  return internalIds.slice(0, 2);
}

function resolveRadarHandles(radar: RadarDefinition, registry: SourceRegistry): SourceHandle[] {
  const ids = radar.sourceHandleIds?.length
    ? radar.sourceHandleIds
    : attachRadarSourceHandles(radar, registry).sourceHandleIds ?? [];
  const byId = new Map(registry.handles.map((handle) => [handle.id, handle]));
  return ids.map((id) => byId.get(id)).filter((handle): handle is SourceHandle => Boolean(handle));
}

function createFoundMaterialForHandle(
  handle: SourceHandle,
  radar: RadarDefinition,
  context: RadarRunContext,
  runId: string,
  capturedAt: string
): FoundMaterial | null {
  if (handle.type === 'authorMemory') {
    const note = context.authorNotes.find((item) => item.body || item.title);
    return note ? materialFromInternalItem(runId, handle, 'authorNote', note.id, note.title, note.body, capturedAt) : null;
  }
  if (handle.type === 'archive') {
    const record = context.archiveRecords.find((item) => item.title || item.bodyExcerpt);
    return record ? materialFromInternalItem(runId, handle, 'archiveRecord', record.id, record.title, record.bodyExcerpt, capturedAt) : null;
  }
  if (handle.type === 'manualNotes') {
    const item = context.importCandidates.find((candidate) => candidate.title || candidate.excerpt);
    return item ? materialFromInternalItem(runId, handle, 'manualNote', item.id, item.title, item.excerpt, capturedAt) : null;
  }
  if (handle.type === 'sourcePlaceholder' && handle.locator) {
    return materialFromInternalItem(runId, handle, 'externalPlaceholder', radar.id, handle.title, handle.notes, capturedAt, 'metadataOnly');
  }
  return null;
}

function materialFromInternalItem(
  runId: string,
  handle: SourceHandle,
  type: FoundMaterialType,
  itemId: string,
  title: string,
  body: string,
  capturedAt: string,
  status: FoundMaterial['status'] = 'found'
): FoundMaterial {
  return {
    id: `${runId}-material-${stableSlug(`${handle.id}-${itemId}`)}`,
    radarRunId: runId,
    sourceHandleId: handle.id,
    type,
    title: title || handle.title,
    locator: handle.locator,
    snippet: body.slice(0, 240),
    summary: body.slice(0, 360),
    capturedAt,
    status,
    warnings: status === 'metadataOnly' ? ['metadata-only'] : [],
    provenanceLabel: handle.title
  };
}

function createSkippedOperation(
  id: string,
  runId: string,
  sourceHandleId: string,
  label: string,
  at: string,
  skippedReason: string,
  target?: string
): RadarRunOperation {
  return {
    id,
    runId,
    sourceHandleId,
    kind: 'skip',
    label,
    status: 'skipped',
    startedAt: at,
    completedAt: at,
    target,
    foundMaterialIds: [],
    skippedReason
  };
}

function providerSkippedReason(handle: SourceHandle): string {
  if (handle.capabilities.canSearch) return 'provider-not-implemented';
  if (handle.capabilities.canReadUrl) return 'url-reader-not-implemented';
  if (handle.capabilities.canImport) return 'document-reader-not-implemented';
  return 'metadata-only';
}

function createDefaultRadarRunBudget(): RadarRunBudget {
  return {
    maxOperations: 8,
    maxInternalItems: 4,
    maxExternalQueries: 4,
    maxUrlReads: 2,
    maxFoundMaterials: 5,
    usedOperations: 0,
    usedInternalItems: 0,
    usedExternalQueries: 0,
    usedUrlReads: 0,
    usedFoundMaterials: 0
  };
}

function capabilitiesForHandleType(type: SourceHandleType): SourceCapability {
  const internal = { canScanInternal: true, canSearch: false, canReadUrl: false, canImport: false, canVerify: false, broadDiscovery: false };
  const url = { canScanInternal: false, canSearch: false, canReadUrl: true, canImport: false, canVerify: true, broadDiscovery: false };
  const search = { canScanInternal: false, canSearch: true, canReadUrl: false, canImport: false, canVerify: true, broadDiscovery: true };
  const document = { canScanInternal: false, canSearch: false, canReadUrl: false, canImport: true, canVerify: true, broadDiscovery: false };
  const placeholder = { canScanInternal: false, canSearch: false, canReadUrl: false, canImport: false, canVerify: false, broadDiscovery: false };
  const map: Record<SourceHandleType, SourceCapability> = {
    authorMemory: internal,
    archive: internal,
    previousPosts: internal,
    manualNotes: internal,
    externalUrl: url,
    openWebQuery: search,
    socialProfile: search,
    document,
    sourcePlaceholder: placeholder
  };
  return map[type];
}

function stableId(prefix: string, value: string): string {
  return `${prefix}-${stableSlug(value || prefix)}`;
}

function stableSlug(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9а-яё]+/gi, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 64) || 'item';
}

function unique<T>(items: T[]): T[] {
  return Array.from(new Set(items));
}
