import type { PostVisual, PostVisualMemeReference, PostVisualVariant } from '../domain/editorialWorkspace';

const memeReferenceBlueprints = [
  {
    title: 'This is fine / demo magic',
    previewLabel: 'This is fine',
    rationale: 'Подходит для ситуации, где красивое demo маскирует нерешенную adoption-проблему.',
    risk: 'Мем может быть слишком заезженным, нужен аккуратный подпись и контекст.'
  },
  {
    title: 'Distracted boyfriend / wrong metric',
    previewLabel: 'Wrong metric',
    rationale: 'Хорошо показывает смещение внимания с реального workflow adoption на applause metrics.',
    risk: 'Формат легко становится легкомысленным, важно сохранить B2B-тон.'
  },
  {
    title: 'Drake format / pilot versus rollout',
    previewLabel: 'Pilot vs rollout',
    rationale: 'Понятно разводит пилотную демонстрацию и регулярное внедрение продукта.',
    risk: 'Нужно не упростить тезис до бинарного “пилоты плохие”.'
  }
];

const remixBlueprints = [
  {
    title: 'Кастом с подписями workflow / evals / trust',
    previewLabel: 'Custom labels',
    rationale: 'Сохраняет узнаваемый мем и переносит конфликт в продуктовый язык поста.',
    risk: 'Не перегрузить мем количеством терминов.'
  },
  {
    title: 'Кастом с авторской рамкой adoption gap',
    previewLabel: 'Author frame',
    rationale: 'Делает мем не просто шуткой, а визуальной рамкой авторского тезиса.',
    risk: 'Не потерять считываемость исходного мема.'
  },
  {
    title: 'Кастом для Telegram-поста с короткой punchline',
    previewLabel: 'TG punchline',
    rationale: 'Поддерживает быстрый Telegram-скролл и не требует длинного объяснения.',
    risk: 'Проверить, что punchline не спорит с текстом поста.'
  }
];

export function createMemeReferences(visual: PostVisual, nextBatch: number): PostVisualMemeReference[] {
  if (visual.mode !== 'memeRemix') return [];

  return memeReferenceBlueprints.map((blueprint, index) => ({
    id: `${visual.id}-meme-ref-${nextBatch}-${index + 1}`,
    visualId: visual.id,
    title: blueprint.title,
    description: visual.brief ? `${blueprint.previewLabel}: ${visual.brief}` : blueprint.previewLabel,
    previewLabel: blueprint.previewLabel,
    rationale: blueprint.rationale,
    risks: [blueprint.risk],
    sourceUrl: `https://example.test/meme-references/${nextBatch}-${index + 1}`
  }));
}

export function createMemeRemixVariants(visual: PostVisual, nextBatch: number): PostVisualVariant[] {
  if (visual.mode !== 'memeRemix' || !visual.selectedMemeReferenceId) return [];
  const reference = visual.memeReferences.find((item) => item.id === visual.selectedMemeReferenceId);
  const referenceLabel = reference?.previewLabel ?? visual.memeReferenceTitle;

  return remixBlueprints.map((blueprint, index) => ({
    id: `${visual.id}-variant-${nextBatch}-${index + 1}`,
    visualId: visual.id,
    mode: 'memeRemix',
    title: blueprint.title,
    description: `${referenceLabel}: ${visual.brief}`,
    previewLabel: blueprint.previewLabel,
    rationale: blueprint.rationale,
    risks: [blueprint.risk],
    sourceUrl: reference?.sourceUrl
  }));
}
