import { normalizePortfolioState } from '../application/portfolioService';
import type {
  BlogProject,
  PortfolioState,
  ProjectMembership,
  UserAccount
} from '../domain/portfolio/types';
import type { WorkspaceState } from '../domain/workspace/types';
import { createDemoPortfolio } from '../fixtures/demoPortfolio';
import { normalizeWorkspace } from './localWorkspaceStore';

export class BackendPortfolioAuthRequiredError extends Error {
  constructor() {
    super('backend-auth-required');
  }
}

export class BackendPortfolioUnavailableError extends Error {
  constructor() {
    super('backend-unavailable');
  }
}

interface BackendUserResponse {
  id: string;
  displayName: string;
  email?: string;
  avatarUrl?: string | null;
  status: UserAccount['status'];
  createdAt: string;
}

interface BackendProjectAccessResponse {
  project: BlogProject;
  membership: ProjectMembership;
}

interface BackendWorkspaceResponse {
  projectId: string;
  workspace: Partial<WorkspaceState>;
}

export interface BackendProjectCreateInput {
  title: string;
  description?: string;
  language?: string;
}

export type BackendProjectUpdateInput = Partial<Pick<BlogProject, 'title' | 'description' | 'status'>>;

export class BackendPortfolioStore {
  async load(): Promise<PortfolioState> {
    const me = await this.request<{ user: BackendUserResponse }>('/api/users/me');
    const projectsPayload = await this.request<{ projects: BackendProjectAccessResponse[] }>(
      '/api/projects?includeArchived=true'
    );
    const users = [mapUser(me.user)];
    const projects = projectsPayload.projects.map((item) => item.project);
    const memberships = projectsPayload.projects.map((item) => item.membership);
    const fallback = createDemoPortfolio();
    const workspacesByProjectId: Record<string, WorkspaceState> = {};

    for (const project of projects) {
      const snapshot = await this.request<BackendWorkspaceResponse>(`/api/projects/${encodeURIComponent(project.id)}/workspace`);
      const fallbackWorkspace = fallback.workspacesByProjectId[project.id] ?? Object.values(fallback.workspacesByProjectId)[0];
      workspacesByProjectId[project.id] = normalizeWorkspace(mergeWorkspace(fallbackWorkspace, snapshot.workspace));
    }

    return normalizePortfolioState(
      {
        activeUserId: users[0]?.id,
        activeProjectId: projects[0]?.id,
        users,
        projects,
        memberships,
        workspacesByProjectId,
        updatedAt: new Date().toISOString()
      },
      fallback,
      normalizeWorkspace
    );
  }

  async login(email: string, password: string): Promise<PortfolioState> {
    await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    return this.load();
  }

  async logout(): Promise<void> {
    await this.request('/api/auth/logout', { method: 'POST' });
  }

  async createProject(input: BackendProjectCreateInput): Promise<void> {
    await this.request('/api/projects', {
      method: 'POST',
      body: JSON.stringify({
        title: input.title,
        description: input.description ?? '',
        language: input.language ?? 'ru'
      })
    });
  }

  async updateProject(projectId: string, patch: BackendProjectUpdateInput): Promise<void> {
    await this.request(`/api/projects/${encodeURIComponent(projectId)}`, {
      method: 'PATCH',
      body: JSON.stringify(patch)
    });
  }

  async save(portfolio: PortfolioState): Promise<void> {
    const workspace = portfolio.workspacesByProjectId[portfolio.activeProjectId];
    if (!workspace) return;
    await this.request(`/api/projects/${encodeURIComponent(portfolio.activeProjectId)}/workspace`, {
      method: 'PUT',
      body: JSON.stringify({ workspace })
    });
  }

  private async request<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
    let response: Response;
    try {
      response = await fetch(`${apiBaseUrl()}${path}`, {
        ...init,
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...(init.headers ?? {})
        }
      });
    } catch {
      throw new BackendPortfolioUnavailableError();
    }
    if (response.status === 401) throw new BackendPortfolioAuthRequiredError();
    if (!response.ok) throw new Error(`backend-portfolio-error-${response.status}`);
    return (await response.json()) as T;
  }
}

function mapUser(user: BackendUserResponse): UserAccount {
  return {
    id: user.id,
    displayName: user.displayName,
    email: user.email,
    avatarUrl: user.avatarUrl ?? undefined,
    status: user.status,
    createdAt: user.createdAt
  };
}

function mergeWorkspace(fallback: WorkspaceState, snapshot: Partial<WorkspaceState>): Partial<WorkspaceState> {
  return {
    ...fallback,
    ...snapshot,
    projectProfile: {
      ...fallback.projectProfile,
      ...snapshot.projectProfile
    }
  };
}

function apiBaseUrl(): string {
  const env = (import.meta as unknown as { env?: { VITE_API_BASE_URL?: string } }).env;
  return (env?.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
}
