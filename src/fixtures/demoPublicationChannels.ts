import { createPublicationChannel } from '../domain/publication-channels/transitions';

export function createDemoPublicationChannels() {
  return [
    createPublicationChannel({
      id: 'channel-telegram-main',
      projectId: 'project-ai-design-patterns',
      platform: 'telegram',
      title: 'Telegram',
      language: 'ru',
      defaultPublicationSizeProfileId: 'telegram-post'
    })
  ];
}
