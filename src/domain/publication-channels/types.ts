export type PublicationPlatform = 'telegram' | 'linkedin' | 'dzen' | 'site' | 'other';
export type PublicationChannelRole = 'primary' | 'repurpose' | 'experiment' | 'archive';
export type PublicationChannelPublishingMode = 'manual' | 'adapterPlanned' | 'connected';
export type PublicationChannelStatus = 'active' | 'paused';

export interface PublicationChannel {
  id: string;
  projectId: string;
  platform: PublicationPlatform;
  title: string;
  handleOrUrl: string;
  language: string;
  audience: string;
  role: PublicationChannelRole;
  publishingMode: PublicationChannelPublishingMode;
  status: PublicationChannelStatus;
  defaultPublicationSizeProfileId?: string;
}

export interface PublicationChannelValidationResult {
  status: 'ok' | 'warning' | 'critical';
  messages: string[];
}
