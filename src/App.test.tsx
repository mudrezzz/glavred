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

    expect(screen.getByText('Утверждено')).toBeInTheDocument();
  });
});
