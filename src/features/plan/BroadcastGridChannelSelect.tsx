import type { ContentPlanItem, WorkspaceState } from '../../domain/editorialWorkspace';
import {
  publicationChannelLabel,
  resolvePlanItemPublicationChannel
} from '../../domain/publication-channels/transitions';

export function BroadcastGridChannelSelect({
  item,
  workspace,
  onChange
}: {
  item: ContentPlanItem;
  workspace: WorkspaceState;
  onChange: (channelId: string) => void;
}) {
  return (
    <select value={resolvePlanItemPublicationChannel(item, workspace.publicationChannels)?.id ?? ''} onChange={(event) => onChange(event.target.value)}>
      {workspace.publicationChannels
        .filter((channel) => channel.status === 'active' || channel.id === item.channelId)
        .map((channel) => <option value={channel.id} key={channel.id}>{publicationChannelLabel(channel)}</option>)}
    </select>
  );
}
