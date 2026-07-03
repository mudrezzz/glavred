import type { WorkspaceState } from '../domain/editorialWorkspace';
import {
  attachRadarSourceHandles,
  normalizeFoundMaterials,
  normalizeRadarRuns,
  normalizeSourceRegistry,
  runDeterministicRadar
} from '../domain/editorialWorkspace';

export function normalizeWorkspaceUpstream(workspace: WorkspaceState): WorkspaceState {
  const registry = normalizeSourceRegistry(workspace.sourceRegistry, {
    radars: workspace.radars,
    externalSources: workspace.externalSources,
    authorNotes: workspace.authorNotes,
    archiveRecords: workspace.archiveRecords,
    importCandidates: workspace.importCandidates,
    updatedAt: workspace.updatedAt
  });
  const radars = workspace.radars.map((radar) => attachRadarSourceHandles(radar, registry));

  return {
    ...workspace,
    sourceRegistry: registry,
    radars,
    radarRuns: normalizeRadarRuns(workspace.radarRuns, registry),
    foundMaterials: normalizeFoundMaterials(workspace.foundMaterials, registry)
  };
}

export function runLocalRadar(workspace: WorkspaceState, radarId: string, now = new Date().toISOString()): WorkspaceState {
  const normalized = normalizeWorkspaceUpstream(workspace);
  const radar = normalized.radars.find((item) => item.id === radarId);
  if (!radar) return normalized;

  const result = runDeterministicRadar(radar, {
    radars: normalized.radars,
    externalSources: normalized.externalSources,
    authorNotes: normalized.authorNotes,
    archiveRecords: normalized.archiveRecords,
    importCandidates: normalized.importCandidates,
    updatedAt: normalized.updatedAt,
    registry: normalized.sourceRegistry,
    existingRunCount: normalized.radarRuns.filter((run) => run.radarId === radarId).length,
    now
  });

  return {
    ...normalized,
    radars: normalized.radars.map((item) => (item.id === radarId ? result.radar : item)),
    radarRuns: [result.run, ...normalized.radarRuns],
    foundMaterials: [...result.foundMaterials, ...normalized.foundMaterials],
    updatedAt: now
  };
}
