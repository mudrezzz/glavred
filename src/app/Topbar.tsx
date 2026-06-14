import type { WorkspaceSection } from '../domain/editorialWorkspace';
import { Icon } from '../shared/ui/Icon';
import { TITLES } from './navigation';

export function Topbar({
  active,
  chatOpen,
  suggestionCount,
  onOpenChat,
  onReset
}: {
  active: WorkspaceSection;
  chatOpen: boolean;
  suggestionCount: number;
  onOpenChat: () => void;
  onReset: () => void;
}) {
  const [title, subtitle] = TITLES[active];

  return (
    <header className="topbar">
      <div className="crumb">
        {title}
        <small>{subtitle}</small>
      </div>
      <div className="spacer" />
      <div className="search">
        <Icon name="search" size={16} />
        <input aria-label="Поиск" placeholder="Поиск по темам, фабулам..." />
      </div>
      <button className="icon-btn" type="button" aria-label="Уведомления">
        <Icon name="bell" />
        <span className="dot" />
      </button>
      <button
        className={`btn btn-sec btn-sm assistant-topbar-btn${chatOpen ? ' active' : ''}`}
        data-testid="context-chat-topbar-trigger"
        type="button"
        aria-expanded={chatOpen}
        onClick={onOpenChat}
      >
        <Icon name="spark" size={14} />
        Помощник
        {suggestionCount > 0 ? <span className="assistant-count">{suggestionCount}</span> : null}
      </button>
      <button className="icon-btn" type="button" aria-label="Сбросить демо" onClick={onReset} title="Сбросить демо">
        <Icon name="reset" size={14} />
      </button>
    </header>
  );
}
