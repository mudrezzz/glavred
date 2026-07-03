import type { FoundMaterial, RadarDefinition, RadarRun, WorkspaceState } from '../domain/editorialWorkspace';

type FetchRadarRun = typeof fetch;

let radarRunFetchOverride: FetchRadarRun | null = null;

export function setRadarRunFetchForTests(fetcher: FetchRadarRun | null) {
  radarRunFetchOverride = fetcher;
}

export interface ExternalRadarRunResponse {
  radar: RadarDefinition;
  run: RadarRun;
  foundMaterials: FoundMaterial[];
}

export async function runExternalRadar(workspace: WorkspaceState, radarId: string): Promise<ExternalRadarRunResponse> {
  const response = await radarRunFetch()(`${apiBaseUrl()}/api/radar-runs/external`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ radarId, workspace })
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
