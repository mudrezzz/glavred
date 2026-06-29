import type { PostDraft } from '../domain/editorialWorkspace';

export type DraftCommentRevisionResponse = {
  title: string;
  body: string;
  revisionSummary: string;
  aiRunId: string | null;
  selectedModel: string | null;
  attempts: Array<Record<string, unknown>>;
};

type FetchRevision = typeof fetch;

let revisionFetchOverride: FetchRevision | null = null;

export function setDraftCommentRevisionFetchForTests(fetcher: FetchRevision | null) {
  revisionFetchOverride = fetcher;
}

export async function reviseDraftWithEditorComment(
  draft: PostDraft,
  editorComment: string
): Promise<DraftCommentRevisionResponse> {
  const fetchRevision = revisionFetchOverride ?? fetch;
  const response = await fetchRevision(`${apiBaseUrl()}/api/drafts/revise-with-comment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      draftRunId: draft.generation?.draftRunId ?? null,
      currentVersion: {
        id: draft.activeVersionId ?? `${draft.id}-v${draft.version}`,
        versionNumber: draft.version,
        title: draft.title,
        body: draft.body
      },
      editorComment
    })
  });

  if (!response.ok) {
    throw new Error(`Draft revision failed with HTTP ${response.status}`);
  }

  return await response.json() as DraftCommentRevisionResponse;
}

function apiBaseUrl(): string {
  const env = (import.meta as unknown as { env?: { VITE_API_BASE_URL?: string } }).env;
  return (env?.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
}
