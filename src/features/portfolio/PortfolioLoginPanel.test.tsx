import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { PortfolioLoginPanel } from './PortfolioLoginPanel';

describe('PortfolioLoginPanel', () => {
  it('submits demo credentials and shows auth errors', () => {
    const onLogin = vi.fn().mockResolvedValue(undefined);

    render(<PortfolioLoginPanel error="Неверный email или пароль" loading={false} onLogin={onLogin} />);

    expect(screen.getByText('Вход в рабочий портфель')).toBeInTheDocument();
    expect(screen.getByText('Неверный email или пароль')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Войти' }));

    expect(onLogin).toHaveBeenCalledWith('founder@example.test', 'glavred-demo');
  });
});
