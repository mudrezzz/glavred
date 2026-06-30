import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { getAccessibleProjects, getArchivedProjects } from '../../application/portfolioService';
import { createDemoPortfolio } from '../../fixtures/demoPortfolio';
import { ProjectDashboardView } from './ProjectDashboardView';

describe('ProjectDashboardView', () => {
  it('opens, creates, renames, and archives projects', async () => {
    const portfolio = createDemoPortfolio();
    const activeProjects = getAccessibleProjects(portfolio);
    const onOpenProject = vi.fn();
    const onCreateProject = vi.fn().mockResolvedValue(undefined);
    const onRenameProject = vi.fn().mockResolvedValue(undefined);
    const onArchiveProject = vi.fn().mockResolvedValue(undefined);

    render(
      <ProjectDashboardView
        activeProjects={activeProjects}
        archivedProjects={getArchivedProjects(portfolio)}
        activeUser={portfolio.users[0]}
        backendStatus="localFallback"
        portfolio={portfolio}
        onArchiveProject={onArchiveProject}
        onCreateProject={onCreateProject}
        onLogout={vi.fn()}
        onOpenProject={onOpenProject}
        onRenameProject={onRenameProject}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: 'Новый проект' }));
    fireEvent.change(screen.getByLabelText('Название проекта'), { target: { value: 'New blog' } });
    fireEvent.change(screen.getByLabelText('Описание проекта'), { target: { value: 'New description' } });
    fireEvent.click(screen.getByRole('button', { name: 'Создать' }));
    await waitFor(() =>
      expect(onCreateProject).toHaveBeenCalledWith({
        title: 'New blog',
        description: 'New description',
        language: 'ru'
      })
    );

    fireEvent.click(screen.getAllByLabelText('Действия проекта')[0]);
    fireEvent.click(screen.getAllByRole('button', { name: 'Переименовать' })[0]);
    fireEvent.change(screen.getByLabelText('Новое название'), { target: { value: 'Renamed blog' } });
    fireEvent.click(screen.getByRole('button', { name: 'Сохранить' }));
    await waitFor(() => expect(onRenameProject).toHaveBeenCalledWith(activeProjects[0].id, 'Renamed blog', expect.any(String)));

    fireEvent.click(screen.getAllByLabelText('Действия проекта')[0]);
    fireEvent.click(screen.getAllByRole('button', { name: 'В архив' })[0]);
    await waitFor(() => expect(onArchiveProject).toHaveBeenCalledWith(activeProjects[0].id));

    fireEvent.click(screen.getAllByRole('button', { name: 'Открыть кабинет' })[0]);
    expect(onOpenProject).toHaveBeenCalledWith(activeProjects[0].id);
  });
});
