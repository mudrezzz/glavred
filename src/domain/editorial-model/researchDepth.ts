export type FabulaResearchDepth = 'light' | 'standard' | 'deep' | 'marketResearch';

export const defaultFabulaResearchDepth: FabulaResearchDepth = 'standard';

export const FABULA_RESEARCH_DEPTH_LABELS: Record<FabulaResearchDepth, string> = {
  light: 'Легкая',
  standard: 'Стандарт',
  deep: 'Глубокая',
  marketResearch: 'Market research'
};

const DEPTHS = new Set<FabulaResearchDepth>(['light', 'standard', 'deep', 'marketResearch']);

export function normalizeFabulaResearchDepth(value: unknown): FabulaResearchDepth {
  return typeof value === 'string' && DEPTHS.has(value as FabulaResearchDepth)
    ? (value as FabulaResearchDepth)
    : defaultFabulaResearchDepth;
}

export function fabulaResearchDepthLabel(value: unknown): string {
  return FABULA_RESEARCH_DEPTH_LABELS[normalizeFabulaResearchDepth(value)];
}
