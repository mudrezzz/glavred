import type { BlogProject, PortfolioState } from '../domain/portfolio/types';
import type { WorkspaceState } from '../domain/workspace/types';

export interface ProjectLifecycleInput {
  title: string;
  description?: string;
  language?: string;
}

export type ProjectLifecyclePatch = Partial<Pick<BlogProject, 'title' | 'description' | 'status'>>;

export function createProjectInPortfolio(
  portfolio: PortfolioState,
  input: ProjectLifecycleInput,
  workspace: WorkspaceState
): PortfolioState {
  const now = new Date().toISOString();
  const title = input.title.trim() || 'Новый блог';
  const projectId = `project-local-${Date.now().toString(36)}`;
  const project: BlogProject = {
    id: projectId,
    ownerUserId: portfolio.activeUserId,
    title,
    description: input.description?.trim() ?? '',
    language: input.language?.trim() || 'ru',
    status: 'active',
    benchmarkRole: 'real',
    createdAt: now,
    updatedAt: now
  };
  return {
    ...portfolio,
    activeProjectId: projectId,
    projects: [...portfolio.projects, project],
    memberships: [
      ...portfolio.memberships,
      {
        id: `membership-${portfolio.activeUserId}-${projectId}`,
        userId: portfolio.activeUserId,
        projectId,
        role: 'owner',
        status: 'active'
      }
    ],
    workspacesByProjectId: {
      ...portfolio.workspacesByProjectId,
      [projectId]: {
        ...workspace,
        projectProfile: { ...workspace.projectProfile, name: title },
        updatedAt: now
      }
    },
    updatedAt: now
  };
}

export function updateProjectInPortfolio(
  portfolio: PortfolioState,
  projectId: string,
  patch: ProjectLifecyclePatch
): PortfolioState {
  const now = new Date().toISOString();
  const nextProjects = portfolio.projects.map((project) =>
    project.id === projectId
      ? {
          ...project,
          ...cleanProjectPatch(patch),
          updatedAt: now
        }
      : project
  );
  const currentWorkspace = portfolio.workspacesByProjectId[projectId];
  const title = patch.title?.trim();
  return {
    ...portfolio,
    projects: nextProjects,
    activeProjectId:
      portfolio.activeProjectId === projectId && patch.status === 'archived'
        ? nextProjects.find(
            (project) =>
              project.status === 'active' &&
              portfolio.memberships.some(
                (membership) =>
                  membership.userId === portfolio.activeUserId &&
                  membership.projectId === project.id &&
                  membership.status === 'active'
              )
          )?.id ?? portfolio.activeProjectId
        : portfolio.activeProjectId,
    workspacesByProjectId:
      currentWorkspace && title
        ? {
            ...portfolio.workspacesByProjectId,
            [projectId]: {
              ...currentWorkspace,
              projectProfile: { ...currentWorkspace.projectProfile, name: title },
              updatedAt: now
            }
          }
        : portfolio.workspacesByProjectId,
    updatedAt: now
  };
}

function cleanProjectPatch(patch: ProjectLifecyclePatch): ProjectLifecyclePatch {
  return {
    ...(patch.title !== undefined ? { title: patch.title.trim() || 'Новый блог' } : {}),
    ...(patch.description !== undefined ? { description: patch.description.trim() } : {}),
    ...(patch.status !== undefined ? { status: patch.status } : {})
  };
}
