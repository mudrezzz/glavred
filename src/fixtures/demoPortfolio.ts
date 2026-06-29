import { createPortfolioFromWorkspace } from '../application/portfolioService';
import type { PortfolioState } from '../domain/portfolio/types';
import type { WorkspaceState } from '../domain/workspace/types';
import { createDemoWorkspace } from './demoWorkspace';

export function createDemoPortfolio(): PortfolioState {
  const now = new Date().toISOString();
  const baseWorkspace = createDemoWorkspace({ includeSeededHitlLearning: true });

  return {
    activeUserId: 'user-founder-editor',
    activeProjectId: 'project-ai-design-patterns',
    users: [
      {
        id: 'user-founder-editor',
        displayName: 'Владелец портфеля',
        email: 'founder@example.test',
        status: 'active',
        createdAt: now
      },
      {
        id: 'user-product-editor',
        displayName: 'Редактор Главреда',
        email: 'glavred-editor@example.test',
        status: 'active',
        createdAt: now
      }
    ],
    projects: [
      {
        id: 'project-ai-design-patterns',
        ownerUserId: 'user-founder-editor',
        title: 'AI Design Patterns',
        description: 'Research-heavy blog about durable AI engineering and product design patterns.',
        language: 'en',
        status: 'active',
        benchmarkRole: 'demo',
        createdAt: now,
        updatedAt: now
      },
      {
        id: 'project-kasha-iz-topora',
        ownerUserId: 'user-founder-editor',
        title: 'Каша из топора',
        description: 'RevOps and Product Marketing Telegram-native author blog.',
        language: 'ru',
        status: 'active',
        benchmarkRole: 'demo',
        createdAt: now,
        updatedAt: now
      },
      {
        id: 'project-glavred-blog',
        ownerUserId: 'user-product-editor',
        title: 'Блог Главреда',
        description: 'Product philosophy and practical AI-native editorial methods.',
        language: 'ru',
        status: 'active',
        benchmarkRole: 'demo',
        createdAt: now,
        updatedAt: now
      }
    ],
    memberships: [
      {
        id: 'membership-founder-ai-design-patterns',
        userId: 'user-founder-editor',
        projectId: 'project-ai-design-patterns',
        role: 'owner',
        status: 'active'
      },
      {
        id: 'membership-founder-kasha',
        userId: 'user-founder-editor',
        projectId: 'project-kasha-iz-topora',
        role: 'owner',
        status: 'active'
      },
      {
        id: 'membership-product-editor-glavred',
        userId: 'user-product-editor',
        projectId: 'project-glavred-blog',
        role: 'owner',
        status: 'active'
      }
    ],
    workspacesByProjectId: {
      'project-ai-design-patterns': createProjectWorkspace(baseWorkspace, 'memory'),
      'project-kasha-iz-topora': createProjectWorkspace(baseWorkspace, 'memory'),
      'project-glavred-blog': createProjectWorkspace(baseWorkspace, 'memory')
    },
    updatedAt: now
  };
}

export function createDemoPortfolioFromWorkspace(workspace: WorkspaceState): PortfolioState {
  return createPortfolioFromWorkspace(workspace);
}

function createProjectWorkspace(
  baseWorkspace: WorkspaceState,
  activeSection: WorkspaceState['activeSection']
): WorkspaceState {
  return {
    ...(JSON.parse(JSON.stringify(baseWorkspace)) as WorkspaceState),
    activeSection,
    updatedAt: new Date().toISOString()
  };
}
