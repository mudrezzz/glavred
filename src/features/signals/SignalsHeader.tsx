import type { WorkspaceState } from '../../domain/editorialWorkspace';
import type { SignalsController } from './useSignalsController';

export function SignalsHeader({
  workspace,
  signalSummary
}: {
  workspace: WorkspaceState;
  signalSummary: SignalsController['signalSummary'];
}) {
  return (
    <section className="card project-profile-header signals-section-header" data-testid="signals-section-header">
      <div className="project-profile-main">
        <span className="mono-label">Материал</span>
        <h2>Сигналы</h2>
        <p>
          Радары собирают сырой материал для постов. Автор утверждает, архивирует или правит сигнал до того,
          как он станет кандидатом поста.
        </p>
      </div>
      <div className="project-profile-meta signals-header-stats">
        <div>
          <b>{workspace.radars.length}</b>
          <span>радаров</span>
        </div>
        <div>
          <b>{signalSummary.new}</b>
          <span>новых</span>
        </div>
        <div>
          <b>{signalSummary.approved}</b>
          <span>утверждено</span>
        </div>
      </div>
    </section>
  );
}
