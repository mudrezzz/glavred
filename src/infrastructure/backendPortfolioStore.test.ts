import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  BackendPortfolioAuthRequiredError,
  BackendPortfolioStore,
  BackendPortfolioUnavailableError
} from './backendPortfolioStore';

function jsonResponse(payload: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => payload
  } as Response;
}

describe('BackendPortfolioStore', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('loads authenticated user projects and project-scoped workspaces', async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          user: {
            id: 'user-founder-editor',
            displayName: 'Founder',
            email: 'founder@example.test',
            status: 'active',
            createdAt: '2026-06-30T00:00:00Z'
          }
        })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          projects: [
            {
              project: {
                id: 'project-ai-design-patterns',
                ownerUserId: 'user-founder-editor',
                title: 'AI Design Patterns',
                description: 'Research-heavy blog.',
                language: 'en',
                status: 'active',
                benchmarkRole: 'demo',
                createdAt: '2026-06-30T00:00:00Z',
                updatedAt: '2026-06-30T00:00:00Z'
              },
              membership: {
                id: 'membership-founder-ai-design-patterns',
                userId: 'user-founder-editor',
                projectId: 'project-ai-design-patterns',
                role: 'owner',
                status: 'active'
              }
            }
          ]
        })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          projectId: 'project-ai-design-patterns',
          workspace: { projectProfile: { name: 'Backend AI Design Patterns' } }
        })
      );
    vi.stubGlobal('fetch', fetcher);

    const portfolio = await new BackendPortfolioStore().load();

    expect(portfolio.users).toHaveLength(1);
    expect(portfolio.projects).toHaveLength(1);
    expect(portfolio.activeProjectId).toBe('project-ai-design-patterns');
    expect(portfolio.workspacesByProjectId['project-ai-design-patterns'].projectProfile.name).toBe(
      'Backend AI Design Patterns'
    );
    expect(fetcher).toHaveBeenCalledWith(
      'http://localhost:8000/api/users/me',
      expect.objectContaining({ credentials: 'include' })
    );
    expect(fetcher).toHaveBeenCalledWith(
      'http://localhost:8000/api/projects?includeArchived=true',
      expect.objectContaining({ credentials: 'include' })
    );
  });

  it('creates and updates projects through project lifecycle endpoints', async () => {
    const fetcher = vi.fn().mockResolvedValue(jsonResponse({}));
    vi.stubGlobal('fetch', fetcher);
    const store = new BackendPortfolioStore();

    await store.createProject({ title: 'New blog', description: 'Draft', language: 'en' });
    await store.updateProject('project-new', { title: 'Renamed', status: 'archived' });

    expect(fetcher).toHaveBeenNthCalledWith(
      1,
      'http://localhost:8000/api/projects',
      expect.objectContaining({
        body: JSON.stringify({ title: 'New blog', description: 'Draft', language: 'en' }),
        method: 'POST'
      })
    );
    expect(fetcher).toHaveBeenNthCalledWith(
      2,
      'http://localhost:8000/api/projects/project-new',
      expect.objectContaining({
        body: JSON.stringify({ title: 'Renamed', status: 'archived' }),
        method: 'PATCH'
      })
    );
  });

  it('maps 401 to auth required', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({}, 401)));

    await expect(new BackendPortfolioStore().load()).rejects.toBeInstanceOf(BackendPortfolioAuthRequiredError);
  });

  it('maps network failure to backend unavailable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('failed')));

    await expect(new BackendPortfolioStore().load()).rejects.toBeInstanceOf(BackendPortfolioUnavailableError);
  });
});
