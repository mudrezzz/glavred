import type { FoundMaterial, RadarDefinition, RadarRun, SourceSignal, WorkspaceState } from '../domain/editorialWorkspace';

export interface RadarRunWorkspaceResult {
  radar?: RadarDefinition;
  run: RadarRun;
  foundMaterials?: FoundMaterial[];
  sourceSignals: SourceSignal[];
}

export function applyRadarRunWorkspaceResult(
  workspace: WorkspaceState,
  result: RadarRunWorkspaceResult,
  options: { prependRun?: boolean } = {}
): WorkspaceState {
  const runs = options.prependRun
    ? mergeById([result.run, ...workspace.radarRuns])
    : workspace.radarRuns.map((run) => run.id === result.run.id ? result.run : run);
  const signalsFromOtherRuns = workspace.sourceSignals.filter((signal) => signal.radarRunId !== result.run.id);
  return {
    ...workspace,
    radars: result.radar
      ? workspace.radars.map((radar) => radar.id === result.radar?.id ? result.radar : radar)
      : workspace.radars,
    radarRuns: runs,
    foundMaterials: mergeById([...(result.foundMaterials ?? []), ...workspace.foundMaterials]),
    sourceSignals: mergeById([...result.sourceSignals, ...signalsFromOtherRuns]),
    updatedAt: new Date().toISOString()
  };
}

function mergeById<T extends { id: string }>(items: T[]): T[] {
  const seen = new Set<string>();
  return items.filter((item) => {
    if (seen.has(item.id)) return false;
    seen.add(item.id);
    return true;
  });
}
