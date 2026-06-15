import type {
  AuthorMemoryEvent,
  AuthorNote,
  AuthorPositionAssertion
} from '../domain/editorialWorkspace';

export function createAuthorMemoryEvent(note: AuthorNote): AuthorMemoryEvent {
  return {
    id: `memory-${note.id}`,
    noteId: note.id,
    type: note.type,
    summary: summarizeAuthorNote(note),
    detectedSignals: detectAuthorSignals(note),
    createdAt: new Date().toISOString()
  };
}

export function inferAuthorPositionAssertions(
  notes: AuthorNote[],
  events: AuthorMemoryEvent[]
): AuthorPositionAssertion[] {
  const evidence = (noteIds: string[], reason: string) =>
    Array.from(new Set(noteIds))
      .map((noteId) => notes.find((note) => note.id === noteId))
      .filter((note): note is AuthorNote => Boolean(note))
      .map((note) => ({
        noteId: note.id,
        quote: excerpt(note.body),
        reason
      }));

  const signalNotes = (signal: string) =>
    events.filter((event) => event.detectedSignals.includes(signal)).map((event) => event.noteId);

  const workflowNotes = signalNotes('workflow-risk');
  const evalNotes = signalNotes('evals');
  const adoptionNotes = signalNotes('adoption');
  const trustNotes = signalNotes('trust');
  const confidenceNotes = signalNotes('confidence-boundaries');

  return [
    {
      id: 'assertion-persona-ai-product-manager',
      type: 'persona',
      title: 'AI Product Manager с исследовательской оптикой',
      statement:
        'Автор смотрит на AI-B2B продукт как на исследование workflow, adoption, доверия и экономики внедрения, а не как на демонстрацию модели.',
      confidence: confidenceFor([...workflowNotes, ...adoptionNotes, ...trustNotes]),
      evidence: evidence(
        [...workflowNotes, ...adoptionNotes, ...trustNotes],
        'Заметки фиксируют продуктовую, а не инструментальную оптику автора.'
      ),
      status: 'inferred'
    },
    {
      id: 'assertion-style-research-notes',
      type: 'style',
      title: 'Стиль: исследовательские заметки без демо-магии',
      statement:
        'Тон должен быть спокойным, наблюдательным и проверяющим: меньше хайпа, больше границ применимости, evidence и честных trade-offs.',
      confidence: confidenceFor([...evalNotes, ...trustNotes, ...confidenceNotes]),
      evidence: evidence(
        [...evalNotes, ...trustNotes, ...confidenceNotes],
        'Evidence показывает интерес автора к проверкам, границам уверенности и доверию.'
      ),
      status: 'inferred'
    },
    {
      id: 'assertion-audience-ai-b2b-builders',
      type: 'audience',
      title: 'Аудитория: строители AI-B2B продуктов',
      statement:
        'Блог должен говорить с AI PM, founders, CPO и B2B SaaS командами, которым нужно довести AI-функцию от пилота до повторяемого adoption.',
      confidence: confidenceFor([...adoptionNotes, ...workflowNotes]),
      evidence: evidence(
        [...adoptionNotes, ...workflowNotes],
        'Заметки явно привязаны к GTM, adoption и продуктовым решениям после пилота.'
      ),
      status: 'inferred'
    },
    {
      id: 'assertion-topic-ai-b2b-product-system',
      type: 'topic',
      title: 'Главная тема: система AI-B2B продукта',
      statement:
        'Сильные темы автора: workflow risk, evals как продуктовая функция, trust loop, adoption после пилота и объяснение границ уверенности.',
      confidence: confidenceFor([...workflowNotes, ...evalNotes, ...trustNotes, ...confidenceNotes]),
      evidence: evidence(
        [...workflowNotes, ...evalNotes, ...trustNotes, ...confidenceNotes],
        'Повторяются темы workflow, evals, trust loop и confidence boundaries.'
      ),
      status: 'inferred'
    },
    {
      id: 'assertion-principle-no-demo-magic',
      type: 'principle',
      title: 'Принцип: демо не равно продукт',
      statement:
        'AI-фича становится продуктом только тогда, когда у нее есть evals, объяснимые границы, rollback, adoption loop и понятная экономика внедрения.',
      confidence: confidenceFor([...evalNotes, ...adoptionNotes, ...confidenceNotes]),
      evidence: evidence(
        [...evalNotes, ...adoptionNotes, ...confidenceNotes],
        'Заметки противопоставляют красивое демо реальному productization.'
      ),
      status: 'inferred'
    }
  ];
}

function summarizeAuthorNote(note: AuthorNote): string {
  const prefix: Record<AuthorNote['type'], string> = {
    thought: 'Мысль автора',
    linkReaction: 'Реакция на источник',
    manualCorrection: 'Ручная корректировка'
  };

  const title = note.title.trim() || excerpt(note.body);
  return `${prefix[note.type]}: ${title}`;
}

function detectAuthorSignals(note: AuthorNote): string[] {
  const normalized = `${note.title} ${note.body} ${note.tags.join(' ')}`.toLowerCase();
  const signals: string[] = [];

  if ((note.attachments ?? []).length > 0) {
    signals.push('attached-material');
  }

  if (matches(normalized, ['workflow', 'процесс', 'сценар', 'risk', 'риск'])) {
    signals.push('workflow-risk');
  }

  if (matches(normalized, ['eval', 'оценк', 'метрик', 'провер', 'quality'])) {
    signals.push('evals');
  }

  if (matches(normalized, ['adoption', 'gtm', 'пилот', 'внедрен', 'rollout'])) {
    signals.push('adoption');
  }

  if (matches(normalized, ['trust', 'довер', 'enterprise', 'rollback', 'evidence'])) {
    signals.push('trust');
  }

  if (matches(normalized, ['уверенн', 'confidence', 'границ', 'не знает', 'объясн'])) {
    signals.push('confidence-boundaries');
  }

  return signals.length > 0 ? signals : ['author-observation'];
}

function matches(value: string, needles: string[]): boolean {
  return needles.some((needle) => value.includes(needle));
}

function excerpt(value: string): string {
  return value.length > 180 ? `${value.slice(0, 177)}...` : value;
}

function confidenceFor(noteIds: string[]): number {
  const unique = new Set(noteIds);
  return Math.min(0.95, 0.62 + unique.size * 0.08);
}
