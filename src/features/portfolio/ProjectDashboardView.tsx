import { useMemo, useState } from 'react';
import type { BlogProject, PortfolioState, UserAccount } from '../../domain/portfolio/types';
import type { PortfolioBackendStatus } from '../../app/useBackendPortfolioBridge';
import type { ProjectLifecycleInput } from '../../application/portfolioLifecycleService';
import type { WorkspaceState } from '../../domain/workspace/types';

interface ProjectDashboardViewProps {
  activeProjects: BlogProject[];
  archivedProjects: BlogProject[];
  activeUser: UserAccount;
  backendStatus: PortfolioBackendStatus;
  portfolio: PortfolioState;
  onArchiveProject: (projectId: string) => Promise<void>;
  onCreateProject: (input: ProjectLifecycleInput) => Promise<void>;
  onLogout: () => void;
  onOpenProject: (projectId: string) => void;
  onRenameProject: (projectId: string, title: string, description: string) => Promise<void>;
}

export function ProjectDashboardView({
  activeProjects,
  archivedProjects,
  activeUser,
  backendStatus,
  portfolio,
  onArchiveProject,
  onCreateProject,
  onLogout,
  onOpenProject,
  onRenameProject
}: ProjectDashboardViewProps) {
  const [filter, setFilter] = useState<'active' | 'archived'>('active');
  const [creating, setCreating] = useState(false);
  const [editingProjectId, setEditingProjectId] = useState<string | null>(null);
  const projects = filter === 'active' ? activeProjects : archivedProjects;

  return (
    <main className="project-dashboard" data-testid="project-dashboard">
      <header className="project-dashboard-header">
        <div>
          <p className="eyebrow">Портфель блогов</p>
          <h1>Проекты</h1>
          <p>
            {activeUser.displayName} ·{' '}
            {backendStatus === 'authenticated' ? 'backend session' : 'local fallback'}
          </p>
        </div>
        <div className="project-dashboard-actions">
          {backendStatus === 'authenticated' ? (
            <button type="button" className="btn btn-sec" onClick={onLogout}>
              Выйти
            </button>
          ) : null}
          <button type="button" className="btn btn-pri" onClick={() => setCreating((current) => !current)}>
            Новый проект
          </button>
        </div>
      </header>

      {creating ? <ProjectCreateForm onCreate={onCreateProject} /> : null}

      <div className="project-dashboard-toolbar" aria-label="Фильтр проектов">
        <button
          type="button"
          className={filter === 'active' ? 'active' : ''}
          onClick={() => setFilter('active')}
        >
          Активные · {activeProjects.length}
        </button>
        <button
          type="button"
          className={filter === 'archived' ? 'active' : ''}
          onClick={() => setFilter('archived')}
        >
          Архив · {archivedProjects.length}
        </button>
      </div>

      <section className="project-dashboard-grid" aria-label="Проекты пользователя">
        {projects.map((project) => (
          <ProjectCard
            key={project.id}
            editing={editingProjectId === project.id}
            project={project}
            workspace={portfolio.workspacesByProjectId[project.id]}
            onArchiveProject={onArchiveProject}
            onEdit={() => setEditingProjectId(project.id)}
            onOpenProject={onOpenProject}
            onRenameProject={async (title, description) => {
              await onRenameProject(project.id, title, description);
              setEditingProjectId(null);
            }}
            onStopEdit={() => setEditingProjectId(null)}
          />
        ))}
        {projects.length === 0 ? (
          <div className="project-dashboard-empty">
            {filter === 'active' ? 'Активных проектов нет.' : 'Архив пуст.'}
          </div>
        ) : null}
      </section>
    </main>
  );
}

