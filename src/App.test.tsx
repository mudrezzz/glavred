import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { App } from './App';

describe('App', () => {
  it('renders the project foundation and workflow baseline', () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: 'Glavred' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Editorial loop' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'First five modules' })).toBeInTheDocument();
    expect(screen.getByText('Approval gates:')).toBeInTheDocument();
    expect(screen.getAllByText('Content Plan')).toHaveLength(2);
  });
});
