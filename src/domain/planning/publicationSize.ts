export type PublicationKind = 'shortPost' | 'longPost' | 'article';
export type PublicationDensity = 'compact' | 'normal' | 'deep';
export type FabulaSizeIntent = 'compact' | 'standard' | 'deep';

export interface PublicationSizeRange {
  min: number;
  max: number;
}

export interface PublicationSizeProfile {
  id: string;
  title: string;
  platform: string;
  publicationKind: PublicationKind;
  minChars: number;
  targetChars: number;
  maxChars: number;
  hardMaxChars: number;
  paragraphRange: PublicationSizeRange;
  sectionRange: PublicationSizeRange;
  density: PublicationDensity;
}

export const DEFAULT_PUBLICATION_SIZE_PROFILE_ID = 'telegram-post';

export const DEFAULT_PUBLICATION_SIZE_PROFILES: PublicationSizeProfile[] = [
  {
    id: 'telegram-post',
    title: 'Telegram post',
    platform: 'Telegram',
    publicationKind: 'shortPost',
    minChars: 1800,
    targetChars: 2800,
    maxChars: 3800,
    hardMaxChars: 4096,
    paragraphRange: { min: 4, max: 8 },
    sectionRange: { min: 1, max: 1 },
    density: 'normal'
  },
  {
    id: 'linkedin-post',
    title: 'LinkedIn post',
    platform: 'LinkedIn',
    publicationKind: 'longPost',
    minChars: 1200,
    targetChars: 2200,
    maxChars: 2800,
    hardMaxChars: 3000,
    paragraphRange: { min: 4, max: 7 },
    sectionRange: { min: 1, max: 1 },
    density: 'compact'
  },
  {
    id: 'linkedin-article',
    title: 'LinkedIn article',
    platform: 'LinkedIn',
    publicationKind: 'article',
    minChars: 5000,
    targetChars: 7000,
    maxChars: 9000,
    hardMaxChars: 11000,
    paragraphRange: { min: 10, max: 18 },
    sectionRange: { min: 3, max: 6 },
    density: 'deep'
  }
];

const VALID_KINDS: PublicationKind[] = ['shortPost', 'longPost', 'article'];
const VALID_DENSITIES: PublicationDensity[] = ['compact', 'normal', 'deep'];
const VALID_SIZE_INTENTS: FabulaSizeIntent[] = ['compact', 'standard', 'deep'];

export function normalizePublicationSizeProfiles(
  saved: PublicationSizeProfile[] | undefined,
  fallback: PublicationSizeProfile[] = DEFAULT_PUBLICATION_SIZE_PROFILES
): PublicationSizeProfile[] {
  const profiles = (saved ?? [])
    .map((profile, index) => normalizePublicationSizeProfile(profile, fallback[index] ?? fallback[0]))
    .filter((profile): profile is PublicationSizeProfile => profile !== null);
  return profiles.length > 0 ? profiles : fallback.map((profile) => ({ ...profile }));
}

export function normalizePublicationSizeProfileId(
  savedId: string | undefined,
  profiles: PublicationSizeProfile[],
  fallbackId = DEFAULT_PUBLICATION_SIZE_PROFILE_ID
): string {
  const saved = profiles.find((profile) => profile.id === savedId)?.id;
  if (saved) return saved;
  return profiles.find((profile) => profile.id === fallbackId)?.id ?? profiles[0]?.id ?? fallbackId;
}

export function normalizeFabulaSizeIntent(value: unknown): FabulaSizeIntent {
  return VALID_SIZE_INTENTS.includes(value as FabulaSizeIntent) ? value as FabulaSizeIntent : 'standard';
}

function normalizePublicationSizeProfile(
  profile: Partial<PublicationSizeProfile> | undefined,
  fallback: PublicationSizeProfile
): PublicationSizeProfile | null {
  if (!profile && !fallback) return null;
  const base = fallback ?? DEFAULT_PUBLICATION_SIZE_PROFILES[0];
  const hardMaxChars = clampInteger(profile?.hardMaxChars, base.hardMaxChars, 500, 100000);
  const minChars = clampInteger(profile?.minChars, base.minChars, 100, hardMaxChars);
  const targetChars = clampInteger(profile?.targetChars, base.targetChars, minChars, hardMaxChars);
  const maxChars = clampInteger(profile?.maxChars, base.maxChars, targetChars, hardMaxChars);
  return {
    id: normalizeText(profile?.id, base.id),
    title: normalizeText(profile?.title, base.title),
    platform: normalizeText(profile?.platform, base.platform),
    publicationKind: VALID_KINDS.includes(profile?.publicationKind as PublicationKind)
      ? profile?.publicationKind as PublicationKind
      : base.publicationKind,
    minChars,
    targetChars,
    maxChars,
    hardMaxChars,
    paragraphRange: normalizeRange(profile?.paragraphRange, base.paragraphRange, 1, 60),
    sectionRange: normalizeRange(profile?.sectionRange, base.sectionRange, 1, 30),
    density: VALID_DENSITIES.includes(profile?.density as PublicationDensity)
      ? profile?.density as PublicationDensity
      : base.density
  };
}

function normalizeRange(
  range: Partial<PublicationSizeRange> | undefined,
  fallback: PublicationSizeRange,
  min: number,
  max: number
): PublicationSizeRange {
  const rangeMin = clampInteger(range?.min, fallback.min, min, max);
  return { min: rangeMin, max: clampInteger(range?.max, fallback.max, rangeMin, max) };
}

function normalizeText(value: unknown, fallback: string): string {
  return typeof value === 'string' && value.trim() ? value.trim() : fallback;
}

function clampInteger(value: number | undefined, fallback: number, min: number, max: number): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) return fallback;
  return Math.min(max, Math.max(min, Math.round(value)));
}
