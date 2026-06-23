import type { ContentPlanSettings } from './types';
import {
  normalizePublicationSizeProfileId,
  normalizePublicationSizeProfiles
} from './publicationSize';

export function normalizePublicationSizeSettings(
  saved: Partial<ContentPlanSettings> | null | undefined,
  fallback: ContentPlanSettings
) {
  const publicationSizeProfiles = normalizePublicationSizeProfiles(
    saved?.publicationSizeProfiles,
    fallback.publicationSizeProfiles
  );
  return {
    publicationSizeProfiles,
    defaultPublicationSizeProfileId: normalizePublicationSizeProfileId(
      saved?.defaultPublicationSizeProfileId,
      publicationSizeProfiles,
      fallback.defaultPublicationSizeProfileId
    )
  };
}
