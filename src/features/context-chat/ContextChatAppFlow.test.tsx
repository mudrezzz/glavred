import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from '../../App';
import { renderAppCabinet } from '../../test-support/appFlowDriver';

describe('Context chat app flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders context chat collapsed by default and opens from the topbar', () => {
    renderAppCabinet();

    expect(screen.getByTestId('context-chat-topbar-trigger')).toBeInTheDocument();
    expect(screen.queryByTestId('context-chat-toggle')).not.toBeInTheDocument();
    expect(screen.queryByTestId('context-chat-drawer')).not.toBeInTheDocument();

    fireEvent.click(screen.getByTestId('context-chat-topbar-trigger'));

    expect(screen.getByTestId('context-chat-drawer')).toBeInTheDocument();
    expect(screen.getByText(/Память автора · мысли/i)).toBeInTheDocument();

    expect(screen.getByRole('tab', { name: /Чат/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Подсказки/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Свернуть/i })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Закрыть помощника/i }));

    expect(screen.queryByTestId('context-chat-drawer')).not.toBeInTheDocument();
  });

  it('updates context chat suggestions when the active section changes', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByTestId('context-chat-topbar-trigger'));
    fireEvent.click(screen.getByRole('tab', { name: /Подсказки/i }));
    expect(screen.getByText(/Зафиксировать сырую мысль/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Редакционная модель|Р РµРґР°РєС†РёРѕРЅРЅР°СЏ РјРѕРґРµР»СЊ/i }));

    expect(screen.getByText(/Добавить anti-AI правило/i)).toBeInTheDocument();
  });

  it('opens existing draft flows from accepted context chat suggestions without saving automatically', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Редакционная модель|Р РµРґР°РєС†РёРѕРЅРЅР°СЏ РјРѕРґРµР»СЊ/i }));
    fireEvent.click(screen.getByRole('tab', { name: /Темы|РўРµРјС‹/i }));
    fireEvent.click(screen.getByTestId('context-chat-topbar-trigger'));
    fireEvent.click(screen.getByRole('tab', { name: /Подсказки/i }));
    fireEvent.click(screen.getByRole('button', { name: /Создать черновик темы/i }));

    expect(screen.getByDisplayValue('AI trust onboarding')).toBeInTheDocument();
    expect(screen.getByText(/8 тем|8 тем/i)).toBeInTheDocument();
  });

  it('allows asking the context chat to generate a topic without saving automatically', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Редакционная модель/i }));
    fireEvent.click(screen.getByTestId('context-chat-topbar-trigger'));
    fireEvent.change(screen.getByLabelText(/Сообщение помощнику/i), {
      target: { value: 'Сгенерируй темы согласно настройкам издательства' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Отправить/i }));

    expect(screen.getByText(/Могу открыть черновик новой темы/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Создать черновик темы/i }));

    expect(screen.getByDisplayValue('AI rollout risk')).toBeInTheDocument();
    expect(screen.queryByText(/9 тем/i)).not.toBeInTheDocument();
  });

  it('allows dismissing context chat suggestions instead of accepting read-only actions', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByTestId('context-chat-topbar-trigger'));
    fireEvent.click(screen.getByRole('tab', { name: /Подсказки/i }));

    expect(screen.queryByRole('button', { name: /Принять к сведению/i })).not.toBeInTheDocument();
    fireEvent.click(screen.getAllByRole('button', { name: /Скрыть подсказку/i })[0]);

    expect(screen.queryByText(/Зафиксировать сырую мысль/i)).not.toBeInTheDocument();
  });
});
