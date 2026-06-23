import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { createFabulaDraft } from '../../domain/editorialWorkspace';
import { FabulaResearchStrategyEditor } from './FabulaResearchStrategyEditor';

describe('FabulaResearchStrategyEditor', () => {
  it('switches from auto mode to manual instructions and shows source intent preview', () => {
    const onChange = vi.fn();
    const fabula = createFabulaDraft();

    render(<FabulaResearchStrategyEditor fabula={fabula} onChange={onChange} />);

    expect(screen.getByText(/предложит источники/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /задать вручную/i }));
    expect(onChange).toHaveBeenLastCalledWith(expect.objectContaining({
      researchStrategy: expect.objectContaining({ mode: 'manual' })
    }));

    const manualFabula = { ...fabula, researchStrategy: { mode: 'manual' as const, instructions: [] } };
    onChange.mockClear();
    render(<FabulaResearchStrategyEditor fabula={manualFabula} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText(/поручения для источников/i), {
      target: { value: 'найти: мнение лидеров мнений\nне использовать: vendor blogs' }
    });

    expect(onChange).toHaveBeenLastCalledWith(expect.objectContaining({
      researchStrategy: {
        mode: 'manual',
        instructions: ['найти: мнение лидеров мнений', 'не использовать: vendor blogs']
      }
    }));
  });

  it('preserves spaces while typing manual instructions', () => {
    const onChange = vi.fn();
    const fabula = {
      ...createFabulaDraft(),
      researchStrategy: { mode: 'manual' as const, instructions: ['найти: лидеров'] }
    };

    render(<FabulaResearchStrategyEditor fabula={fabula} onChange={onChange} />);
    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'найти: лидеров ' }
    });

    expect(onChange).toHaveBeenLastCalledWith(expect.objectContaining({
      researchStrategy: expect.objectContaining({
        mode: 'manual',
        instructions: ['найти: лидеров ']
      })
    }));
  });
});
