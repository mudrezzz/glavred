import { fireEvent, screen, waitFor } from '@testing-library/react';
import { expect } from 'vitest';
import { goToSignals, openFoundSignals } from './signalsFlowDriver';

export function createApprovedBrief() {
  goToSignals();
  openFoundSignals();
  fireEvent.click(screen.getByRole('button', { name: /Собрать инсайт/i }));
  fireEvent.click(screen.getByRole('button', { name: /В план/i }));
  fireEvent.click(screen.getByRole('button', { name: /^Утвердить$/i }));
  fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));
  fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));
  fireEvent.click(screen.getByRole('button', { name: /Утвердить фабулу/i }));
}

export function createApprovedFinalText() {
  createApprovedBrief();
  fireEvent.click(screen.getByRole('button', { name: /Утвердить текст/i }));
}

export async function createExportedRelease() {
  createApprovedFinalText();
  fireEvent.click(screen.getByRole('button', { name: /Выпуск/i }));
  fireEvent.click(screen.getByRole('button', { name: /Подготовить выпуск/i }));
  fireEvent.click(screen.getByLabelText(/Фактические warnings просмотрены/i));
  fireEvent.click(screen.getByLabelText(/CTA проверен/i));
  fireEvent.click(screen.getByLabelText(/Текст скопирован или Markdown скачан/i));
  fireEvent.click(screen.getByRole('button', { name: /Готово к выпуску/i }));
  fireEvent.click(screen.getByRole('button', { name: /Скопировать текст/i }));

  await waitFor(() => {
    expect(screen.getAllByText(/Экспортировано вручную/i).length).toBeGreaterThan(0);
  });
}
