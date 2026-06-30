import { fireEvent, render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import { App } from '../App';

export function renderAppDashboard() {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('backend disabled for app-flow test')));
  return render(<App />);
}

export function openDefaultProjectCabinet() {
  fireEvent.click(screen.getAllByRole('button', { name: 'Открыть кабинет' })[0]);
}

export function renderAppCabinet() {
  const result = renderAppDashboard();
  openDefaultProjectCabinet();
  return result;
}
