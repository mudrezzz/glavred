import { describe, expect, it } from 'vitest';
import { normalizeWorkspace } from './localWorkspaceStore';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';

describe('local workspace fabula research strategy normalization', () => {
  it('adds auto research strategy to legacy fabulas', () => {
    const workspace = createDemoWorkspace();
    const legacyFabulas = workspace.fabulas.map(({ researchStrategy: _researchStrategy, ...fabula }) => fabula);

    const normalized = normalizeWorkspace({ ...workspace, fabulas: legacyFabulas as typeof workspace.fabulas });

    expect(normalized.fabulas.every((fabula) => fabula.researchStrategy.mode === 'auto')).toBe(true);
    expect(normalized.fabulas.every((fabula) => Array.isArray(fabula.researchStrategy.instructions))).toBe(true);
  });
});
