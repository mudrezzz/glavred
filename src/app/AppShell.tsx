import type { ReactNode } from 'react';
import type { WorkspaceSection, WorkspaceState } from '../domain/editorialWorkspace';
import { Icon } from '../shared/ui/Icon';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export function AppShell({
  active,
  chatOpen,
  children,
  overlay,
  portfolioSwitcher,
  suggestionCount,
  toast,
  workspace,
  onNav,
  onOpenChat,
  onReset
}: {
  active: WorkspaceSection;
  chatOpen: boolean;
  children: ReactNode;
  overlay?: ReactNode;
  portfolioSwitcher?: ReactNode;
  suggestionCount: number;
  toast: string;
  workspace: WorkspaceState;
  onNav: (section: WorkspaceSection) => void;
  onOpenChat: () => void;
  onReset: () => void;
}) {
  return (
    <div className="app">
      <Sidebar active={active} onNav={onNav} workspace={workspace} />
      <main className="main">
        {portfolioSwitcher}
        <Topbar
          active={active}
          chatOpen={chatOpen}
          suggestionCount={suggestionCount}
          onOpenChat={onOpenChat}
          onReset={onReset}
        />
        <div className="scroll">{children}</div>
      </main>
      {overlay}
      {toast ? (
        <div className="toast" role="status">
          <Icon name="check" size={17} />
          {toast}
        </div>
      ) : null}
    </div>
  );
}
