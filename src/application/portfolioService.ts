import type { BlogProject, PortfolioState, UserAccount } from '../domain/portfolio/types';
import type { WorkspaceState } from '../domain/workspace/types';

export type WorkspaceNormalizer = (workspace: Partial<WorkspaceState>) => WorkspaceState;

export function getActiveUser(portfolio: PortfolioState): UserAccount {
  return portfolio.users.find((user) => user.id === portfolio.activeUserId) ?? portfolio.users[0];
}

export function getAccessibleProjects(portfolio: PortfolioState, userId = portfolio.activeUserId): BlogProject[] {
  const accessibleProjectIds = new Set(
    portfolio.memberships
      .filter((membership) => membership.userId === userId && membership.status === 'active')
      .map((membership) => membership.projectId)
  );
  return portfolio.projects.filter((project) => project.status === 'active' && accessibleProjectIds.has(project.id));
}

export function getArchivedProjects(portfolio: PortfolioState, userId = portfolio.activeUserId): BlogProject[] {
  const accessibleProjectIds = new Set(
    portfolio.memberships
      .filter((membership) => membership.userId === userId && membership.status === 'active')
      .map((membership) => membership.projectId)
  );
  return portfolio.projects.filter((project) => project.status === 'archived' && accessibleProjectIds.has(project.id));
}

export function getActiveProject(portfolio: PortfolioState): BlogProject {
  const accessibleProjects = getAccessibleProjects(portfolio);
  return accessibleProjects.find((project) => project.id === portfolio.activeProjectId) ?? accessibleProjects[0] ?? portfolio.projects[0];
}

export function getActiveWorkspace(portfolio: PortfolioState): WorkspaceState {
  const activeProject = getActiveProject(portfolio);
  return portfolio.workspacesByProjectId[activeProject.id] ?? Object.values(portfolio.workspacesByProjectId)[0];
}

export function selectPortfolioUser(portfolio: PortfolioState, userId: string): PortfolioState {
  const nextUserId = portfolio.users.some((user) => user.id === userId && user.status === 'active')
    ? userId
    : portfolio.users.find((user) => user.status === 'active')?.id ?? portfolio.activeUserId;
  const accessibleProjects = getAccessibleProjects(portfolio, nextUserId);
  const currentStillAccessible = accessibleProjects.some((project) => project.id === portfolio.activeProjectId);
  const activeProjectId = currentStillAccessible
    ? portfolio.activeProjectId
    : accessibleProjects[0]?.id ?? portfolio.activeProjectId;
  return { ...portfolio, activeUserId: nextUserId, activeProjectId, updatedAt: new Date().toISOString() };
}

export function selectPortfolioProject(portfolio: PortfolioState, projectId: string): PortfolioState {
  const accessibleProjects = getAccessibleProjects(portfolio);
  const activeProjectId = accessibleProjects.some((project) => project.id === projectId)
    ? projectId
    : accessibleProjects[0]?.id ?? portfolio.activeProjectId;
  return { ...portfolio, activeProjectId, updatedAt: new Date().toISOString() };
}

export function updateActiveProjectWorkspace(
  portfolio: PortfolioState,
  update: (workspace: WorkspaceState) => WorkspaceState
): PortfolioState {
  const activeProject = getActiveProject(portfolio);
  const currentWorkspace = getActiveWorkspace(portfolio);
  const nextWorkspace = update(currentWorkspace);
  return {
    ...portfolio,
    workspacesByProjectId: {
      ...portfolio.workspacesByProjectId,
      [activeProject.id]: nextWorkspace
    },
    updatedAt: nextWorkspace.updatedAt ?? new Date().toISOString()
  };
}

export function createPortfolioFromWorkspace(workspace: WorkspaceState): PortfolioState {
  const now = new Date().toISOString();
  return {
    activeUserId: 'local-user-owner',
    activeProjectId: 'project-legacy-workspace',
    users: [
      {
        id: 'local-user-owner',
        displayName: 'Local editor',
        email: 'editor@example.test',
        status: 'active',
        createdAt: now
      }
    ],
    projects: [
      {
        id: 'project-legacy-workspace',
        ownerUserId: 'local-user-owner',
        title: workspace.projectProfile?.name || 'Editorial workspace',
        description: 'Migrated local workspace.',
        language: 'ru',
        status: 'active',
        benchmarkRole: 'demo',
        createdAt: now,
        updatedAt: now
      }
    ],
    memberships: [
      {
        id: 'membership-local-user-owner-project-legacy-workspace',
        userId: 'local-user-owner',
        projectId: 'project-legacy-workspace',
        role: 'owner',
        status: 'active'
      }
    ],
    workspacesByProjectId: {
      'project-legacy-workspace': workspace
    },
    updatedAt: now
  };
}

export function normalizePortfolioState(
  saved: Partial<PortfolioState>,
  fallback: PortfolioState,
  normalizeWorkspace: WorkspaceNormalizer
): PortfolioState {
  const users = (saved.users?.length ? saved.users : fallback.users).map((user) => ({
    ...user,
    status: user.status ?? 'active',
    createdAt: user.createdAt ?? fallback.users.find((candidate) => candidate.id === user.id)?.createdAt ?? new Date().toISOString()
  }));
  const projects = (saved.projects?.length ? saved.projects : fallback.projects).map((project) => ({
    ...project,
    status: project.status ?? 'active',
    language: project.language ?? 'ru',
    description: project.description ?? '',
    createdAt: project.createdAt ?? new Date().toISOString(),
    updatedAt: project.updatedAt ?? new Date().toISOString()
  }));
  const memberships = (saved.memberships?.length ? saved.memberships : fallback.memberships).filter((membership) =>
    users.some((user) => user.id === membership.userId) && projects.some((project) => project.id === membership.projectId)
  );
  const workspacesByProjectId = projects.reduce<Record<string, WorkspaceState>>((acc, project) => {
    const savedWorkspace = saved.workspacesByProjectId?.[project.id];
    const fallbackWorkspace = fallback.workspacesByProjectId[project.id] ?? Object.values(fallback.workspacesByProjectId)[0];
    acc[project.id] = normalizeWorkspace(savedWorkspace ?? fallbackWorkspace);
    return acc;
  }, {});
  const normalized = {
    ...fallback,
    ...saved,
    users,
    projects,
    memberships: memberships.length > 0 ? memberships : fallback.memberships,
    workspacesByProjectId,
    activeUserId: saved.activeUserId ?? fallback.activeUserId,
    activeProjectId: saved.activeProjectId ?? fallback.activeProjectId,
    updatedAt: saved.updatedAt ?? fallback.updatedAt
  };
  return selectPortfolioProject(selectPortfolioUser(normalized, normalized.activeUserId), normalized.activeProjectId);
}
