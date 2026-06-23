import { describe, expect, it } from 'vitest';
import {
  DEFAULT_PUBLICATION_SIZE_PROFILE_ID,
  normalizeFabulaSizeIntent,
  normalizePublicationSizeProfileId,
  normalizePublicationSizeProfiles
} from './publicationSize';

describe('publication size profiles', () => {
  it('normalizes missing profiles to editable defaults', () => {
    const profiles = normalizePublicationSizeProfiles(undefined);

    expect(profiles).toHaveLength(3);
    expect(profiles[0].id).toBe(DEFAULT_PUBLICATION_SIZE_PROFILE_ID);
  });

  it('keeps selected profile id only when it exists', () => {
    const profiles = normalizePublicationSizeProfiles(undefined);

    expect(normalizePublicationSizeProfileId('linkedin-post', profiles)).toBe('linkedin-post');
    expect(normalizePublicationSizeProfileId('missing', profiles)).toBe(DEFAULT_PUBLICATION_SIZE_PROFILE_ID);
  });

  it('normalizes fabula size intent without platform coupling', () => {
    expect(normalizeFabulaSizeIntent('deep')).toBe('deep');
    expect(normalizeFabulaSizeIntent('telegram-only')).toBe('standard');
  });
});
