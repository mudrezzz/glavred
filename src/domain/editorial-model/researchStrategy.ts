export type FabulaResearchStrategyMode = 'auto' | 'manual';

export interface FabulaResearchStrategy {
  mode: FabulaResearchStrategyMode;
  instructions: string[];
  autoSeedNote?: string;
}

export const defaultFabulaResearchStrategy: FabulaResearchStrategy = {
  mode: 'auto',
  instructions: []
};

export function normalizeFabulaResearchStrategy(
  strategy: Partial<FabulaResearchStrategy> | null | undefined
): FabulaResearchStrategy {
  const mode = strategy?.mode === 'manual' ? 'manual' : 'auto';
  const instructions = (strategy?.instructions ?? [])
    .map((item) => item.trim())
    .filter(Boolean);
  const autoSeedNote = strategy?.autoSeedNote?.trim();

  return {
    mode,
    instructions,
    ...(autoSeedNote ? { autoSeedNote } : {})
  };
}
