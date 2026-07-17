import type { FoundMaterial, RadarDefinition, RadarRun, SourceSignal, WorkspaceState } from '../domain/editorialWorkspace';
import type { RadarSignalExtractionReport } from '../domain/upstream-search/types';

export interface RadarProjectContext {
  projectId: string;
  editorialLanguage: string;
}

type FetchRadarRun = typeof fetch;

let radarRunFetchOverride: FetchRadarRun | null = null;

export function setRadarRunFetchForTests(fetcher: FetchRadarRun | null) {
  radarRunFetchOverride = fetcher;
}

export interface ExternalRadarRunResponse {
  radar: RadarDefinition;
  run: RadarRun;
  foundMaterials: FoundMaterial[];
  sourceSignals: SourceSignal[];
  signalExtractionReport: RadarSignalExtractionReport;
}

export interface SignalExtractionRetryResponse {
  run: RadarRun;
  sourceSignals: SourceSignal[];
  signalExtractionReport: RadarSignalExtractionReport;
}

export async function retryRadarSignalExtraction(
  workspace: WorkspaceState,
  runId: string,
  forceRetry = true,
  projectContext?: RadarProjectContext
): Promise<SignalExtractionRetryResponse> {
  const response = await radarRunFetch()(`${apiBaseUrl()}/api/radar-runs/${encodeURIComponent(runId)}/signal-extraction`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ workspace, forceRetry, projectContext })
  });
  if (!response.ok) throw new Error(`Signal extraction failed with HTTP ${response.status}`);
  return await response.json() as SignalExtractionRetryResponse;
}

export async function runExternalRadar(
  workspace: WorkspaceState,
  radarId: string,
  projectContext?: RadarProjectContext
): Promise<ExternalRadarRunResponse> {
  const response = await radarRunFetch()(`${apiBaseUrl()}/api/radar-runs/external`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ radarId, workspace, projectContext })
  });
  if (!response.ok) {
    throw new Error(`Radar run failed with HTTP ${response.status}`);
  }
  return await response.json() as ExternalRadarRunResponse;
}

function radarRunFetch(): FetchRadarRun {
  return radarRunFetchOverride ?? fetch;
}

function apiBaseUrl(): string {
  const env = (import.meta as unknown as { env?: { VITE_API_BASE_URL?: string } }).env;
  return (env?.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
}
