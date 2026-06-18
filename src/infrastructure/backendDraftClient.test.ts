import { describe, expect, it, vi } from 'vitest';
import { approvePostBrief } from '../domain/editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { buildApprovePlanSlotPatch } from '../app/editorialWorkQueueActions';
import { generateBackendDraft } from './backendDraftClient';

describe('backendDraftClient', () => {
  it('posts approved brief context to the backend draft endpoint', async () => {
    const workspace = createWorkspaceWithBrief();
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        draft: {
          id: 'draft-brief-demo',
          briefId: workspace.postBrief!.id,
          title: 'Backend title',
          body: 'Backend body',
          version: 1,
          status: 'draft',
          updatedAt: '2026-06-18T00:00:00+00:00'
        },
        aiRun: {
          id: 'run-1',
          capability: 'draftGeneration',
          status: 'succeeded',
          provider: 'openrouter',
          model: 'openrouter/test-model',
          requestPayload: {},
          resultPayload: { draftId: 'draft-brief-demo' },
          error: null,
          fallbackUsed: false,
          createdAt: '2026-06-18T00:00:00+00:00',
          updatedAt: '2026-06-18T00:00:00+00:00'
        }
      })
    });
    vi.stubGlobal('fetch', fetchMock);

    const result = await generateBackendDraft(approvePostBrief(workspace.postBrief!), workspace.editorialModel);

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/api/drafts/generate',
      expect.objectContaining({ method: 'POST' })
    );
    const body = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(body.brief.id).toBe(workspace.postBrief!.id);
    expect(body.brief.authorPosition).toBe(workspace.postBrief!.authorPosition);
    expect(body.editorialModel.styleRules).toEqual(workspace.editorialModel.styleRules);
    expect(result.draft.body).toBe('Backend body');
    expect(result.draft.generation).toEqual({
      source: 'openrouter',
      aiRunId: 'run-1',
      provider: 'openrouter',
      model: 'openrouter/test-model',
      fallbackUsed: false,
      createdAt: '2026-06-18T00:00:00+00:00',
      error: null
    });
    vi.unstubAllGlobals();
  });

  it('throws when the backend rejects draft generation', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 503 }));

    await expect(generateBackendDraft(createWorkspaceWithBrief().postBrief!, createDemoWorkspace().editorialModel)).rejects.toThrow(
      /HTTP 503/
    );
    vi.unstubAllGlobals();
  });
});

function createWorkspaceWithBrief() {
  const workspace = createDemoWorkspace();
  return { ...workspace, ...buildApprovePlanSlotPatch(workspace, workspace.contentPlanItems[0].id) };
}
