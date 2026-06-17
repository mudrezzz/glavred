import { useMemo, useState } from 'react';
import type { PostBriefEditPatch, WorkspaceState } from '../../domain/editorialWorkspace';
import { EditorialPostsAside, EditorialWorkbenchAside } from './EditorialWorkAside';
import { EditorialWorkbench } from './EditorialWorkbench';
import { EditorialWorkGroupList, EditorialWorkQueueList } from './EditorialWorkQueueList';
import { EditorialWorkQueueToolbar } from './EditorialWorkQueueToolbar';
import { EditorialWorkbenchPicker } from './EditorialWorkbenchPicker';
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
  onEditBrief,
  onDraftChange,
  onGoPlan,
  onReturnWorkItem,
  onSelectWorkItem,
  onApproveFinal
}: {
  workspace: WorkspaceState;
  onApproveBrief: () => void;
  onEditBrief: (patch: PostBriefEditPatch) => void;
  onDraftChange: (body: string) => void;
  onGoPlan: () => void;
  onReturnWorkItem: (workItemId: string) => void;
  onSelectWorkItem: (workItemId: string) => void;
  onApproveFinal: () => void;
}) {
  const [mode, setMode] = useState<'posts' | 'workbench'>('posts');
  const [filters, setFilters] = useState<EditorialWorkQueueFilters>(defaultEditorialWorkQueueFilters);
  const [viewMode, setViewMode] = useState<EditorialWorkQueueViewMode>('list');
  const [groupMode, setGroupMode] = useState<EditorialWorkGroupMode>('stage');
  const filteredItems = useMemo(
    () => filterEditorialWorkItems(workspace.editorialWorkItems, filters),
    [filters, workspace.editorialWorkItems]
  );
  const groups = useMemo(() => groupEditorialWorkItems(filteredItems, groupMode), [filteredItems, groupMode]);

  function openWorkbench(workItemId: string) {
    onSelectWorkItem(workItemId);
    setMode('workbench');
  }

  return (
    <div className="page wide fade-up">
      <section className="card project-profile-header signals-section-header editorial-section-header" data-testid="editorial-section-header">
        <div className="project-profile-main">
          <span className="rub">Редактура</span>
          <h2>Очередь постов и рабочий стол</h2>
          <p>Утвержденные слоты из плана попадают сюда как посты. В очереди выбирайте пост, на рабочем столе ведите его через стадии фабулы, драфта и финала.</p>
        </div>
        <div className="project-profile-meta signals-header-stats">
          <div><b>{workspace.editorialWorkItems.length}</b><span>постов</span></div>
          <div><b>{workspace.editorialWorkItems.filter((item) => item.status === 'inProgress').length}</b><span>в работе</span></div>
          <div><b>{workspace.editorialWorkItems.filter((item) => item.status === 'approved').length}</b><span>готово</span></div>
        </div>
      </section>
      <div className="tabs memory-tabs editorial-mode-tabs" role="tablist" aria-label="Редактура">
        <button className={`tab${mode === 'posts' ? ' active' : ''}`} type="button" role="tab" aria-selected={mode === 'posts'} onClick={() => setMode('posts')}>
          Посты
        </button>
        <button className={`tab${mode === 'workbench' ? ' active' : ''}`} type="button" role="tab" aria-selected={mode === 'workbench'} onClick={() => setMode('workbench')}>
          Рабочий стол
        </button>
      </div>
      {mode === 'posts' ? (
        <div className="memory-grid signals-workspace-grid editorial-workspace-grid">
          <section className="memory-main editorial-production-flow">
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
                В редакционной очереди пока нет утвержденных слотов. Утвердите слот в разделе «План».
              </div>
            ) : viewMode === 'groups' ? (
              <EditorialWorkGroupList
                groups={groups}
                selectedId={workspace.selectedEditorialWorkItemId}
                onReturn={onReturnWorkItem}
                onSelect={openWorkbench}
              />
            ) : (
              <EditorialWorkQueueList
                items={filteredItems}
                selectedId={workspace.selectedEditorialWorkItemId}
                onReturn={onReturnWorkItem}
                onSelect={openWorkbench}
              />
            )}
          </section>
          <EditorialPostsAside items={workspace.editorialWorkItems} />
        </div>
      ) : (
        <div className="memory-grid signals-workspace-grid editorial-workspace-grid">
          <section className="memory-main editorial-production-flow">
            <EditorialWorkbenchPicker
              items={workspace.editorialWorkItems}
              selectedId={workspace.selectedEditorialWorkItemId}
              onSelect={onSelectWorkItem}
            />
            <EditorialWorkbench
              workspace={workspace}
              onApproveBrief={onApproveBrief}
              onApproveFinal={onApproveFinal}
              onDraftChange={onDraftChange}
              onEditBrief={onEditBrief}
              onGoPlan={onGoPlan}
            />
          </section>
          <EditorialWorkbenchAside workspace={workspace} />
        </div>
      )}
    </div>
  );
}
