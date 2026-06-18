import type { PostVisual, PostVisualVariant, VisualMode } from '../domain/editorialWorkspace';

const variantBlueprints: Record<Exclude<VisualMode, 'noVisual'>, Array<{
  title: string;
  previewLabel: string;
  rationale: string;
  risk: string;
}>> = {
  generate: [
    {
      title: 'Контраст до и после пилота',
      previewLabel: 'AI demo -> adoption gap',
      rationale: 'Показывает разрыв между впечатляющим демо и регулярным использованием.',
      risk: 'Не сделать визуал слишком рекламным.'
    },
    {
      title: 'Карта препятствий adoption',
      previewLabel: 'Workflow · evals · trust',
      rationale: 'Собирает причины провала adoption в один понятный образ.',
      risk: 'Не перегрузить деталями.'
    },
    {
      title: 'Сцена рабочего дня пользователя',
      previewLabel: 'Real workflow, not magic',
      rationale: 'Приземляет AI-B2B тему в конкретный рабочий процесс.',
      risk: 'Не уйти в generic office stock.'
    }
  ],
  memeSearch: [
    {
      title: 'Мем про ложный прогресс',
      previewLabel: 'This is fine / demo magic',
      rationale: 'Ищет мем, который высмеивает спокойствие после красивого, но бесполезного демо.',
      risk: 'Проверить уместность и не нарушить тон автора.'
    },
    {
      title: 'Мем про выбор не той метрики',
      previewLabel: 'Distracted metrics',
      rationale: 'Подойдет, если пост спорит с demo applause как метрикой успеха.',
      risk: 'Не выбрать слишком заезженный формат.'
    },
    {
      title: 'Мем про пилот без adoption',
      previewLabel: 'Pilot trap',
      rationale: 'Поддерживает тезис о том, что пилот сам по себе не доказывает продуктовую ценность.',
      risk: 'Нужен мем, понятный B2B-аудитории.'
    }
  ],
  memeRemix: [
    {
      title: 'Кастомизация мема про demo magic',
      previewLabel: 'Meme + AI-B2B labels',
      rationale: 'Берет узнаваемую механику мема и подписывает ее терминами поста.',
      risk: 'Не потерять читаемость после кастомизации.'
    },
    {
      title: 'Мем с заменой объектов на workflow/evals/trust',
      previewLabel: 'Remix with product labels',
      rationale: 'Помогает быстро объяснить, почему adoption ломается не в модели, а в продуктовой системе.',
      risk: 'Потребуется аккуратная работа с исходным мемом.'
    },
    {
      title: 'Гибридный визуал с авторской рамкой',
      previewLabel: 'Meme base + sober caption',
      rationale: 'Сохраняет мемность, но удерживает тон AI Product Manager.',
      risk: 'Не уйти в слишком развлекательный стиль.'
    }
  ]
};

export function createVisualVariants(visual: PostVisual, nextBatch: number): PostVisualVariant[] {
  if (visual.mode === 'noVisual') return [];

  return variantBlueprints[visual.mode].map((blueprint, index) => ({
    id: `${visual.id}-variant-${nextBatch}-${index + 1}`,
    visualId: visual.id,
    mode: visual.mode,
    title: blueprint.title,
    description: visual.brief ? `${blueprint.previewLabel}: ${visual.brief}` : blueprint.previewLabel,
    previewLabel: blueprint.previewLabel,
    rationale: blueprint.rationale,
    risks: [blueprint.risk],
    sourceUrl: visual.mode === 'memeSearch' ? `https://example.test/memes/${nextBatch}-${index + 1}` : undefined
  }));
}
