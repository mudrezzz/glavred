import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from '../../App';
import { renderAppCabinet } from '../../test-support/appFlowDriver';
import { createExportedRelease } from '../../test-support/productionFlowDriver';

describe('Release app flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('shows an empty release state before an approved final text', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Выпуск/i }));

    expect(screen.getByText(/Сначала утвердите финальный текст/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Перейти в редактуру/i })).toBeInTheDocument();
  });

  it('prepares, marks ready, exports, and persists a manual release package', async () => {
    const { unmount } = renderAppCabinet();

    await createExportedRelease();

    expect(screen.getByText('Telegram')).toBeInTheDocument();
    expect(screen.getByText(/Markdown export/i)).toBeInTheDocument();

    unmount();
    renderAppCabinet();

    expect(screen.getAllByText(/Экспортировано вручную/i).length).toBeGreaterThan(0);
  });
});
