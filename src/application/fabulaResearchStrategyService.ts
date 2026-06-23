import type { ContentPlanItem, Fabula, InsightCard, PostCandidate, SourceSignal, Topic } from '../domain/editorialWorkspace';
import { normalizeFabulaResearchStrategy } from '../domain/editorial-model/researchStrategy';

export type BriefResearchSourceOrigin = 'fabulaManual' | 'fabulaAuto' | 'userOverride' | 'empty';

export type BriefResearchSourceContext = {
  planItem: ContentPlanItem;
  insight: InsightCard;
  topic?: Topic | null;
  fabula?: Fabula | null;
  candidate?: PostCandidate | null;
  sourceSignal?: SourceSignal | null;
};

export function createBriefResearchSources(context: BriefResearchSourceContext): string[] {
  const strategy = normalizeFabulaResearchStrategy(context.fabula?.researchStrategy);
  if (strategy.mode === 'manual') return strategy.instructions;
  return createAutoResearchSources(context);
}

export function detectBriefResearchSourceOrigin({
  sources,
  fabula,
  expectedAutoSources = []
}: {
  sources: string[];
  fabula?: Pick<Fabula, 'researchStrategy'> | null;
  expectedAutoSources?: string[];
}): BriefResearchSourceOrigin {
  const normalizedSources = normalizeLines(sources);
  if (normalizedSources.length === 0) return 'empty';
  const strategy = normalizeFabulaResearchStrategy(fabula?.researchStrategy);
  if (strategy.mode === 'manual' && sameLines(normalizedSources, strategy.instructions)) return 'fabulaManual';
  if (strategy.mode === 'auto' && sameLines(normalizedSources, expectedAutoSources)) return 'fabulaAuto';
  return 'userOverride';
}

function createAutoResearchSources({
  planItem,
  insight,
  topic,
  fabula,
  candidate,
  sourceSignal
}: BriefResearchSourceContext): string[] {
  return normalizeLines([
    `найти: публичные подтверждения для тезиса "${candidate?.thesis || planItem.title}"`,
    topic?.authorStance
      ? `найти: мнения практиков или лидеров мнений, которые подтверждают или спорят с позицией "${topic.authorStance}"`
      : '',
    sourceSignal?.summary
      ? `проверить: внешние источники вокруг сигнала "${sourceSignal.summary}"`
      : `проверить: внешние источники вокруг темы "${topic?.title || insight.rubric}"`,
    ...((fabula?.proofRequirements ?? []).slice(0, 2).map((item) => `проверить: ${item}`)),
    candidate?.risks?.[0] ? `проверить: риск "${candidate.risks[0]}" не превращается в недоказанный факт` : '',
    'не использовать: vendor blogs без независимых данных'
  ]).slice(0, 6);
}

function normalizeLines(items: string[]): string[] {
  return items.map((item) => item.trim()).filter(Boolean);
}

function sameLines(left: string[], right: string[]): boolean {
  const normalizedRight = normalizeLines(right);
  return left.length === normalizedRight.length && left.every((item, index) => item === normalizedRight[index]);
}
