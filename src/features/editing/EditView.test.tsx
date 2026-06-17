import { useState } from 'react';
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
import { buildSelectEditorialWorkItemPatch } from '../../app/editorialWorkQueueActions';
import { EditView } from './EditView';

describe('EditView', () => {
  it('shows the editorial queue before the selected workbench', () => {
    const workspace = createWorkspaceWithQueue();

    renderEdit(workspace);

    expect(screen.getByRole('tab', { name: /Посты/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Рабочий стол/i })).toBeInTheDocument();
    const toolbar = screen.getByTestId('editorial-work-toolbar');
    const list = screen.getByTestId('editorial-work-list');
    expect(toolbar.compareDocumentPosition(list) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(toolbar.closest('.editorial-production-flow')).toBeInTheDocument();
    expect(screen.getAllByTestId('editorial-work-row')).toHaveLength(2);
    expect(within(screen.getAllByTestId('editorial-work-row')[0]).getByRole('button', { name: /К рабочему столу/i }).closest('.inline-actions')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /На рабочем столе/i })).not.toBeInTheDocument();
    expect(document.querySelectorAll('.editorial-summary-grid .summary-item').length).toBeGreaterThan(0);
  });

  it('opens a post on the workbench tab and shows the searchable picker', () => {
    const workspace = createWorkspaceWithQueue();
    const onSelectWorkItem = vi.fn();

    renderEdit(workspace, { onSelectWorkItem });

    fireEvent.click(within(screen.getAllByTestId('editorial-work-row')[1]).getByRole('button', { name: /Second queue item/i }));
    fireEvent.click(within(screen.getAllByTestId('editorial-work-row')[1]).getByRole('button', { name: /К рабочему столу/i }));

    expect(onSelectWorkItem).toHaveBeenCalledWith(workspace.editorialWorkItems[1].id);
    expect(screen.getByRole('tab', { name: /Рабочий стол/i })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByTestId('editorial-workbench-picker')).toBeInTheDocument();
    const picker = screen.getByLabelText(/Выбор поста/i) as HTMLSelectElement;
    expect(picker.tagName).toBe('SELECT');
    expect(picker.value).toBe(workspace.editorialWorkItems[0].id);
    fireEvent.change(picker, { target: { value: workspace.editorialWorkItems[1].id } });
    expect(onSelectWorkItem).toHaveBeenLastCalledWith(workspace.editorialWorkItems[1].id);
    expect(document.querySelector('.picker-results')).not.toBeInTheDocument();
    expect(screen.getByTestId('editorial-workbench')).toBeInTheDocument();
    expect(document.querySelector('.editorial-workbench-head')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Написать драфт/i })).not.toBeInTheDocument();
  });

  it('hydrates the workbench for the selected queue post', () => {
    const workspace = createWorkspaceWithQueue();

    render(<ControlledEditView workspace={workspace} />);

    fireEvent.click(within(screen.getAllByTestId('editorial-work-row')[1]).getByRole('button', { name: /Second queue item/i }));
    fireEvent.click(within(screen.getAllByTestId('editorial-work-row')[1]).getByRole('button', { name: /К рабочему столу/i }));

    expect(screen.getByRole('tab', { name: /Рабочий стол/i })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByLabelText(/Выбор поста/i)).toHaveValue(workspace.editorialWorkItems[1].id);
    expect(screen.getByTestId('editorial-workbench')).toHaveTextContent('Second queue item');

    fireEvent.change(screen.getByLabelText(/Выбор поста/i), {
      target: { value: workspace.editorialWorkItems[0].id }
    });

    expect(screen.getByLabelText(/Выбор поста/i)).toHaveValue(workspace.editorialWorkItems[0].id);
    expect(screen.getByTestId('editorial-workbench')).toHaveTextContent('First queue item');
  });

  it('returns a post to candidates from the posts list', () => {
    const workspace = createWorkspaceWithQueue();
    const onReturnWorkItem = vi.fn();

    renderEdit(workspace, { onReturnWorkItem });

    fireEvent.click(within(screen.getAllByTestId('editorial-work-row')[0]).getByRole('button', { name: /Вернуть в кандидаты/i }));

    expect(onReturnWorkItem).toHaveBeenCalledWith(workspace.editorialWorkItems[0].id);
  });

  it('filters, searches, and groups editorial work items', () => {
    const workspace = createWorkspaceWithQueue();

    renderEdit(workspace);

    fireEvent.change(screen.getByLabelText(/Поиск/i), { target: { value: 'Second queue item' } });
    expect(screen.getAllByTestId('editorial-work-row')).toHaveLength(1);
    expect(screen.getAllByText('Second queue item').length).toBeGreaterThan(0);

    fireEvent.change(screen.getByLabelText(/Поиск/i), { target: { value: '' } });
    fireEvent.click(screen.getByRole('tab', { name: /Группы/i }));
    expect(screen.getByText(/По стадии/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Фабула/i).length).toBeGreaterThan(0);
  });

  it('shows an empty queue path through plan when no work items exist', () => {
    renderEdit({ ...createDemoWorkspace(), editorialWorkItems: [], selectedEditorialWorkItemId: null });

    expect(screen.getByTestId('editorial-work-empty')).toHaveTextContent(/План/i);
    fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));
    expect(screen.getByText(/Выберите пост из очереди/i)).toBeInTheDocument();
  });
});

function renderEdit(
  workspace: WorkspaceState,
  overrides: Partial<{
    onReturnWorkItem: (itemId: string) => void;
    onSelectWorkItem: (itemId: string) => void;
  }> = {}
) {
  return render(
    <EditView
      workspace={workspace}
      onApproveBrief={vi.fn()}
      onApproveFinal={vi.fn()}
      onDraftChange={vi.fn()}
      onGoPlan={vi.fn()}
      onReturnWorkItem={overrides.onReturnWorkItem ?? vi.fn()}
      onSelectWorkItem={overrides.onSelectWorkItem ?? vi.fn()}
    />
  );
}

function ControlledEditView({ workspace }: { workspace: WorkspaceState }) {
  const [current, setCurrent] = useState(workspace);

  return (
    <EditView
      workspace={current}
      onApproveBrief={vi.fn()}
      onApproveFinal={vi.fn()}
      onDraftChange={vi.fn()}
      onGoPlan={vi.fn()}
      onReturnWorkItem={vi.fn()}
      onSelectWorkItem={(itemId) =>
        setCurrent((previous) => ({
          ...previous,
          ...buildSelectEditorialWorkItemPatch(previous, itemId)
        }))
      }
    />
  );
}

function createWorkspaceWithQueue(): WorkspaceState {
  const workspace = createDemoWorkspace();
  const firstItem = renamePlanItem(workspace.contentPlanItems[0], 'First queue item');
  const secondItem = renamePlanItem(workspace.contentPlanItems[1], 'Second queue item');
  const insightCard = createWorkspaceInsightCard({ ...workspace, contentPlanItem: firstItem });
  const brief = approvePostBrief(createPostBrief(firstItem, insightCard, workspace.editorialModel));
  const secondBrief = approvePostBrief(createPostBrief(secondItem, insightCard, workspace.editorialModel));
  const firstWorkItem = createEditorialWorkItem(firstItem, { brief });
  const secondWorkItem = createEditorialWorkItem(secondItem, { brief: secondBrief });

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
