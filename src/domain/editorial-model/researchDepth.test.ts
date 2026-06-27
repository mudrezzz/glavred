import { describe, expect, it } from 'vitest';
import { fabulaResearchDepthLabel, normalizeFabulaResearchDepth } from './researchDepth';

describe('fabula research depth', () => {
  it('normalizes legacy or invalid values to standard', () => {
    expect(normalizeFabulaResearchDepth(undefined)).toBe('standard');
    expect(normalizeFabulaResearchDepth('unknown')).toBe('standard');
  });

  it('keeps valid research depth values', () => {
    expect(normalizeFabulaResearchDepth('marketResearch')).toBe('marketResearch');
    expect(fabulaResearchDepthLabel('deep')).toBe('Глубокая');
  });
});
