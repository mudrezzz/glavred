export type AiRunTrace = {
  id: string;
  capability: string;
  status: string;
  provider: string;
  model: string | null;
  requestPayload: Record<string, unknown>;
  resultPayload: Record<string, unknown> | null;
  error: string | null;
  fallbackUsed: boolean;
  createdAt: string;
  updatedAt: string;
};

type FetchAiRun = typeof fetch;

let aiRunTraceFetchOverride: FetchAiRun | null = null;

export function setAiRunTraceFetchForTests(fetcher: FetchAiRun | null) {
  aiRunTraceFetchOverride = fetcher;
}

export async function fetchAiRunTrace(runId: string): Promise<AiRunTrace> {
  const normalizedRunId = runId.trim();
  if (!normalizedRunId) throw new Error('Run ID is required');

  const fetchAiRun = aiRunTraceFetchOverride ?? fetch;
  const response = await fetchAiRun(`${apiBaseUrl()}/api/ai-runs/${encodeURIComponent(normalizedRunId)}`);
  if (!response.ok) {
    throw new Error(response.status === 404 ? 'AI run not found' : `AI run request failed with HTTP ${response.status}`);
  }

  return await response.json() as AiRunTrace;
}

function apiBaseUrl(): string {
  const env = (import.meta as unknown as { env?: { VITE_API_BASE_URL?: string } }).env;
  return (env?.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
}
