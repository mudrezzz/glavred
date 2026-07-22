import { afterEach, describe, expect, it, vi } from 'vitest';
import { createDemoPortfolio } from '../fixtures/demoPortfolio';
import {
  BackendPortfolioAuthRequiredError,
  BackendPortfolioIntegrityError,
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
                title: 'Опытный цех «Сборочная»',
                description: 'Research-heavy industrial AI workshop.',
                language: 'ru',
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
          workspace: { projectProfile: { name: 'Backend Сборочная' } }
        })
      );
    vi.stubGlobal('fetch', fetcher);

    const portfolio = await new BackendPortfolioStore().load();

    expect(portfolio.users).toHaveLength(1);
    expect(portfolio.projects).toHaveLength(1);
    expect(portfolio.activeProjectId).toBe('project-ai-design-patterns');
    expect(portfolio.workspacesByProjectId['project-ai-design-patterns'].projectProfile.name).toBe(
      'Backend Сборочная'
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

  it('ends the backend session with credentials included', async () => {
    const fetcher = vi.fn().mockResolvedValue(jsonResponse({ status: 'ok' }));
    vi.stubGlobal('fetch', fetcher);

    await new BackendPortfolioStore().logout();

    expect(fetcher).toHaveBeenCalledWith(
      'http://localhost:8000/api/auth/logout',
      expect.objectContaining({ method: 'POST', credentials: 'include' })
    );
  });

  it('uses the browser loopback hostname so the session cookie remains same-site', async () => {
    vi.stubGlobal('location', { hostname: '127.0.0.1' });
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({}))
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
      .mockResolvedValueOnce(jsonResponse({ projects: [] }));
    vi.stubGlobal('fetch', fetcher);

    await new BackendPortfolioStore().login('founder@example.test', 'glavred-demo');

    expect(fetcher).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/auth/login',
      expect.objectContaining({ credentials: 'include' })
    );
    expect(fetcher).toHaveBeenNthCalledWith(
      2,
      'http://127.0.0.1:8000/api/users/me',
      expect.objectContaining({ credentials: 'include' })
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

  it('keeps workspace integrity failures distinct from backend unavailability', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse(
          {
            detail: {
              code: 'workspace-text-integrity-failed',
              operation: 'save',
              projectId: 'project-ai-design-patterns',
              snapshotId: null,
              blockingIssueCount: 1
            }
          },
          422
        )
      )
    );

    const promise = new BackendPortfolioStore().save({
      ...createDemoPortfolio(),
      activeProjectId: 'project-ai-design-patterns'
    });

    await expect(promise).rejects.toBeInstanceOf(BackendPortfolioIntegrityError);
    await expect(promise).rejects.toMatchObject({
      diagnostic: expect.objectContaining({ operation: 'save', blockingIssueCount: 1 })
    });
  });
});
