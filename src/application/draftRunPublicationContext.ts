import type { WorkspaceState } from '../domain/editorialWorkspace';

type WorkItem = WorkspaceState['editorialWorkItems'][number] | null;
type PlanSlot = WorkspaceState['contentPlanItems'][number] | null;
type Fabula = WorkspaceState['fabulas'][number] | null;

export function buildPublicationSizeContext(
  workspace: WorkspaceState,
  workItem: WorkItem,
  planSlot: PlanSlot,
  fabula: Fabula
): Record<string, unknown> {
  const settings = workspace.contentPlanSettings;
  const selectedProfileId =
    planSlot?.publicationSizeProfileId ??
    settings.defaultPublicationSizeProfileId ??
    null;
  const selectedProfile =
    settings.publicationSizeProfiles.find((profile) => profile.id === selectedProfileId) ??
    settings.publicationSizeProfiles.find((profile) => profile.platform === (planSlot?.platform ?? workItem?.platform)) ??
    settings.publicationSizeProfiles[0] ??
    null;

  return {
    slotProfileId: planSlot?.publicationSizeProfileId ?? null,
    defaultProfileId: settings.defaultPublicationSizeProfileId,
    selectedProfileId: selectedProfile?.id ?? null,
    selectedProfile,
    availableProfiles: settings.publicationSizeProfiles,
    fabulaSizeIntent: fabula?.sizeIntent ?? 'standard',
    platform: planSlot?.platform ?? workItem?.platform ?? settings.defaultPlatform
  };
}
