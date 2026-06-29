import { afterEach, describe, expect, it, vi } from 'vitest';
import type { HumanCommentRevisionQualityCheck, PostDraft } from '../domain/editorialWorkspace';
import { reviseDraftWithEditorComment, setDraftCommentRevisionFetchForTests } from './draftCommentRevisionClient';

describe('draftCommentRevisionClient', () => {
  afterEach(() => {
    setDraftCommentRevisionFetchForTests(null);
  });

  it('posts the active draft version to the comment revision endpoint', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        title: 'Revised title',
        body: 'Revised body',
        revisionSummary: 'Used editor comment.',
        aiRunId: 'ai-human-1',
        selectedModel: 'writer-model',
        attempts: [],
        qualityCheck: makeQualityCheck('passed')
      })
    });
    setDraftCommentRevisionFetchForTests(fetchMock);

    const result = await reviseDraftWithEditorComment(makeDraft(), 'Make it more concrete');

    expect(result.body).toBe('Revised body');
    expect(result.qualityCheck.status).toBe('passed');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/api/drafts/revise-with-comment',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
    );
    const payload = JSON.parse(String(fetchMock.mock.calls[0][1].body));
    expect(payload).toMatchObject({
      draftRunId: 'run-1',
      currentVersion: {
        id: 'draft-1-v2',
        versionNumber: 2,
        title: 'Active title',
        body: 'Active body'
      },
      editorComment: 'Make it more concrete'
    });
  });

  it('throws on provider failure instead of fabricating a revision', async () => {
    setDraftCommentRevisionFetchForTests(vi.fn().mockResolvedValue({ ok: false, status: 503 }));

    await expect(reviseDraftWithEditorComment(makeDraft(), 'Try again')).rejects.toThrow(/HTTP 503/i);
  });
});

function makeDraft(): PostDraft {
  return {
    id: 'draft-1',
    briefId: 'brief-1',
    title: 'Active title',
    body: 'Active body',
    version: 2,
    status: 'revised',
    updatedAt: '2026-06-28T00:00:00.000Z',
    activeVersionId: 'draft-1-v2',
    versions: [
      {
        id: 'draft-1-v1',
        versionNumber: 1,
        source: 'machineFinal',
        title: 'Machine title',
        body: 'Machine body',
        draftRunId: 'run-1',
        aiRunId: 'ai-machine-1',
        createdAt: '2026-06-28T00:00:00.000Z'
      },
      {
        id: 'draft-1-v2',
        versionNumber: 2,
        source: 'manualEdit',
        baseVersionId: 'draft-1-v1',
        title: 'Active title',
        body: 'Active body',
        draftRunId: 'run-1',
        aiRunId: null,
        createdAt: '2026-06-28T00:01:00.000Z'
      }
    ],
    generation: {
      source: 'draftRun',
      aiRunId: 'ai-machine-1',
      draftRunId: 'run-1',
      provider: 'openrouter',
      model: 'writer-model',
      fallbackUsed: false,
      createdAt: '2026-06-28T00:00:00.000Z'
    }
  };
}

function makeQualityCheck(status: 'passed' | 'warning' | 'critical' | 'notRun'): HumanCommentRevisionQualityCheck {
  return {
    status,
    commentComplianceStatus: status,
    sourceIntegrityStatus: 'passed',
    publicProseStatus: 'passed',
    internalJargonLeaks: [],
    regressionWarnings: [],
    matchedCommentIntents: ['concreteness'],
    missedCommentIntents: [],
    summary: 'Revision follows the comment.',
    attempts: []
  };
}
