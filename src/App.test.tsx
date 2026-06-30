import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from './App';
import { renderAppCabinet } from './test-support/appFlowDriver';

describe('App shell', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders the editorial cabinet shell and planned sections', () => {
    renderAppCabinet();

    expect(screen.getByText('Главред')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Память автора/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Редакционная модель/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Сигналы/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /^Радар/i })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /План/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /^Фабулы/i })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Редактура/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Выпуск/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Аналитика/i })).toBeInTheDocument();
  });
});
