import type { EditorialModel, PostBrief, PostDraft } from '../domain/editorialWorkspace';

export type BackendAiRun = {
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

export type BackendDraftResponse = {
  draft: PostDraft;
  aiRun: BackendAiRun;
};

export async function generateBackendDraft(
  brief: PostBrief,
  editorialModel: EditorialModel
): Promise<BackendDraftResponse> {
  const response = await fetch(`${apiBaseUrl()}/api/drafts/generate`, {
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

  return response.json() as Promise<BackendDraftResponse>;
}

function apiBaseUrl(): string {
  const env = (import.meta as unknown as { env?: { VITE_API_BASE_URL?: string } }).env;
  return (env?.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
}
