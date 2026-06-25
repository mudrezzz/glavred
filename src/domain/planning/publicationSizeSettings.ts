import type { ContentPlanSettings } from './types';
import {
  PUBLICATION_SIZE_DEFAULTS_VERSION,
  normalizePublicationSizeProfileId,
  normalizePublicationSizeProfiles
} from './publicationSize';

export function normalizePublicationSizeSettings(
  saved: Partial<ContentPlanSettings> | null | undefined,
  fallback: ContentPlanSettings
) {
  const publicationSizeProfiles = normalizePublicationSizeProfiles(
    saved?.publicationSizeProfiles,
    fallback.publicationSizeProfiles,
    { savedDefaultsVersion: saved?.publicationSizeDefaultsVersion }
  );
  return {
    publicationSizeProfiles,
    defaultPublicationSizeProfileId: normalizePublicationSizeProfileId(
      saved?.defaultPublicationSizeProfileId,
      publicationSizeProfiles,
      fallback.defaultPublicationSizeProfileId
    ),
    publicationSizeDefaultsVersion: PUBLICATION_SIZE_DEFAULTS_VERSION
  };
}
