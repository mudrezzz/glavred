import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from '../../App';
import { renderAppCabinet } from '../../test-support/appFlowDriver';
import { goToSignals } from '../../test-support/signalsFlowDriver';

describe('Signals app flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('shows the signals workspace with radars, reviewable signals, and post-candidate preview', () => {
    renderAppCabinet();

    goToSignals();

    expect(screen.getByTestId('signals-section-header')).toHaveTextContent('Сигналы');
    expect(screen.getByRole('button', { name: /Радары|Р Р°РґР°СЂС‹/i })).toBeInTheDocument();
    const foundSignalsTab = screen.getByRole('button', { name: /Найденные сигналы|РќР°Р№РґРµРЅРЅС‹Рµ СЃРёРіРЅР°Р»С‹/i });
    expect(foundSignalsTab).toBeInTheDocument();
    expect(foundSignalsTab.querySelector('.tab-count')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Кандидаты постов|РљР°РЅРґРёРґР°С‚С‹ РїРѕСЃС‚РѕРІ/i })).toBeInTheDocument();
    expect(screen.getByTestId('radar-list')).toBeInTheDocument();
    expect(within(screen.getByTestId('signals-radar-toolbar')).getByTestId('add-radar-button')).toHaveClass('btn-sec');
    expect(within(screen.getByTestId('signals-radar-toolbar')).getByTestId('add-radar-button')).not.toHaveClass('btn-pri');
    expect(screen.getAllByTestId('radar-row').length).toBeGreaterThan(0);
    expect(screen.getAllByTestId('radar-row')[0]).toHaveClass('radar-card');
    expect(screen.getAllByText('Память автора').length).toBeGreaterThan(0);
    expect(document.querySelector('.source-grid')).toBeNull();

    fireEvent.click(screen.getByRole('button', { name: /Sanitized author materials/i }));
    const expandedRadar = screen.getAllByTestId('radar-row').find((row) => row.classList.contains('expanded')) as HTMLElement;
    expect(within(expandedRadar).getByRole('tab', { name: /Настройка/i })).toHaveAttribute('aria-selected', 'true');
    expect(within(expandedRadar).getByTestId('radar-settings-panel')).toBeInTheDocument();
    expect(screen.queryByTestId('radar-upstream-trace')).not.toBeInTheDocument();
    fireEvent.click(within(expandedRadar).getByRole('tab', { name: /Трасса запуска/i }));
    expect(screen.getByTestId('radar-upstream-trace')).toBeInTheDocument();
    fireEvent.click(within(expandedRadar).getByRole('tab', { name: /Настройка/i }));
    fireEvent.click(within(expandedRadar).getByRole('button', { name: /Запустить радар/i }));
    expect(within(expandedRadar).getByRole('tab', { name: /Трасса запуска/i })).toHaveAttribute('aria-selected', 'true');
    expect(within(expandedRadar).getByTestId('radar-upstream-trace')).toBeInTheDocument();
    fireEvent.click(within(expandedRadar).getByRole('tab', { name: /Настройка/i }));
    fireEvent.click(screen.getByRole('button', { name: /Открыть сигналы|РћС‚РєСЂС‹С‚СЊ СЃРёРіРЅР°Р»С‹/i }));

    const signalList = screen.getByTestId('source-signal-list');
    expect(signalList).toBeInTheDocument();
    expect(screen.getAllByTestId('source-signal-row').length).toBeGreaterThan(0);
    expect(screen.getAllByTestId('source-signal-row')[0]).toHaveClass('signal-card');

    fireEvent.change(screen.getByLabelText(/Фильтр статуса сигнала/i), { target: { value: 'new' } });
    expect(screen.getAllByTestId('source-signal-row').length).toBeGreaterThan(0);

    const signalRow = screen.getAllByTestId('source-signal-row')[0];
    if (!signalRow.classList.contains('expanded')) {
      fireEvent.click(within(signalRow).getAllByRole('button')[0]);
    }
    expect(within(signalRow).getByText('Доказательства')).toBeInTheDocument();
    expect(within(signalRow).getByTestId('signal-filter-evaluations')).toBeInTheDocument();
    expect(within(signalRow).getByRole('heading', { name: /Редакционная полезность|Предварительная локальная оценка/i })).toBeInTheDocument();
    expect(within(screen.getByTestId('signal-filter-status-filter')).getByRole('option', { name: 'Все по фильтрам' })).toBeInTheDocument();
    fireEvent.change(screen.getByTestId('signal-filter-status-filter'), { target: { value: 'all' } });
    expect(screen.getAllByTestId('source-signal-row').length).toBeGreaterThan(0);
    fireEvent.change(screen.getByTestId('signal-filter-status-filter'), { target: { value: 'all' } });
    fireEvent.click(within(signalRow).getByRole('button', { name: /Утвердить сигнал|РЈС‚РІРµСЂРґРёС‚СЊ СЃРёРіРЅР°Р»/i }));
    fireEvent.change(screen.getByLabelText(/Фильтр статуса сигнала/i), { target: { value: 'approved' } });
    expect(screen.getAllByTestId('source-signal-row').length).toBeGreaterThan(0);

    fireEvent.change(screen.getByLabelText(/Фильтр статуса сигнала/i), { target: { value: 'new' } });
    const archiveRow = screen.getAllByTestId('source-signal-row')[0];
    fireEvent.click(within(archiveRow).getAllByRole('button')[0]);
    fireEvent.click(within(archiveRow).getByRole('button', { name: /В архив|Р’ Р°СЂС…РёРІ/i }));
    fireEvent.change(screen.getByLabelText(/Фильтр статуса сигнала/i), { target: { value: 'archived' } });
    expect(screen.getAllByTestId('source-signal-row').length).toBeGreaterThan(0);

    fireEvent.click(screen.getByRole('button', { name: /Кандидаты постов|РљР°РЅРґРёРґР°С‚С‹ РїРѕСЃС‚РѕРІ/i }));
    expect(screen.queryByText(/Slice 1\.6/i)).not.toBeInTheDocument();
    expect(screen.getAllByTestId('post-candidate-card').length).toBeGreaterThanOrEqual(2);
    const candidateCard = screen.getAllByTestId('post-candidate-card')[0];
    const candidateTitle = within(candidateCard).getByRole('heading', { level: 3 }).textContent ?? '';
    fireEvent.click(within(candidateCard).getByRole('button', { name: /^Утвердить$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Собрать инсайт/i }));
    expect(screen.getAllByText(candidateTitle).length).toBeGreaterThan(1);
  });

  it('edits an existing radar inline with multiline rule and source fields', () => {
    renderAppCabinet();

    goToSignals();

    const radarRows = screen.getAllByTestId('radar-row');
    const lastRadar = radarRows[radarRows.length - 1];
    const rowMain = lastRadar.querySelector('.radar-row-main') as HTMLElement;
    fireEvent.click(rowMain);

    const editButton = lastRadar.querySelector('.radar-actions .btn') as HTMLElement;
    fireEvent.click(editButton);

    const inlineEditor = lastRadar.querySelector('.radar-editor');
    expect(inlineEditor).toBeInTheDocument();
    expect(screen.getByTestId('radar-list').previousElementSibling).not.toHaveClass('radar-editor');
    expect(within(inlineEditor as HTMLElement).getByTestId('radar-source-discovery-mode')).toBeInTheDocument();
    expect(within(inlineEditor as HTMLElement).getByTestId('radar-filter-section')).toBeInTheDocument();
    expect(within(inlineEditor as HTMLElement).getByRole('radiogroup', { name: 'Языки источников' })).toBeInTheDocument();
    expect(within(inlineEditor as HTMLElement).getByLabelText('Язык редакции и английский')).toBeChecked();
    fireEvent.click(within(inlineEditor as HTMLElement).getByLabelText('Любые языки'));
    expect(within(inlineEditor as HTMLElement).getByLabelText('Любые языки')).toBeChecked();
    expect((inlineEditor as HTMLElement).querySelector('.radar-filter-controls')).toBeInTheDocument();
    expect(within(inlineEditor as HTMLElement).queryByText(/^Заметка$/i)).not.toBeInTheDocument();
    expect(lastRadar.querySelectorAll('.radar-rule-edit textarea').length).toBeGreaterThan(0);
    fireEvent.click(within(inlineEditor as HTMLElement).getByLabelText(/Только указанные/i));
    expect(within(inlineEditor as HTMLElement).queryByRole('alert')).not.toBeInTheDocument();
    expect(within(inlineEditor as HTMLElement).getByRole('button', { name: /^Сохранить$/i })).toBeEnabled();
    if (lastRadar.querySelectorAll('.radar-source-edit textarea').length === 0) {
      const addSourceButton = Array.from((inlineEditor as HTMLElement).querySelectorAll('button')).find((button) =>
        button.textContent?.includes('Источник')
      ) as HTMLElement;
      fireEvent.click(addSourceButton);
    }
    expect(lastRadar.querySelectorAll('.radar-source-edit textarea').length).toBeGreaterThan(0);
  });
});
