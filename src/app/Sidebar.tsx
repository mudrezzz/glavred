import type { WorkspaceSection, WorkspaceState } from '../domain/editorialWorkspace';
import { Icon } from '../shared/ui/Icon';
import { NAV } from './navigation';

export function Sidebar({
  active,
  onNav,
  workspace
}: {
  active: WorkspaceSection;
  onNav: (section: WorkspaceSection) => void;
  workspace: WorkspaceState;
}) {
  return (
    <aside className="side">
      <div className="brand">
        <span className="brand-mark">Г</span>
        <span className="wm">Главред</span>
      </div>
      <div className="nav-label">Редакция</div>
      {NAV.map((item) => (
        <button
          key={item.id}
          className={`nav-item${active === item.id ? ' active' : ''}${item.disabled ? ' muted' : ''}`}
          onClick={() => onNav(item.id)}
          type="button"
        >
          <Icon name={item.icon} />
          <span>{item.label}</span>
          {item.id === 'memory' ? <span className="count">{workspace.authorNotes.length}</span> : null}
          {item.id === 'signals' ? <span className="count">{workspace.sourceSignals.length}</span> : null}
          {item.id === 'plan' ? <span className="count">{workspace.contentPlanItems.length}</span> : null}
          {item.id !== 'memory' && item.id !== 'signals' && item.id !== 'plan' && item.count ? (
            <span className="count">{item.count}</span>
          ) : null}
        </button>
      ))}
      <div className="side-foot">
        <div className="author">
          <div className="ava">АК</div>
          <div>
            <b>{workspace.editorialModel.author.split(' — ')[0]}</b>
            <span>Главный редактор</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
