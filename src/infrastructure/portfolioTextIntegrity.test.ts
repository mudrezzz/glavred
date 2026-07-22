import { describe, expect, it } from 'vitest';
import { inspectPortfolioText } from './portfolioTextIntegrity';

describe('inspectPortfolioText', () => {
  it('accepts normal Russian, English, punctuation, and URLs', () => {
    const value = JSON.stringify({
      title: 'Опытный цех «Сборочная» — AI maintenance',
      url: 'https://example.test/search?q=предиктивное+обслуживание&ref=radar'
    });

    expect(inspectPortfolioText(value)).toBeNull();
  });

  it('detects repeated mojibake without retaining the damaged value', () => {
    const value = JSON.stringify({ title: 'РџСЂРёРІРµС‚ РјРёСЂ РџСЂРёРІРµС‚' });

    expect(inspectPortfolioText(value)).toEqual(expect.objectContaining({
      code: 'portfolio-text-integrity-failed',
      charCount: value.length,
      valueHash: expect.any(String)
    }));
  });

  it('detects the observed short mixed-script corruption signature', () => {
    const value = JSON.stringify({ source: 'Public industrial AI cases, вЮша/EAM materials' });

    expect(inspectPortfolioText(value)).toEqual(expect.objectContaining({
      code: 'portfolio-text-integrity-failed'
    }));
  });
});
