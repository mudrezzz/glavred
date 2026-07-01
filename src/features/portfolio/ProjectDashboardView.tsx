import { useMemo, useState } from 'react';
import type { PortfolioBackendStatus } from '../../app/useBackendPortfolioBridge';
import type { ProjectLifecycleInput } from '../../application/portfolioLifecycleService';
import type { BlogProject, PortfolioState, UserAccount } from '../../domain/portfolio/types';
import type { WorkspaceState } from '../../domain/workspace/types';
import { Icon } from '../../shared/ui/Icon';

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
  const gridClassName = `project-dashboard-grid${projects.length === 1 ? ' single' : ''}`;
  const totalNotes = useMemo(
    () =>
      Object.values(portfolio.workspacesByProjectId).reduce(
        (count, workspace) => count + (workspace.authorNotes?.length ?? 0),
        0
      ),
    [portfolio.workspacesByProjectId]
  );

  return (
    <div className="app project-dashboard" data-testid="project-dashboard">
      <ProjectDashboardSidebar
        activeProjectsCount={activeProjects.length}
        activeUser={activeUser}
        archivedProjectsCount={archivedProjects.length}
        backendStatus={backendStatus}
        onLogout={onLogout}
      />
      <main className="main">
        <header className="topbar project-dashboard-topbar">
          <div className="crumb">
            Проекты <small>Портфель блогов</small>
          </div>
          <span className="spacer" />
        </header>

        <div className="scroll">
          <div className="project-dashboard-canvas" data-testid="project-dashboard-shell">
            <header className="project-dashboard-header">
              <div>
                <p className="eyebrow">Портфель блогов</p>
                <h1>Проекты</h1>
                <p>Выберите блог, создайте новый кабинет или вернитесь к архиву.</p>
              </div>
            </header>

            <section className="project-dashboard-stats" aria-label="Сводка портфеля">
              <div>
                <span>Активные</span>
                <b>{activeProjects.length}</b>
              </div>
              <div>
                <span>Архив</span>
                <b>{archivedProjects.length}</b>
              </div>
              <div>
                <span>Память автора</span>
                <b>{totalNotes}</b>
              </div>
            </section>

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

            <div className="project-dashboard-action-row" data-testid="project-dashboard-action-row">
              <button type="button" className="btn btn-pri" onClick={() => setCreating((current) => !current)}>
                <Icon name="plus" />
                Новый проект
              </button>
            </div>

            {creating ? <ProjectCreateForm onCreate={onCreateProject} /> : null}

            <section className={gridClassName} aria-label="Проекты пользователя" data-testid="project-dashboard-grid">
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
          </div>
        </div>
      </main>
    </div>
  );
}

function ProjectDashboardSidebar({
  activeProjectsCount,
  activeUser,
  archivedProjectsCount,
  backendStatus,
  onLogout
}: {
  activeProjectsCount: number;
  activeUser: UserAccount;
  archivedProjectsCount: number;
  backendStatus: PortfolioBackendStatus;
  onLogout: () => void;
}) {
  return (
    <aside className="side project-dashboard-side" aria-label="Управление портфелем">
      <div className="brand">
        <span className="brand-mark">Г</span>
        <span className="wm">Главред</span>
      </div>

      <div className="nav-label">Портфель</div>
      <nav className="project-dashboard-nav" aria-label="Разделы аккаунта">
        <button type="button" className="nav-item active" aria-current="page">
          <Icon name="model" />
          <span>Проекты</span>
          <span className="count">{activeProjectsCount}</span>
        </button>
        <button type="button" className="nav-item muted" disabled>
          <Icon name="memory" />
          <span>Аккаунт</span>
        </button>
        <button type="button" className="nav-item muted" disabled>
          <Icon name="analytics" />
          <span>Статистика</span>
        </button>
        <button type="button" className="nav-item muted" disabled>
          <Icon name="release" />
          <span>Биллинг</span>
        </button>
        <button type="button" className="nav-item muted" disabled>
          <Icon name="brief" />
          <span>Настройки</span>
        </button>
      </nav>

      <div className="side-foot">
        <div className="project-dashboard-owner" data-testid="project-dashboard-owner">
          <div className="author">
            <span className="ava dashboard-account-avatar">{initials(activeUser.displayName)}</span>
            <div>
              <b>{activeUser.displayName}</b>
              <span>Владелец профиля</span>
            </div>
          </div>
          <div className="project-dashboard-owner-meta">
            <span>{activeUser.email}</span>
            <span>{backendStatus === 'authenticated' ? 'Backend session' : 'Local fallback'}</span>
            <span>Архив · {archivedProjectsCount}</span>
          </div>
          {backendStatus === 'authenticated' ? (
            <button type="button" className="btn btn-sec project-dashboard-logout" onClick={onLogout}>
              Выйти
            </button>
          ) : null}
        </div>
      </div>
    </aside>
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
          <div className="project-card-menu-panel">
            <button type="button" onClick={onEdit}>
              Переименовать
            </button>
            {project.status === 'active' ? (
              <button type="button" onClick={() => onArchiveProject(project.id)}>
                В архив
              </button>
            ) : null}
          </div>
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
      <button
        type="button"
        className="btn btn-pri"
        onClick={(event) => {
          event.stopPropagation();
          onOpenProject(project.id);
        }}
      >
        Открыть кабинет
      </button>
    </article>
  );
}

function initials(value: string): string {
  const words = value.trim().split(/\s+/).filter(Boolean);
  return (words[0]?.[0] ?? 'G').toUpperCase() + (words[1]?.[0] ?? '').toUpperCase();
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
