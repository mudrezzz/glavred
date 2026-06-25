import { describe, expect, it } from 'vitest';
import {
  DEFAULT_PUBLICATION_SIZE_PROFILE_ID,
  LEGACY_PUBLICATION_SIZE_PROFILES,
  PUBLICATION_SIZE_DEFAULTS_VERSION,
  normalizeFabulaSizeIntent,
  normalizePublicationSizeProfileId,
  normalizePublicationSizeProfiles
} from './publicationSize';

describe('publication size profiles', () => {
  it('normalizes missing profiles to editable defaults', () => {
    const profiles = normalizePublicationSizeProfiles(undefined);

    expect(profiles).toHaveLength(3);
    expect(profiles[0].id).toBe(DEFAULT_PUBLICATION_SIZE_PROFILE_ID);
    expect(profiles[0].hardMaxChars).toBe(10240);
  });

  it('migrates exact legacy built-in profiles to expanded defaults', () => {
    const profiles = normalizePublicationSizeProfiles(LEGACY_PUBLICATION_SIZE_PROFILES, undefined, {
      savedDefaultsVersion: 1
    });

    expect(profiles[0].targetChars).toBe(7000);
    expect(profiles[1].hardMaxChars).toBe(7500);
    expect(profiles[2].maxChars).toBe(22500);
  });

  it('preserves manually edited profiles while bumping defaults elsewhere', () => {
    const custom = [{ ...LEGACY_PUBLICATION_SIZE_PROFILES[0], targetChars: 3333 }];
    const profiles = normalizePublicationSizeProfiles(custom, undefined, { savedDefaultsVersion: 1 });

    expect(profiles[0].targetChars).toBe(3333);
    expect(PUBLICATION_SIZE_DEFAULTS_VERSION).toBe(2);
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
