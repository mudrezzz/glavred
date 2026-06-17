import { useMemo, useState } from 'react';
import type { WorkspaceState } from '../../domain/editorialWorkspace';
import { EditorialWorkbench } from './EditorialWorkbench';
import { EditorialWorkGroupList, EditorialWorkQueueList } from './EditorialWorkQueueList';
import { EditorialWorkQueueToolbar } from './EditorialWorkQueueToolbar';
import {
  defaultEditorialWorkQueueFilters,
  filterEditorialWorkItems,
  groupEditorialWorkItems,
  type EditorialWorkGroupMode,
  type EditorialWorkQueueFilters,
  type EditorialWorkQueueViewMode
} from './editorialWorkQueueFilters';

export function EditView({
  workspace,
  onApproveBrief,
  onCreateDraft,
  onDraftChange,
  onGoPlan,
  onSelectWorkItem,
  onApproveFinal
}: {
  workspace: WorkspaceState;
  onApproveBrief: () => void;
  onCreateDraft: () => void;
  onDraftChange: (body: string) => void;
  onGoPlan: () => void;
  onSelectWorkItem: (workItemId: string) => void;
  onApproveFinal: () => void;
}) {
  const [filters, setFilters] = useState<EditorialWorkQueueFilters>(defaultEditorialWorkQueueFilters);
  const [viewMode, setViewMode] = useState<EditorialWorkQueueViewMode>('list');
  const [groupMode, setGroupMode] = useState<EditorialWorkGroupMode>('stage');
  const filteredItems = useMemo(
    () => filterEditorialWorkItems(workspace.editorialWorkItems, filters),
    [filters, workspace.editorialWorkItems]
  );
  const groups = useMemo(() => groupEditorialWorkItems(filteredItems, groupMode), [filteredItems, groupMode]);

  return (
    <div className="page wide fade-up">
      <section className="editorial-production-flow">
        <EditorialWorkQueueToolbar
          fabulas={workspace.fabulas}
          filters={filters}
          groupMode={groupMode}
          items={workspace.editorialWorkItems}
          topics={workspace.topics}
          viewMode={viewMode}
          onChangeFilters={setFilters}
          onChangeGroupMode={setGroupMode}
          onChangeViewMode={setViewMode}
        />
        {workspace.editorialWorkItems.length === 0 ? (
          <div className="card empty-state" data-testid="editorial-work-empty">
            В редакционной очереди пока нет утвержденных слотов. Утвердите слот в разделе «План», затем подготовьте фабулу поста.
          </div>
        ) : viewMode === 'groups' ? (
          <EditorialWorkGroupList
            groups={groups}
            selectedId={workspace.selectedEditorialWorkItemId}
            onGoPlan={onGoPlan}
            onSelect={onSelectWorkItem}
          />
        ) : (
          <EditorialWorkQueueList
            items={filteredItems}
            selectedId={workspace.selectedEditorialWorkItemId}
            onGoPlan={onGoPlan}
            onSelect={onSelectWorkItem}
          />
        )}
        <EditorialWorkbench
          workspace={workspace}
          onApproveBrief={onApproveBrief}
          onApproveFinal={onApproveFinal}
          onCreateDraft={onCreateDraft}
          onDraftChange={onDraftChange}
          onGoPlan={onGoPlan}
        />
      </section>
    </div>
  );
}
