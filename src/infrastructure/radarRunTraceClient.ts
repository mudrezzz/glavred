import { getActiveWorkspace } from '../application/portfolioService';
import type { BlogProject, PortfolioState } from '../domain/portfolio/types';
import type { FoundMaterial, RadarDefinition, RadarRun, SourceHandle, SourceSignal, WorkspaceState } from '../domain/editorialWorkspace';
import { applyRadarRunWorkspaceResult } from '../app/radarRunWorkspacePatches';
import { retryRadarSignalExtraction } from './radarRunClient';
import { BackendPortfolioStore } from './backendPortfolioStore';
import { LocalPortfolioStore } from './localPortfolioStore';

export type RadarBenchmarkTraceReport = {
  status: string;
  scenarioId?: string;
  evaluationMode?: string;
  providerHealth?: string;
  coverage?: Record<string, unknown>;
  plannedCoverage?: Record<string, unknown>;
  executedCoverage?: Record<string, unknown>;
  skippedRequiredCoverage?: Array<Record<string, unknown>>;
  counters?: Record<string, unknown>;
  missingExpectations?: string[];
  warnings?: string[];
  unacceptableNoiseHits?: string[];
  inconclusiveReasons?: string[];
  traceComplete?: boolean;
  usefulYield?: RadarRun['searchOpportunityCoverage'];
};

export type RadarRunTraceBundle = {
  project: BlogProject;
  workspace: WorkspaceState;
  radar: RadarDefinition;
  run: RadarRun;
  sourceHandles: SourceHandle[];
  foundMaterials: FoundMaterial[];
  sourceSignals: SourceSignal[];
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

  const backendPortfolio = await tryLoadPortfolio(backendPortfolioLoader);
  const backendMatch = backendPortfolio ? findRadarRunTrace(backendPortfolio, normalizedRunId, projectId, 'backend') : null;
  if (backendMatch) return backendMatch;

  const localPortfolio = await tryLoadPortfolio(localPortfolioLoader);
  const localMatch = localPortfolio ? findRadarRunTrace(localPortfolio, normalizedRunId, projectId, 'local') : null;
  if (localMatch) return localMatch;

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
      sourceSignals: workspace.sourceSignals.filter((signal) => signal.radarRunId === run.id),
      benchmarkReport: extractBenchmarkReport(run),
      source
    };
  }
  return null;
}

export async function retryRadarRunSignalExtraction(bundle: RadarRunTraceBundle): Promise<RadarRunTraceBundle> {
  const result = await retryRadarSignalExtraction(bundle.workspace, bundle.run.id, true, {
    projectId: bundle.project.id,
    editorialLanguage: bundle.project.language
  });
  const workspace = applyRadarRunWorkspaceResult(bundle.workspace, result);
  const portfolio = await (bundle.source === 'backend' ? backendPortfolioLoader() : localPortfolioLoader());
  const nextPortfolio: PortfolioState = {
    ...portfolio,
    activeProjectId: bundle.project.id,
    workspacesByProjectId: { ...portfolio.workspacesByProjectId, [bundle.project.id]: workspace },
    updatedAt: new Date().toISOString()
  };
  if (bundle.source === 'backend') await backendStore.save(nextPortfolio);
  else localStore.save(nextPortfolio);
  return {
    ...bundle,
    workspace,
    run: result.run,
    sourceSignals: workspace.sourceSignals.filter((signal) => signal.radarRunId === result.run.id)
  };
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
