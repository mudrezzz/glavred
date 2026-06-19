import type { DraftGenerationTrace, EditorialModel, PostBrief, PostDraft } from '../domain/editorialWorkspace';

type FetchDraftRun = typeof fetch;

export type DraftRunCreateResponse = {
  runId: string;
  status: DraftRunStatus;
};

export type DraftRunStatus = 'queued' | 'running' | 'succeeded' | 'failed';
export type DraftRunStepStatus = 'pending' | 'running' | 'succeeded' | 'failed';

export type DraftRunStepResponse = {
  key: string;
  status: DraftRunStepStatus;
  title: string;
  artifactPayload: Record<string, unknown> | null;
  error: string | null;
  startedAt: string | null;
  completedAt: string | null;
};

export type DraftRunResponse = {
  id: string;
  status: DraftRunStatus;
  steps: DraftRunStepResponse[];
  finalDraft: PostDraft | null;
  error: string | null;
  createdAt: string;
  updatedAt: string;
};

let draftRunFetchOverride: FetchDraftRun | null = null;
let pollingIntervalMs = 1600;
let pollingTimeoutMs = 120000;

export function setDraftRunFetchForTests(fetcher: FetchDraftRun | null) {
  draftRunFetchOverride = fetcher;
}

export function setDraftRunPollingForTests(options: { intervalMs?: number; timeoutMs?: number }) {
  pollingIntervalMs = options.intervalMs ?? pollingIntervalMs;
  pollingTimeoutMs = options.timeoutMs ?? pollingTimeoutMs;
}

export async function startDraftRun(
  brief: PostBrief,
  editorialModel: EditorialModel
): Promise<DraftRunCreateResponse> {
  const response = await draftRunFetch()(`${apiBaseUrl()}/api/draft-runs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(draftRequestPayload(brief, editorialModel))
  });
  if (!response.ok) {
    throw new Error(`DraftRun creation failed with HTTP ${response.status}`);
  }
  return await response.json() as DraftRunCreateResponse;
}

export async function fetchDraftRun(runId: string): Promise<DraftRunResponse> {
  const response = await draftRunFetch()(`${apiBaseUrl()}/api/draft-runs/${runId}`);
  if (!response.ok) {
    throw new Error(`DraftRun polling failed with HTTP ${response.status}`);
  }
  return await response.json() as DraftRunResponse;
}

export async function waitForDraftRun(
  runId: string,
  onProgress?: (run: DraftRunResponse) => void
): Promise<DraftRunResponse> {
  const startedAt = Date.now();
  for (;;) {
    const run = await fetchDraftRun(runId);
    onProgress?.(run);
    if (run.status === 'succeeded' || run.status === 'failed') {
      return run;
    }
    if (Date.now() - startedAt > pollingTimeoutMs) {
      throw new Error(`DraftRun ${runId} timed out`);
    }
    await new Promise((resolve) => setTimeout(resolve, pollingIntervalMs));
  }
}

export function draftFromCompletedRun(run: DraftRunResponse): PostDraft {
  if (!run.finalDraft) {
    throw new Error(`DraftRun ${run.id} completed without final draft`);
  }
  return {
    ...run.finalDraft,
    generation: generationTraceFromRun(run)
  };
}

export function currentDraftRunStep(run: DraftRunResponse): DraftRunStepResponse | null {
  return (
    run.steps.find((step) => step.status === 'running') ??
    [...run.steps].reverse().find((step) => step.status === 'succeeded') ??
    run.steps[0] ??
    null
  );
}

function draftRunFetch(): FetchDraftRun {
  return draftRunFetchOverride ?? fetch;
}

function apiBaseUrl(): string {
  const env = (import.meta as unknown as { env?: { VITE_API_BASE_URL?: string } }).env;
  return (env?.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
}

function generationTraceFromRun(run: DraftRunResponse): DraftGenerationTrace {
  return {
    source: 'draftRun',
    aiRunId: null,
    draftRunId: run.id,
    provider: 'deterministic',
    model: 'draft-run-v1',
    fallbackUsed: false,
    createdAt: run.createdAt,
    error: run.error
  };
}

function draftRequestPayload(brief: PostBrief, editorialModel: EditorialModel) {
  return {
    brief: {
      id: brief.id,
      title: brief.title,
      rubric: brief.rubric,
      audience: brief.audience,
      thesis: brief.thesis,
      conflict: brief.conflict,
      authorPosition: brief.authorPosition,
      evidence: brief.evidence,
      examples: brief.examples,
      structure: brief.structure,
      cta: brief.cta,
      risks: brief.risks,
      sources: brief.sources
    },
    editorialModel: {
      audience: editorialModel.audience,
      styleRules: editorialModel.styleRules,
      forbiddenTopics: editorialModel.forbiddenTopics,
      goals: editorialModel.goals
    }
  };
}
