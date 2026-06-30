import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from '../../App';
import { renderAppCabinet } from '../../test-support/appFlowDriver';
import type { HumanCommentRevisionQualityCheck } from '../../domain/editorialWorkspace';
import { setDraftCommentRevisionFetchForTests } from '../../infrastructure/draftCommentRevisionClient';
import { createApprovedBrief } from '../../test-support/productionFlowDriver';

const HITL_FLOW_WAIT = { timeout: 30000 };

describe('Editorial workbench HITL app flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    setDraftCommentRevisionFetchForTests(null);
  });

  it('creates a new immutable draft version from an editor comment', async () => {
    const revisionFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        title: 'Усиленная версия',
        body: 'Усиленная версия с более ясной авторской позицией и меньшим пересказом источников.',
        revisionSummary: 'Усилена авторская позиция.',
        aiRunId: 'ai-human-comment-1',
        selectedModel: 'writer-model',
        attempts: [],
        qualityCheck: makeQualityCheck('warning', {
          summary: 'Комментарий выполнен частично.',
          missedCommentIntents: ['меньше пересказа источников']
        })
      })
    });
    setDraftCommentRevisionFetchForTests(revisionFetch);

    renderAppCabinet();
    await createApprovedBrief();

    fireEvent.change(screen.getByLabelText('Комментарий к улучшению драфта'), {
      target: { value: 'Усиль авторскую позицию и убери пересказ источников' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Улучшить по комментарию/i }));

    await waitFor(() => {
      expect(screen.getByDisplayValue(/Усиленная версия с более ясной авторской позицией/i)).toBeInTheDocument();
    }, HITL_FLOW_WAIT);
    expect(within(screen.getByLabelText('Версии драфта')).getByRole('button', { name: /v1/i })).toBeInTheDocument();
    expect(within(screen.getByLabelText('Версии драфта')).getByRole('button', { name: /v2.*есть риски/i })).toBeInTheDocument();
    expect(screen.getByText(/Комментарий выполнен частично/i)).toBeInTheDocument();
    expect(screen.getByText(/Не закрыто: меньше пересказа источников/i)).toBeInTheDocument();
    expect(screen.queryByDisplayValue('Усиль авторскую позицию и убери пересказ источников')).not.toBeInTheDocument();

    const payload = JSON.parse(String(revisionFetch.mock.calls[0][1].body));
    expect(payload).toMatchObject({
      draftRunId: 'draft-run-app-flow',
      currentVersion: {
        id: 'draft-app-flow-v1',
        versionNumber: 1
      },
      editorComment: 'Усиль авторскую позицию и убери пересказ источников'
    });
  });

  it('keeps the current version list intact when comment revision fails', async () => {
    setDraftCommentRevisionFetchForTests(vi.fn().mockResolvedValue({ ok: false, status: 503 }));

    renderAppCabinet();
    await createApprovedBrief();

    fireEvent.change(screen.getByLabelText('Комментарий к улучшению драфта'), {
      target: { value: 'Сделай текст конкретнее' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Улучшить по комментарию/i }));

    await waitFor(() => {
      expect(screen.getByText(/Draft revision failed with HTTP 503/i)).toBeInTheDocument();
    }, HITL_FLOW_WAIT);
    expect(within(screen.getByLabelText('Версии драфта')).getByRole('button', { name: /v1/i })).toBeInTheDocument();
    expect(within(screen.getByLabelText('Версии драфта')).queryByRole('button', { name: /v2/i })).not.toBeInTheDocument();
  });

  it('allows selecting the original machine version as final after human revisions', async () => {
    setDraftCommentRevisionFetchForTests(vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        title: 'Новая версия',
        body: 'Новая версия по комментарию редактора.',
        revisionSummary: 'Переписано по комментарию.',
        aiRunId: 'ai-human-comment-2',
        selectedModel: 'writer-model',
        attempts: [],
        qualityCheck: makeQualityCheck('passed')
      })
    }));

    renderAppCabinet();
    await createApprovedBrief();

    const originalBody = (screen.getByLabelText('Текст драфта') as HTMLTextAreaElement).value;
    fireEvent.change(screen.getByLabelText('Комментарий к улучшению драфта'), {
      target: { value: 'Сделай версию короче' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Улучшить по комментарию/i }));
    await waitFor(() => {
      expect(screen.getByDisplayValue('Новая версия по комментарию редактора.')).toBeInTheDocument();
    }, HITL_FLOW_WAIT);

    fireEvent.click(within(screen.getByLabelText('Версии драфта')).getByRole('button', { name: /v1/i }));
    await waitFor(() => {
      expect(screen.getByLabelText('Текст драфта')).toHaveValue(originalBody);
    }, HITL_FLOW_WAIT);
    fireEvent.click(screen.getByRole('button', { name: /Сделать финальной/i }));

    await waitFor(() => {
      expect(screen.getAllByText(/Текст утвержден/i).length).toBeGreaterThan(0);
    }, HITL_FLOW_WAIT);
    expect(within(screen.getByLabelText('Версии драфта')).getByRole('button', { name: /v1.*финал/i })).toBeInTheDocument();
  });
});

function makeQualityCheck(
  status: 'passed' | 'warning' | 'critical' | 'notRun',
  overrides: Partial<HumanCommentRevisionQualityCheck> = {}
): HumanCommentRevisionQualityCheck {
  return {
    status,
    commentComplianceStatus: status,
    sourceIntegrityStatus: 'passed',
    publicProseStatus: 'passed',
    internalJargonLeaks: [],
    regressionWarnings: [],
    matchedCommentIntents: ['editor comment'],
    missedCommentIntents: [],
    summary: 'Комментарий выполнен.',
    attempts: [],
    ...overrides
  };
}
