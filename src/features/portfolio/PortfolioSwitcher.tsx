import type { BlogProject, PortfolioState, UserAccount } from '../../domain/portfolio/types';

export function PortfolioSwitcher({
  activeProject,
  activeUser,
  accessibleProjects,
  portfolio,
  onProjectChange,
  onUserChange
}: {
  activeProject: BlogProject;
  activeUser: UserAccount;
  accessibleProjects: BlogProject[];
  portfolio: PortfolioState;
  onProjectChange: (projectId: string) => void;
  onUserChange: (userId: string) => void;
}) {
  return (
    <section className="portfolio-switcher" data-testid="portfolio-switcher" aria-label="Портфель блогов">
      <div className="portfolio-switcher-main">
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
      </div>
      <div className="portfolio-project-meta" aria-label="Текущий проект">
        <strong>{activeProject.title}</strong>
        <span>{activeProject.language}</span>
        <span>{activeProject.benchmarkRole === 'demo' ? 'demo' : activeProject.status}</span>
      </div>
    </section>
  );
}
