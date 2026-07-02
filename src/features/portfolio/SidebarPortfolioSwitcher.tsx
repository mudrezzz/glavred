import { useMemo, useState } from 'react';
import type { BlogProject, PortfolioState, UserAccount } from '../../domain/portfolio/types';
import type { PortfolioBackendStatus } from '../../app/useBackendPortfolioBridge';
import { Icon } from '../../shared/ui/Icon';

export function SidebarPortfolioSwitcher({
  activeProject,
  activeUser,
  accessibleProjects,
  backendStatus,
  onLogout,
  onOpenDashboard,
  portfolio,
  onProjectChange,
  onUserChange
}: {
  activeProject: BlogProject;
  activeUser: UserAccount;
  accessibleProjects: BlogProject[];
  backendStatus?: PortfolioBackendStatus;
  portfolio: PortfolioState;
  onLogout?: () => void;
  onOpenDashboard?: () => void;
  onProjectChange: (projectId: string) => void;
  onUserChange: (userId: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const initials = useMemo(() => projectInitials(activeProject.title), [activeProject.title]);

  return (
    <div className={`sidebar-portfolio-switcher${open ? ' open' : ''}`} data-testid="portfolio-switcher">
      {open ? (
        <div id="sidebar-portfolio-panel" className="sidebar-portfolio-panel" data-testid="portfolio-switcher-panel">
          <label>
            <span>Пользователь</span>
            <select
              aria-label="Пользователь"
              data-testid="portfolio-user-select"
              value={activeUser.id}
              onChange={(event) => onUserChange(event.target.value)}
            >
              {portfolio.users
                .filter((user) => user.status === 'active')
                .map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.displayName}
                  </option>
                ))}
            </select>
          </label>
          <label>
            <span>Блог</span>
            <select
              aria-label="Блог"
              data-testid="portfolio-project-select"
              value={activeProject.id}
              onChange={(event) => onProjectChange(event.target.value)}
            >
              {accessibleProjects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.title}
                </option>
              ))}
            </select>
          </label>
          <div className="sidebar-portfolio-meta" aria-label="Текущий проект">
            <span>{activeProject.language}</span>
            <span>{activeProject.benchmarkRole === 'demo' ? 'demo' : activeProject.status}</span>
          </div>
          <div className="sidebar-portfolio-session">
            <span>{backendStatus === 'authenticated' ? 'backend session' : 'local fallback'}</span>
            {onOpenDashboard ? (
              <button type="button" onClick={onOpenDashboard}>
                Все проекты
              </button>
            ) : null}
            {onLogout ? (
              <button type="button" onClick={onLogout}>
                Выйти
              </button>
            ) : null}
          </div>
        </div>
      ) : null}
      <button
        className="sidebar-portfolio-trigger"
        type="button"
        aria-expanded={open}
        aria-controls="sidebar-portfolio-panel"
        onClick={() => setOpen((current) => !current)}
      >
        <span className="ava sidebar-portfolio-avatar">{initials}</span>
        <span className="sidebar-portfolio-text">
          <b>{activeProject.title}</b>
          <span>{activeUser.displayName}</span>
        </span>
        <span className="sidebar-portfolio-caret" aria-hidden="true">
          <Icon name="caret" size={15} />
        </span>
      </button>
    </div>
  );
}

function projectInitials(title: string): string {
  const words = title
    .replace(/[^\p{L}\p{N}\s]/gu, ' ')
    .split(/\s+/)
    .filter(Boolean);
  if (words.length === 0) return 'БЛ';
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return `${words[0][0]}${words[1][0]}`.toUpperCase();
}
