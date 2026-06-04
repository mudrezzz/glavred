import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from './App';

describe('App', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders the editorial cabinet shell and planned sections', () => {
    render(<App />);

    expect(screen.getByText('Главред')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Редакционная модель/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Радар/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /План/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Фабулы/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Редактура/i })).toBeInTheDocument();
  });

  it('moves from source signal to an approved post brief', () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Собрать инсайт/i }));
    expect(screen.getByText(/AI-пилоты проваливаются/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /В план/i }));
    expect(screen.getByText(/Утвердите публикацию/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Утвердить план/i }));
    fireEvent.click(screen.getByRole('button', { name: /Подготовить фабулу/i }));

    expect(screen.getByText(/Утвердите фабулу/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Утвердить фабулу/i }));

    expect(screen.getAllByText('Утверждено').length).toBeGreaterThan(0);
  });

  it('shows an empty editorial review state before an approved brief', () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));

    expect(screen.getByText(/Сначала утвердите фабулу/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Перейти к фабуле/i })).toBeInTheDocument();
  });

  it('creates, edits, approves, and persists a final text', () => {
    const { unmount } = render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Собрать инсайт/i }));
    fireEvent.click(screen.getByRole('button', { name: /В план/i }));
    fireEvent.click(screen.getByRole('button', { name: /Утвердить план/i }));
    fireEvent.click(screen.getByRole('button', { name: /Подготовить фабулу/i }));
    fireEvent.click(screen.getByRole('button', { name: /Утвердить фабулу/i }));

    fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));
    fireEvent.click(screen.getByRole('button', { name: /Написать драфт/i }));

    expect(screen.getByText('Стиль')).toBeInTheDocument();
    expect(screen.getByText('Анти-AI')).toBeInTheDocument();
    expect(screen.getAllByText('Фактчек').length).toBeGreaterThan(0);
    expect(screen.getByText('Политика')).toBeInTheDocument();

    const draftEditor = screen.getByLabelText('Текст драфта');
    fireEvent.change(draftEditor, {
      target: {
        value: `${(draftEditor as HTMLTextAreaElement).value}\n\nРучная редакторская правка перед финалом.`
      }
    });
    fireEvent.click(screen.getByRole('button', { name: /Утвердить текст/i }));
    fireEvent.click(screen.getByRole('button', { name: /Финал/i }));

    expect(screen.getAllByText(/Финальный текст утвержден/i).length).toBeGreaterThan(0);

    unmount();
    render(<App />);

    expect(screen.getAllByText(/Финальный текст утвержден/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Ручная редакторская правка/i)).toBeInTheDocument();
  });
});
