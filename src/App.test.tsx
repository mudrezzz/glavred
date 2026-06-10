import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from './App';

function goToRadar() {
  fireEvent.click(screen.getByRole('button', { name: /Радар/i }));
}

function createApprovedBrief() {
  goToRadar();
  fireEvent.click(screen.getByRole('button', { name: /Собрать инсайт/i }));
  fireEvent.click(screen.getByRole('button', { name: /В план/i }));
  fireEvent.click(screen.getByRole('button', { name: /Утвердить план/i }));
  fireEvent.click(screen.getByRole('button', { name: /Подготовить фабулу/i }));
  fireEvent.click(screen.getByRole('button', { name: /Утвердить фабулу/i }));
}

function createApprovedFinalText() {
  createApprovedBrief();
  fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));
  fireEvent.click(screen.getByRole('button', { name: /Написать драфт/i }));
  fireEvent.click(screen.getByRole('button', { name: /Утвердить текст/i }));
}

async function createExportedRelease() {
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

describe('App', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders the editorial cabinet shell and planned sections', () => {
    render(<App />);

    expect(screen.getByText('Главред')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Память автора/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Редакционная модель/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Радар/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /План/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Фабулы/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Редактура/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Выпуск/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Аналитика/i })).toBeInTheDocument();
  });

  it('opens on author memory with demo notes and evidence-backed assertions', () => {
    render(<App />);

    expect(screen.getByText('Авторская память')).toBeInTheDocument();
    expect(screen.getByText(/Workflow risk важнее выбора модели/i)).toBeInTheDocument();
    expect(screen.getByText(/AI Product Manager с исследовательской оптикой/i)).toBeInTheDocument();
    expect(screen.getByText(/Как система поняла автора/i)).toBeInTheDocument();
  });

  it('adds an author thought note and persists it after reload', () => {
    const { unmount } = render(<App />);

    fireEvent.change(screen.getByLabelText('Заголовок'), { target: { value: 'Новая заметка про onboarding' } });
    fireEvent.change(screen.getByLabelText('Заметка автора'), {
      target: { value: 'AI onboarding должен объяснять, где пользователь может доверять системе, а где нужен fallback.' }
    });
    fireEvent.change(screen.getByLabelText('Теги'), { target: { value: 'onboarding, trust' } });
    fireEvent.click(screen.getByRole('button', { name: /Добавить в память/i }));

    expect(screen.getByText('Новая заметка про onboarding')).toBeInTheDocument();

    unmount();
    render(<App />);

    expect(screen.getByText('Новая заметка про onboarding')).toBeInTheDocument();
  });

  it('moves from source signal to an approved post brief', () => {
    render(<App />);

    createApprovedBrief();

    expect(screen.getAllByText('Утверждено').length).toBeGreaterThan(0);
  });

  it('shows an empty editorial review state before an approved brief', () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));

    expect(screen.getByText(/Сначала утвердите фабулу/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Перейти к фабуле/i })).toBeInTheDocument();
  });

  it('shows an empty release state before an approved final text', () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Выпуск/i }));

    expect(screen.getByText(/Сначала утвердите финальный текст/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Перейти в редактуру/i })).toBeInTheDocument();
  });

  it('shows an empty analytics state before manual export', () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Аналитика/i }));

    expect(screen.getByText(/Сначала завершите ручной выпуск/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Перейти в выпуск/i })).toBeInTheDocument();
  });

  it('creates, edits, approves, and persists a final text', () => {
    const { unmount } = render(<App />);

    createApprovedBrief();
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

  it('prepares, marks ready, exports, and persists a manual release package', async () => {
    const { unmount } = render(<App />);

    await createExportedRelease();

    expect(screen.getByText('Telegram')).toBeInTheDocument();
    expect(screen.getByText(/Markdown export/i)).toBeInTheDocument();

    unmount();
    render(<App />);

    expect(screen.getAllByText(/Экспортировано вручную/i).length).toBeGreaterThan(0);
  });

  it('prepares, captures, and persists editorial learning notes after manual export', async () => {
    const { unmount } = render(<App />);

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
    render(<App />);

    expect(screen.getAllByText(/Выводы зафиксированы/i).length).toBeGreaterThan(0);
    expect(screen.getByDisplayValue(/demo-to-adoption gap/i)).toBeInTheDocument();
  });
});
