import type { FoundMaterial, RadarDefinition, RadarRun, SourceSignal, WorkspaceState } from '../domain/editorialWorkspace';
import type { RadarSignalExtractionReport, RadarSignalScoringReport } from '../domain/upstream-search/types';
import { resolveApiBaseUrl } from './apiBaseUrl';

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
  signalScoringReport: RadarSignalScoringReport;
}

export interface SignalExtractionRetryResponse {
  run: RadarRun;
  sourceSignals: SourceSignal[];
  signalExtractionReport: RadarSignalExtractionReport;
  signalScoringReport: RadarSignalScoringReport;
}

export interface SignalScoringResponse {
  run: RadarRun;
  sourceSignals: SourceSignal[];
  signalScoringReport: RadarSignalScoringReport;
}

export interface SignalReviewResponse {
  sourceSignal: SourceSignal;
  signalScoringReport?: RadarSignalScoringReport | null;
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

export async function rescoreRadarSignals(projectId: string, runId: string): Promise<SignalScoringResponse> {
  const response = await radarRunFetch()(
    `${apiBaseUrl()}/api/projects/${encodeURIComponent(projectId)}/radar-runs/${encodeURIComponent(runId)}/signal-scoring`,
    { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' } }
  );
  if (!response.ok) throw new Error(`Signal scoring failed with HTTP ${response.status}`);
  return await response.json() as SignalScoringResponse;
}

export async function reviewSourceSignal(
  projectId: string,
  signalId: string,
  input: {
    action: 'approve' | 'reject' | 'archive' | 'correct' | 'reopen' | 'restore';
    reason?: string;
    editorialPatch?: Pick<SourceSignal, 'title' | 'summary' | 'authorCorrection'>;
    expectedReviewRevision: number;
  }
): Promise<SignalReviewResponse> {
  const response = await radarRunFetch()(
    `${apiBaseUrl()}/api/projects/${encodeURIComponent(projectId)}/source-signals/${encodeURIComponent(signalId)}/review`,
    {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input)
    }
  );
  if (!response.ok) throw new Error(`Signal review failed with HTTP ${response.status}`);
  return await response.json() as SignalReviewResponse;
}

function radarRunFetch(): FetchRadarRun {
  return radarRunFetchOverride ?? fetch;
}

function apiBaseUrl(): string {
  const env = (import.meta as unknown as { env?: { VITE_API_BASE_URL?: string } }).env;
  return resolveApiBaseUrl(env?.VITE_API_BASE_URL ?? 'http://localhost:8000');
}
