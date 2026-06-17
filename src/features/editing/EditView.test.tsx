import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import {
  approvePostBrief,
  createEditorialWorkItem,
  type ContentPlanItem,
  type WorkspaceState
} from '../../domain/editorialWorkspace';
import { createPostBrief, createWorkspaceInsightCard } from '../../application/editorialServices';
import { createDemoWorkspace } from '../../fixtures/demoWorkspace';
import { EditView } from './EditView';

describe('EditView', () => {
  it('shows the editorial queue before the selected workbench', () => {
    const workspace = createWorkspaceWithQueue();

    renderEdit(workspace);

    const toolbar = screen.getByTestId('editorial-work-toolbar');
    const list = screen.getByTestId('editorial-work-list');
    expect(toolbar.compareDocumentPosition(list) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(toolbar.closest('.editorial-production-flow')).toBeInTheDocument();
    expect(screen.getAllByTestId('editorial-work-row')).toHaveLength(2);
    expect(within(screen.getAllByTestId('editorial-work-row')[0]).getByRole('button', { name: /Открыть|Открыто/i }).closest('.inline-actions')).toBeInTheDocument();
    expect(screen.getByTestId('editorial-workbench')).toBeInTheDocument();
  });

  it('filters, searches, and groups editorial work items', () => {
    const workspace = createWorkspaceWithQueue();

    renderEdit(workspace);

    fireEvent.change(screen.getByLabelText(/Поиск/i), { target: { value: 'Second queue item' } });
    expect(screen.getAllByTestId('editorial-work-row')).toHaveLength(1);
    expect(screen.getByText('Second queue item')).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/Поиск/i), { target: { value: '' } });
    fireEvent.click(screen.getByRole('tab', { name: /Группы/i }));
    expect(screen.getByText(/По стадии/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Фабула/i).length).toBeGreaterThan(0);
  });

  it('shows an empty queue path through plan when no work items exist', () => {
    renderEdit({ ...createDemoWorkspace(), editorialWorkItems: [], selectedEditorialWorkItemId: null });

    expect(screen.getByTestId('editorial-work-empty')).toHaveTextContent(/План/i);
    expect(screen.getByText(/Выберите пост из очереди/i)).toBeInTheDocument();
  });
});

function renderEdit(workspace: WorkspaceState) {
  return render(
    <EditView
      workspace={workspace}
      onApproveBrief={vi.fn()}
      onApproveFinal={vi.fn()}
      onCreateDraft={vi.fn()}
      onDraftChange={vi.fn()}
      onGoPlan={vi.fn()}
      onSelectWorkItem={vi.fn()}
    />
  );
}

function createWorkspaceWithQueue(): WorkspaceState {
  const workspace = createDemoWorkspace();
  const firstItem = renamePlanItem(workspace.contentPlanItems[0], 'First queue item');
  const secondItem = renamePlanItem(workspace.contentPlanItems[1], 'Second queue item');
  const insightCard = createWorkspaceInsightCard({ ...workspace, contentPlanItem: firstItem });
  const brief = approvePostBrief(createPostBrief(firstItem, insightCard, workspace.editorialModel));
  const firstWorkItem = createEditorialWorkItem(firstItem, { brief });
  const secondWorkItem = createEditorialWorkItem(secondItem);

  return {
    ...workspace,
    contentPlanItems: [firstItem, secondItem],
    contentPlanItem: firstItem,
    postBrief: brief,
    editorialWorkItems: [firstWorkItem, secondWorkItem],
    selectedEditorialWorkItemId: firstWorkItem.id
  };
}

function renamePlanItem(item: ContentPlanItem, title: string): ContentPlanItem {
  return {
    ...item,
    title,
    topicTitle: item.topicTitle ?? 'AI product discovery',
    fabulaTitle: item.fabulaTitle ?? 'Research note'
  };
}
