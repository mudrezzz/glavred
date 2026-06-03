import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { App } from './App';

describe('App', () => {
  it('renders the project foundation and workflow baseline', () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: 'Glavred' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Editorial loop' })).toBeInTheDocument();
    expect(screen.getByText('First approval gate:')).toBeInTheDocument();
    expect(screen.getAllByText('Plan')).toHaveLength(2);
  });
});
