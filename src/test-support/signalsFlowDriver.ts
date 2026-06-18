import { fireEvent, screen } from '@testing-library/react';

export function goToSignals() {
  fireEvent.click(screen.getByRole('button', { name: /Сигналы/i }));
}

export function openFoundSignals() {
  fireEvent.click(screen.getByRole('button', { name: /Найденные сигналы/i }));
}
