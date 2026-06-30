import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from '../../App';
import { renderAppCabinet } from '../../test-support/appFlowDriver';
import { createExportedRelease } from '../../test-support/productionFlowDriver';

describe('Analytics app flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('shows an empty analytics state before manual export', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Аналитика/i }));

    expect(screen.getByText(/Сначала завершите ручной выпуск/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Перейти в выпуск/i })).toBeInTheDocument();
  });

  it('prepares, captures, and persists editorial learning notes after manual export', async () => {
    const { unmount } = renderAppCabinet();

    await createExportedRelease();

    fireEvent.click(screen.getByRole('button', { name: /Аналитика/i }));
    fireEvent.click(screen.getByRole('button', { name: /Подготовить аналитику/i }));

    expect(screen.getByText(/Ручные метрики/i)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText('Просмотры'), { target: { value: '1200' } });
    fireEvent.change(screen.getByLabelText('Комментарии'), { target: { value: '14' } });
    fireEvent.change(screen.getByLabelText('Что сработало'), {
      target: { value: 'Тезис про demo-to-adoption gap собрал содержательные комментарии AI PM.' }
    });
    fireEvent.change(screen.getByLabelText('Реакция аудитории'), {
      target: { value: 'Founders спорили не про модели, а про то, как встроить AI-фичу в workflow.' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Зафиксировать выводы/i }));

    expect(screen.getAllByText(/Выводы зафиксированы/i).length).toBeGreaterThan(0);

    unmount();
    renderAppCabinet();

    expect(screen.getAllByText(/Выводы зафиксированы/i).length).toBeGreaterThan(0);
    expect(screen.getByDisplayValue(/demo-to-adoption gap/i)).toBeInTheDocument();
  });
});
