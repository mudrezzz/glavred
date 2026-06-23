import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { BriefSourceIntentEditor } from './BriefSourceIntentEditor';
import { buildBriefSourceIntentPreview } from './briefSourceIntentPreview';

describe('BriefSourceIntentEditor', () => {
  it('keeps textarea as raw sources input and shows source intent preview', () => {
    const onChange = vi.fn();

    render(
      <BriefSourceIntentEditor
        value={'url: https://example.com/report\nнайти: мнение лидеров мнений\nпроверить: adoption stats\nне использовать: vendor blogs'}
        onChange={onChange}
      />
    );

    expect(screen.getByText('URL')).toBeInTheDocument();
    expect(screen.getByText('Найти')).toBeInTheDocument();
    expect(screen.getByText('Проверить')).toBeInTheDocument();
    expect(screen.getByText('Не использовать')).toBeInTheDocument();

    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Ben Thompson Stratechery' } });

    expect(onChange).toHaveBeenCalledWith('Ben Thompson Stratechery');
  });

  it('classifies plain human requests as research requests', () => {
    const preview = buildBriefSourceIntentPreview('нужно мнение лидеров мнений по этой теме');

    expect(preview[0]).toEqual(
      expect.objectContaining({
        kind: 'researchRequest',
        label: 'Найти'
      })
    );
  });
});