function ProjectCreateForm({ onCreate }: { onCreate: (input: ProjectLifecycleInput) => Promise<void> }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('ru');

  return (
    <form
      className="project-dashboard-form"
      onSubmit={async (event) => {
        event.preventDefault();
        await onCreate({ title, description, language });
        setTitle('');
        setDescription('');
      }}
    >
      <input
        aria-label="Название проекта"
        value={title}
        placeholder="Название блога"
        onChange={(event) => setTitle(event.target.value)}
      />
      <input
        aria-label="Описание проекта"
        value={description}
        placeholder="Короткое описание"
        onChange={(event) => setDescription(event.target.value)}
      />
      <select aria-label="Язык проекта" value={language} onChange={(event) => setLanguage(event.target.value)}>
        <option value="ru">Русский</option>
        <option value="en">English</option>
      </select>
      <button type="submit" className="btn btn-pri">
        Создать
      </button>
    </form>
  );
}

function ProjectCard({
  editing,
  project,
  workspace,
  onArchiveProject,
  onEdit,
  onOpenProject,
  onRenameProject,
  onStopEdit
}: {
  editing: boolean;
  project: BlogProject;
  workspace?: WorkspaceState;
  onArchiveProject: (projectId: string) => Promise<void>;
  onEdit: () => void;
  onOpenProject: (projectId: string) => void;
  onRenameProject: (title: string, description: string) => Promise<void>;
  onStopEdit: () => void;
}) {
  const [title, setTitle] = useState(project.title);
  const [description, setDescription] = useState(project.description);
  const summary = useMemo(() => workspaceSummary(workspace), [workspace]);

  if (editing) {
    return (
      <article className="project-card editing" data-testid={`project-card-${project.id}`}>
        <input aria-label="Новое название" value={title} onChange={(event) => setTitle(event.target.value)} />
        <textarea
          aria-label="Новое описание"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
        <div className="project-card-actions">
          <button type="button" className="btn btn-pri" onClick={() => onRenameProject(title, description)}>
            Сохранить
          </button>
          <button type="button" className="btn btn-sec" onClick={onStopEdit}>
            Отмена
          </button>
        </div>
      </article>
    );
  }

  return (
    <article
      className="project-card"
      data-testid={`project-card-${project.id}`}
      onClick={() => onOpenProject(project.id)}
    >
      <div className="project-card-head">
        <div>
          <h2>{project.title}</h2>
          <p>{project.description || 'Без описания'}</p>
        </div>
        <details className="project-card-menu" onClick={(event) => event.stopPropagation()}>
          <summary aria-label="Действия проекта">...</summary>
          <button type="button" onClick={onEdit}>
            Переименовать
          </button>
          {project.status === 'active' ? (
            <button type="button" onClick={() => onArchiveProject(project.id)}>
              В архив
            </button>
          ) : null}
        </details>
      </div>
      <dl className="project-card-meta">
        <div>
          <dt>Язык</dt>
          <dd>{project.language}</dd>
        </div>
        <div>
          <dt>Статус</dt>
          <dd>{project.status === 'active' ? 'Активный' : 'Архив'}</dd>
        </div>
        <div>
          <dt>Роль</dt>
          <dd>{project.benchmarkRole ?? 'real'}</dd>
        </div>
        <div>
          <dt>Обновлен</dt>
          <dd>{formatDate(project.updatedAt)}</dd>
        </div>
      </dl>
      <p className="project-card-summary">{summary}</p>
      <button type="button" className="btn btn-pri" onClick={() => onOpenProject(project.id)}>
        Открыть кабинет
      </button>
    </article>
  );
}

function workspaceSummary(workspace?: WorkspaceState): string {
  if (!workspace) return 'Workspace пока не загружен.';
  return [
    `${workspace.authorNotes?.length ?? 0} заметок`,
    `${workspace.topics?.length ?? 0} тем`,
    `${workspace.fabulas?.length ?? 0} фабул`,
    `${workspace.sourceSignals?.length ?? 0} сигналов`
  ].join(' · ');
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('ru', { day: '2-digit', month: '2-digit', year: '2-digit' }).format(
    new Date(value)
  );
}
