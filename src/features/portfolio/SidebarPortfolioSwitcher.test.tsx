import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import type { BlogProject, PortfolioState, UserAccount } from '../../domain/portfolio/types';
import { SidebarPortfolioSwitcher } from './SidebarPortfolioSwitcher';

const user: UserAccount = {
  id: 'user-founder-editor',
  displayName: 'Founder',
  email: 'founder@example.test',
  status: 'active',
  createdAt: '2026-06-30T00:00:00Z'
};

const project: BlogProject = {
  id: 'project-ai-design-patterns',
  ownerUserId: user.id,
  title: 'AI Design Patterns',
  description: 'Research-heavy blog.',
  language: 'en',
  status: 'active',
  benchmarkRole: 'demo',
  createdAt: '2026-06-30T00:00:00Z',
  updatedAt: '2026-06-30T00:00:00Z'
};

const portfolio = {
  activeUserId: user.id,
  activeProjectId: project.id,
  users: [user],
  projects: [project],
  memberships: [{ id: 'membership-1', userId: user.id, projectId: project.id, role: 'owner', status: 'active' }],
  workspacesByProjectId: {},
  updatedAt: '2026-06-30T00:00:00Z'
} as PortfolioState;

describe('SidebarPortfolioSwitcher', () => {
  it('shows backend status, dashboard action, and logout action', () => {
    const onLogout = vi.fn();
    const onOpenDashboard = vi.fn();

    render(
      <SidebarPortfolioSwitcher
        accessibleProjects={[project]}
        activeProject={project}
        activeUser={user}
        backendStatus="authenticated"
        portfolio={portfolio}
        onLogout={onLogout}
        onOpenDashboard={onOpenDashboard}
        onProjectChange={vi.fn()}
        onUserChange={vi.fn()}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /AI Design Patterns/i }));
    fireEvent.click(screen.getByRole('button', { name: 'Все проекты' }));
    fireEvent.click(screen.getByRole('button', { name: 'Выйти' }));

    expect(screen.getByText('backend session')).toBeInTheDocument();
    expect(onOpenDashboard).toHaveBeenCalledTimes(1);
    expect(onLogout).toHaveBeenCalledTimes(1);
  });

  it('keeps logout action available when backend state falls back after login', () => {
    const onLogout = vi.fn();

    render(
      <SidebarPortfolioSwitcher
        accessibleProjects={[project]}
        activeProject={project}
        activeUser={user}
        backendStatus="localFallback"
        portfolio={portfolio}
        onLogout={onLogout}
        onProjectChange={vi.fn()}
        onUserChange={vi.fn()}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /AI Design Patterns/i }));
    fireEvent.click(screen.getByRole('button', { name: 'Выйти' }));

    expect(onLogout).toHaveBeenCalledTimes(1);
  });
});
