import { getActiveWorkspace } from '../application/portfolioService';
import type { BlogProject, PortfolioState } from '../domain/portfolio/types';
import type { FoundMaterial, RadarDefinition, RadarRun, SourceHandle, WorkspaceState } from '../domain/editorialWorkspace';
import { BackendPortfolioStore } from './backendPortfolioStore';
import { LocalPortfolioStore } from './localPortfolioStore';

export type RadarBenchmarkTraceReport = {
  status: string;
  scenarioId?: string;
  counters?: Record<string, unknown>;
  missingExpectations?: string[];
  warnings?: string[];
  unacceptableNoiseHits?: string[];
  traceComplete?: boolean;
};

export type RadarRunTraceBundle = {
  project: BlogProject;
  workspace: WorkspaceState;
  radar: RadarDefinition;
  run: RadarRun;
  sourceHandles: SourceHandle[];
  foundMaterials: FoundMaterial[];
  benchmarkReport: RadarBenchmarkTraceReport | null;
  source: 'local' | 'backend';
};

type PortfolioLoader = () => PortfolioState | Promise<PortfolioState>;

const localStore = new LocalPortfolioStore();
const backendStore = new BackendPortfolioStore();

let localPortfolioLoader: PortfolioLoader = () => localStore.load();
let backendPortfolioLoader: PortfolioLoader = () => backendStore.load();

export function setRadarRunTracePortfolioLoadersForTests(
  localLoader: PortfolioLoader | null,
  backendLoader: PortfolioLoader | null = null
) {
  localPortfolioLoader = localLoader ?? (() => localStore.load());
  backendPortfolioLoader = backendLoader ?? (() => backendStore.load());
}

export async function fetchRadarRunTrace(runId: string, projectId?: string): Promise<RadarRunTraceBundle> {
  const normalizedRunId = runId.trim();
  if (!normalizedRunId) throw new Error('RadarRun ID is required');

  const localPortfolio = await tryLoadPortfolio(localPortfolioLoader);
  const localMatch = localPortfolio ? findRadarRunTrace(localPortfolio, normalizedRunId, projectId, 'local') : null;
  if (localMatch) return localMatch;

  const backendPortfolio = await tryLoadPortfolio(backendPortfolioLoader);
  const backendMatch = backendPortfolio ? findRadarRunTrace(backendPortfolio, normalizedRunId, projectId, 'backend') : null;
  if (backendMatch) return backendMatch;

  throw new Error('RadarRun not found');
}

async function tryLoadPortfolio(loader: PortfolioLoader): Promise<PortfolioState | null> {
  try {
    return await Promise.resolve(loader());
  } catch {
    return null;
  }
}

function findRadarRunTrace(
  portfolio: PortfolioState,
  runId: string,
  projectId: string | undefined,
  source: 'local' | 'backend'
): RadarRunTraceBundle | null {
  const projects = projectId ? portfolio.projects.filter((project) => project.id === projectId) : portfolio.projects;
  for (const project of projects) {
    const workspace = portfolio.workspacesByProjectId[project.id] ?? getActiveWorkspace({ ...portfolio, activeProjectId: project.id });
    const run = workspace.radarRuns.find((candidate) => candidate.id === runId);
    if (!run) continue;
    const radar = workspace.radars.find((candidate) => candidate.id === run.radarId);
    if (!radar) continue;
    const sourceHandles = resolveSourceHandles(workspace, radar, run);
    const foundMaterials = workspace.foundMaterials.filter(
      (material) => material.radarRunId === run.id || run.foundMaterialIds.includes(material.id)
    );
    return {
      project,
      workspace,
      radar,
      run,
      sourceHandles,
      foundMaterials,
      benchmarkReport: extractBenchmarkReport(run),
      source
    };
  }
  return null;
}

function resolveSourceHandles(workspace: WorkspaceState, radar: RadarDefinition, run: RadarRun): SourceHandle[] {
  const wantedIds = new Set([
    ...(radar.sourceHandleIds ?? []),
    ...run.operations.map((operation) => operation.sourceHandleId),
    ...(run.searchPlan?.queries ?? []).map((query) => query.sourceHandleId),
    ...(run.searchPlan?.intents ?? []).map((intent) => intent.sourceHandleId)
  ].filter(Boolean));
  return workspace.sourceRegistry.handles.filter((handle) => wantedIds.has(handle.id));
}

function extractBenchmarkReport(run: RadarRun): RadarBenchmarkTraceReport | null {
  const candidate = (run as unknown as { benchmarkReport?: unknown; benchmark?: { report?: unknown } });
  return asBenchmarkReport(candidate.benchmarkReport) ?? asBenchmarkReport(candidate.benchmark?.report);
}

function asBenchmarkReport(value: unknown): RadarBenchmarkTraceReport | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const report = value as RadarBenchmarkTraceReport;
  return typeof report.status === 'string' ? report : null;
}
