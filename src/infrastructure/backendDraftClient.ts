import type { DraftGenerationTrace, EditorialModel, PostBrief, PostDraft } from '../domain/editorialWorkspace';

export type BackendAiRun = {
  id: string;
  provider: string;
  model: string | null;
  error: string | null;
  fallbackUsed: boolean;
  createdAt: string;
};

export type BackendDraftResponse = {
  draft: PostDraft;
  aiRun: BackendAiRun;
};

type FetchDraft = typeof fetch;

let draftFetchOverride: FetchDraft | null = null;

export function setBackendDraftFetchForTests(fetcher: FetchDraft | null) {
  draftFetchOverride = fetcher;
}

export async function generateBackendDraft(
  brief: PostBrief,
  editorialModel: EditorialModel
): Promise<BackendDraftResponse> {
  const fetchDraft = draftFetchOverride ?? fetch;
  const response = await fetchDraft(`${apiBaseUrl()}/api/drafts/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
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
    })
  });

  if (!response.ok) {
    throw new Error(`Backend draft generation failed with HTTP ${response.status}`);
  }

  const payload = await response.json() as BackendDraftResponse;
  return {
    ...payload,
    draft: {
      ...payload.draft,
      generation: generationTraceFromRun(payload.aiRun)
    }
  };
}

function apiBaseUrl(): string {
  const env = (import.meta as unknown as { env?: { VITE_API_BASE_URL?: string } }).env;
  return (env?.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
}

function generationTraceFromRun(aiRun: BackendAiRun): DraftGenerationTrace {
  return {
    source: aiRun.fallbackUsed ? 'backendFallback' : 'openrouter',
    aiRunId: aiRun.id,
    provider: aiRun.provider,
    model: aiRun.model,
    fallbackUsed: aiRun.fallbackUsed,
    createdAt: aiRun.createdAt,
    error: aiRun.error
  };
}
