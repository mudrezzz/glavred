export interface PortfolioTextIntegrityDiagnostic {
  code: 'portfolio-text-integrity-failed';
  charCount: number;
  valueHash: string;
}

const LATIN_MOJIBAKE_MARKERS = ['Ã', 'Â', 'Ð', 'Ñ', 'â€', 'ï¿½'];
const KNOWN_MOJIBAKE_MARKERS = ['вЮша'];
const CYRILLIC_MOJIBAKE_MARKERS = [
  'Рђ', 'Р‘', 'Р’', 'Р“', 'Р”', 'Р•', 'Р–', 'Р—', 'Р', 'Р™', 'Рљ', 'Р›', 'Рњ', 'Рќ', 'Рћ',
  'Рџ', 'Р ', 'РЎ', 'Рў', 'РЈ', 'Р¤', 'РҐ', 'Р¦', 'Р§', 'РЁ', 'Р©', 'Р­', 'Р®', 'РЇ', 'СЃ',
  'С‚', 'СЂ', 'Сѓ', 'С„', 'С…', 'С†', 'С‡', 'С€', 'С‰', 'СЊ', 'С‹', 'СЌ', 'СЋ', 'СЏ',
  'В«', 'В»', 'вЂ'
];

export function inspectPortfolioText(raw: string): PortfolioTextIntegrityDiagnostic | null {
  const latinMojibake = LATIN_MOJIBAKE_MARKERS.some((marker) => raw.includes(marker));
  const knownMojibake = KNOWN_MOJIBAKE_MARKERS.some((marker) => raw.includes(marker));
  const cyrillicHits = CYRILLIC_MOJIBAKE_MARKERS.reduce(
    (count, marker) => count + countOccurrences(raw, marker),
    0
  );
  if (!latinMojibake && !knownMojibake && cyrillicHits < 3 && !raw.includes('\ufffd') && !/\?{4,}/u.test(raw)) return null;
  return {
    code: 'portfolio-text-integrity-failed',
    charCount: raw.length,
    valueHash: stableTextHash(raw)
  };
}

function countOccurrences(value: string, marker: string): number {
  let count = 0;
  let offset = 0;
  while ((offset = value.indexOf(marker, offset)) >= 0) {
    count += 1;
    offset += marker.length;
  }
  return count;
}

function stableTextHash(value: string): string {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16).padStart(8, '0');
}
