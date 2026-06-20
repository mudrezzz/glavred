import type { AiRunTrace } from './aiRunTraceClient';

export type DraftRunTraceStep = {
  key: string;
  status: string;
  title: string;
  artifactPayload: Record<string, unknown> | null;
  error: string | null;
  startedAt: string | null;
  completedAt: string | null;
};

export type DraftRunTrace = {
  id: string;
  status: string;
  inputSummary: Record<string, unknown>;
  steps: DraftRunTraceStep[];
  finalDraft: Record<string, unknown> | null;
  error: string | null;
  aiRunIds: string[];
  createdAt: string;
  updatedAt: string;
};

export type DraftRunTraceBundle = {
  kind: 'draftRun';
  draftRun: DraftRunTrace;
  childAiRuns: AiRunTrace[];
  missingAiRunIds: string[];
};

export type SingleAiRunTraceBundle = {
  kind: 'aiRun';
  aiRun: AiRunTrace;
};

export type RunTraceBundle = DraftRunTraceBundle | SingleAiRunTraceBundle;

type FetchRunTrace = typeof fetch;

let runTraceFetchOverride: FetchRunTrace | null = null;

export function setRunTraceFetchForTests(fetcher: FetchRunTrace | null) {
  runTraceFetchOverride = fetcher;
}

export async function fetchRunTrace(runId: string): Promise<RunTraceBundle> {
  const normalizedRunId = runId.trim();
  if (!normalizedRunId) throw new Error('Run ID is required');

  const fetchRun = runTraceFetchOverride ?? fetch;
  const draftRunResponse = await fetchRun(`${apiBaseUrl()}/api/draft-runs/${encodeURIComponent(normalizedRunId)}`);
  if (draftRunResponse.ok) {
    const draftRun = await draftRunResponse.json() as DraftRunTrace;
    const children = await Promise.all(
      (draftRun.aiRunIds ?? []).map((aiRunId) => loadChildAiRun(fetchRun, aiRunId))
    );
    return {
      kind: 'draftRun',
      draftRun,
      childAiRuns: children.filter((child): child is AiRunTrace => child !== null),
      missingAiRunIds: (draftRun.aiRunIds ?? []).filter((aiRunId, index) => children[index] === null)
    };
  }

  if (draftRunResponse.status !== 404) {
    throw new Error(`DraftRun request failed with HTTP ${draftRunResponse.status}`);
  }

  const aiRunResponse = await fetchRun(`${apiBaseUrl()}/api/ai-runs/${encodeURIComponent(normalizedRunId)}`);
  if (!aiRunResponse.ok) {
    throw new Error(aiRunResponse.status === 404 ? 'Run not found' : `AI run request failed with HTTP ${aiRunResponse.status}`);
  }

  return { kind: 'aiRun', aiRun: await aiRunResponse.json() as AiRunTrace };
}

async function loadChildAiRun(fetchRun: FetchRunTrace, aiRunId: string): Promise<AiRunTrace | null> {
  try {
    const response = await fetchRun(`${apiBaseUrl()}/api/ai-runs/${encodeURIComponent(aiRunId)}`);
    if (!response.ok) return null;
    return await response.json() as AiRunTrace;
  } catch {
    return null;
  }
}

function apiBaseUrl(): string {
  const env = (import.meta as unknown as { env?: { VITE_API_BASE_URL?: string } }).env;
  return (env?.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
}
