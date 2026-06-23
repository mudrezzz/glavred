export type BriefSourceIntentKind = 'url' | 'namedSource' | 'researchRequest' | 'proofNeed' | 'framingHint' | 'exclusion' | 'unknown';

export type BriefSourceIntentPreviewItem = {
  id: string;
  raw: string;
  kind: BriefSourceIntentKind;
  label: string;
  value: string;
};

const PREFIXES: Array<[string, BriefSourceIntentKind, string]> = [
  ['url:', 'url', 'URL'],
  ['источник:', 'namedSource', 'Источник'],
  ['source:', 'namedSource', 'Источник'],
  ['найти:', 'researchRequest', 'Найти'],
  ['search:', 'researchRequest', 'Найти'],
  ['проверить:', 'proofNeed', 'Проверить'],
  ['verify:', 'proofNeed', 'Проверить'],
  ['контекст:', 'framingHint', 'Контекст'],
  ['framing:', 'framingHint', 'Контекст'],
  ['не использовать:', 'exclusion', 'Не использовать'],
  ['exclude:', 'exclusion', 'Не использовать']
];

const REQUEST_MARKERS = ['найти', 'поиск', 'мнение', 'лидер', 'эксперт', 'кто пишет', 'что говорят', 'исследовать'];
const PROOF_MARKERS = ['проверить', 'статистик', 'данн', 'цифр', 'подтверд', 'доказ'];
const EXCLUSION_MARKERS = ['не использовать', 'исключить', 'без vendor', 'без вендор'];
const FRAMING_MARKERS = ['контекст', 'рамка', 'для фрейминга', 'как фон'];

export function buildBriefSourceIntentPreview(value: string): BriefSourceIntentPreviewItem[] {
  return value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((raw, index) => ({
      id: `source-intent-${index}`,
      raw,
      ...classifyBriefSourceLine(raw)
    }));
}

export function classifyBriefSourceLine(raw: string): Omit<BriefSourceIntentPreviewItem, 'id' | 'raw'> {
  const lower = raw.toLowerCase();
  for (const [prefix, kind, label] of PREFIXES) {
    if (lower.startsWith(prefix)) {
      return { kind, label, value: raw.slice(prefix.length).trim() || raw };
    }
  }
  if (/^https?:\/\/\S+/i.test(raw)) return { kind: 'url', label: 'URL', value: raw };
  if (EXCLUSION_MARKERS.some((marker) => lower.includes(marker))) return { kind: 'exclusion', label: 'Не использовать', value: raw };
  if (PROOF_MARKERS.some((marker) => lower.includes(marker))) return { kind: 'proofNeed', label: 'Проверить', value: raw };
  if (REQUEST_MARKERS.some((marker) => lower.includes(marker))) return { kind: 'researchRequest', label: 'Найти', value: raw };
  if (FRAMING_MARKERS.some((marker) => lower.includes(marker))) return { kind: 'framingHint', label: 'Контекст', value: raw };
  if (raw.length < 80 && !/[.!?]$/.test(raw)) return { kind: 'namedSource', label: 'Источник', value: raw };
  return { kind: 'researchRequest', label: 'Поручение', value: raw };
}
