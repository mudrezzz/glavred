import { useState } from 'react';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import {
  approvePostBrief,
  approvePostCandidate,
  createEditorialWorkItem,
  type ContentPlanItem,
  type WorkspaceState
} from '../../domain/editorialWorkspace';
import { createPostBrief, createPostCandidates, createPostDraft, createWorkspaceInsightCard } from '../../application/editorialServices';
import { createDemoWorkspace } from '../../fixtures/demoWorkspace';
import { buildEditCurrentBriefPatch, buildSelectEditorialWorkItemPatch } from '../../app/editorialWorkQueueActions';
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

  it('shows full candidate and slot context on the fabula workbench', () => {
    const workspace = createWorkspaceWithQueue();
    const candidate = workspace.postCandidate!;

    render(<ControlledEditView workspace={workspace} />);

    fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));
    fireEvent.click(within(screen.getByTestId('editorial-workbench')).getByRole('tab', { name: /Фабула/i }));

    const context = screen.getByTestId('editorial-brief-context');
    expect(context).toHaveTextContent(workspace.sourceSignals.find((signal) => signal.id === candidate.sourceSignalId)?.title ?? '');
    expect(context).toHaveTextContent(candidate.audience);
    expect(context).toHaveTextContent(candidate.value);
    expect(context).toHaveTextContent(candidate.goal);
    expect(context).toHaveTextContent(candidate.platform);
    expect(context).toHaveTextContent(candidate.evidenceSummary);
    expect(screen.getByText('Risks').closest('.editorial-brief-risks')).toHaveTextContent(candidate.risks[0]);
    expect(context.querySelectorAll('.candidate-fact.wide')).toHaveLength(1);
  });

  it('approves draft text from the draft stage without a final tab', () => {
    const workspace = createWorkspaceWithQueue();
    const onDraftChange = vi.fn();
    const onApproveFinal = vi.fn();

    renderEdit(workspace, { onApproveFinal, onDraftChange });

    fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));
    const workbench = within(screen.getByTestId('editorial-workbench'));

    expect(workbench.queryByRole('tab', { name: /Финал/i })).not.toBeInTheDocument();
    expect(workbench.getByRole('tab', { name: /Драфт/i })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('button', { name: /Сохранить правки/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Утвердить текст/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Вернуться к фабуле/i })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Текст драфта'), { target: { value: 'Unsaved draft edit' } });
    expect(onDraftChange).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /Сохранить правки/i }));
    expect(onDraftChange).toHaveBeenCalledWith('Unsaved draft edit');

    fireEvent.change(screen.getByLabelText('Текст драфта'), { target: { value: 'Approved draft edit' } });
    fireEvent.click(screen.getByRole('button', { name: /Утвердить текст/i }));
    expect(onApproveFinal).toHaveBeenCalledWith('Approved draft edit');
  });

  it('shows visual stage in queue filters instead of final', () => {
    const workspace = createWorkspaceWithQueue();

    renderEdit(workspace);

    expect(screen.getByRole('option', { name: /Визуал/i })).toBeInTheDocument();
    expect(screen.queryByRole('option', { name: /Финал/i })).not.toBeInTheDocument();
  });

  it('edits the current fabula brief and drops the stale draft from the workbench', () => {
    const workspace = createWorkspaceWithQueue();

    render(<ControlledEditView workspace={workspace} />);

    fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));
    fireEvent.click(within(screen.getByTestId('editorial-workbench')).getByRole('tab', { name: /Фабула/i }));
    expect(screen.getByText('First queue item')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Редактировать/i }));

    fireEvent.change(screen.getByLabelText('Заголовок'), { target: { value: 'Edited fabula title' } });
    fireEvent.change(screen.getByLabelText('Тезис'), { target: { value: 'Edited fabula thesis' } });
    fireEvent.change(screen.getByLabelText('Доказательства'), {
      target: { value: 'First evidence line\n\nSecond evidence line' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Сохранить/i }));

    expect(screen.queryByTestId('editorial-brief-edit-form')).not.toBeInTheDocument();
    expect(screen.getByTestId('editorial-brief-snapshot')).toHaveTextContent('Edited fabula title');
    expect(screen.getByTestId('editorial-brief-snapshot')).toHaveTextContent('Edited fabula thesis');
    expect(screen.getByTestId('editorial-brief-snapshot')).toHaveTextContent('First evidence line');
    expect(screen.queryByText(/Версия 1/i)).not.toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Фабула/i })).toHaveAttribute('aria-selected', 'true');
  });

  it('cancels fabula brief editing without changing visible text', () => {
    const workspace = createWorkspaceWithQueue();

    render(<ControlledEditView workspace={workspace} />);

    fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));
    fireEvent.click(within(screen.getByTestId('editorial-workbench')).getByRole('tab', { name: /Фабула/i }));
    fireEvent.click(screen.getByRole('button', { name: /Редактировать/i }));
    fireEvent.change(screen.getByLabelText('Заголовок'), { target: { value: 'Discarded title' } });
    fireEvent.click(screen.getByRole('button', { name: /Отменить/i }));

    expect(screen.queryByTestId('editorial-brief-edit-form')).not.toBeInTheDocument();
    expect(screen.queryByText('Discarded title')).not.toBeInTheDocument();
    expect(screen.getByTestId('editorial-brief-snapshot')).toHaveTextContent('First queue item');
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
    onApproveFinal: (body?: string) => void;
    onDraftChange: (body: string) => void;
    onReturnWorkItem: (itemId: string) => void;
    onSelectWorkItem: (itemId: string) => void;
  }> = {}
) {
  return render(
    <EditView
      workspace={workspace}
      onApproveBrief={vi.fn()}
      onEditBrief={vi.fn()}
      onApproveFinal={overrides.onApproveFinal ?? vi.fn()}
      onDraftChange={overrides.onDraftChange ?? vi.fn()}
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
      onEditBrief={(patch) =>
        setCurrent((previous) => ({
          ...previous,
          ...buildEditCurrentBriefPatch(previous, patch)
        }))
      }
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
  const approvedCandidate = approvePostCandidate(createPostCandidates(workspace)[0]);
  const firstItem = renamePlanItem(
    {
      ...workspace.contentPlanItems[0],
      insightId: `insight-${approvedCandidate.id}`,
      sourceSignalId: approvedCandidate.sourceSignalId,
      topicId: approvedCandidate.topicId,
      fabulaId: approvedCandidate.fabulaId,
      topicTitle: workspace.topics.find((topic) => topic.id === approvedCandidate.topicId)?.title,
      fabulaTitle: workspace.fabulas.find((fabula) => fabula.id === approvedCandidate.fabulaId)?.title,
      platform: approvedCandidate.platform
    },
    'First queue item'
  );
  const secondItem = renamePlanItem(workspace.contentPlanItems[1], 'Second queue item');
  const insightCard = createWorkspaceInsightCard({ ...workspace, contentPlanItem: firstItem });
  const brief = approvePostBrief(createPostBrief(firstItem, insightCard, workspace.editorialModel));
  const secondBrief = approvePostBrief(createPostBrief(secondItem, insightCard, workspace.editorialModel));
  const draft = createPostDraft(brief, workspace.editorialModel);
  const firstWorkItem = createEditorialWorkItem(firstItem, { brief, draft }, approvedCandidate.id);
  const secondWorkItem = createEditorialWorkItem(secondItem, { brief: secondBrief });

  return {
    ...workspace,
    postCandidates: [approvedCandidate],
    postCandidate: approvedCandidate,
    contentPlanItems: [firstItem, secondItem],
    contentPlanItem: firstItem,
    postBrief: brief,
    postDraft: draft,
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
