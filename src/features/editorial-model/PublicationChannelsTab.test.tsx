import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { createDemoWorkspace } from '../../fixtures/demoWorkspace';
import { PublicationChannelsTab } from './PublicationChannelsTab';

describe('PublicationChannelsTab', () => {
  it('renders channels as compact entity rows, not freeform text cards', () => {
    const workspace = createDemoWorkspace();
    const channel = workspace.publicationChannels[0];

    render(
      <PublicationChannelsTab
        channels={workspace.publicationChannels}
        planItems={workspace.contentPlanItems}
        settings={workspace.contentPlanSettings}
        onChange={vi.fn()}
      />
    );

    const row = screen.getByRole('button', { name: channel.title }).closest('article');
    expect(row).toHaveClass('entity-row');
    expect(row).not.toHaveClass('publication-channel-card');
    expect(within(row as HTMLElement).getByText(/активно|пауза/)).toHaveClass('status-chip');
  });

  it('renders expanded details inside the row and edits by replacing details with a form', () => {
    const workspace = createDemoWorkspace();
    const channel = workspace.publicationChannels[0];

    render(
      <PublicationChannelsTab
        channels={workspace.publicationChannels}
        planItems={[{ ...workspace.contentPlanItems[0], channelId: channel.id }]}
        settings={workspace.contentPlanSettings}
        onChange={vi.fn()}
      />
    );

    const row = screen.getByRole('button', { name: channel.title }).closest('article') as HTMLElement;
    expect(row.querySelector('.entity-details')).toBeTruthy();
    expect(row.querySelector('.entity-edit-form')).toBeNull();

    fireEvent.click(within(row).getByRole('button', { name: 'Редактировать' }));

    expect(row.querySelector('.entity-details')).toBeNull();
    expect(row.querySelector('.entity-edit-form')).toBeTruthy();
    expect(row.querySelector('.publication-channel-editor')).toBeTruthy();
  });

  it('does not expose legacy channel audience as an editable channel field', () => {
    const workspace = createDemoWorkspace();
    const channel = { ...workspace.publicationChannels[0], audience: 'Legacy channel audience' };

    render(
      <PublicationChannelsTab
        channels={[channel]}
        planItems={workspace.contentPlanItems}
        settings={workspace.contentPlanSettings}
        onChange={vi.fn()}
      />
    );

    const row = screen.getByRole('button', { name: channel.title }).closest('article') as HTMLElement;
    expect(within(row).queryByText('Legacy channel audience')).toBeNull();

    fireEvent.click(within(row).getByRole('button', { name: /Редактировать|Р РµРґР°РєС‚РёСЂРѕРІР°С‚СЊ/ }));

    expect(within(row).queryByDisplayValue('Legacy channel audience')).toBeNull();
  });

  it('pauses referenced channel instead of deleting it', () => {
    const workspace = createDemoWorkspace();
    const channel = workspace.publicationChannels[0];
    const onChange = vi.fn();

    render(
      <PublicationChannelsTab
        channels={workspace.publicationChannels}
        planItems={[{ ...workspace.contentPlanItems[0], channelId: channel.id }]}
        settings={workspace.contentPlanSettings}
        onChange={onChange}
      />
    );

    const row = screen.getByRole('button', { name: channel.title }).closest('article') as HTMLElement;
    fireEvent.click(within(row).getByRole('button', { name: 'Пауза вместо удаления' }));

    expect(onChange).toHaveBeenCalledWith([
      expect.objectContaining({ id: channel.id, status: 'paused' })
    ]);
  });

  it('creates a new channel from the entity-row editor form', () => {
    const workspace = createDemoWorkspace();
    const onChange = vi.fn();

    render(
      <PublicationChannelsTab
        channels={workspace.publicationChannels}
        planItems={[]}
        settings={workspace.contentPlanSettings}
        onChange={onChange}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: '+ Канал' }));
    const editor = screen.getByText('Сохранить').closest('.publication-channel-editor') as HTMLElement;
    fireEvent.change(within(editor).getByLabelText('Название'), { target: { value: 'Дзен' } });
    fireEvent.change(within(editor).getByLabelText('Платформа'), { target: { value: 'dzen' } });
    fireEvent.change(within(editor).getByLabelText('Язык'), { target: { value: 'ru' } });
    fireEvent.click(within(editor).getByRole('button', { name: 'Сохранить' }));

    expect(onChange).toHaveBeenCalledWith([
      expect.objectContaining({ title: 'Дзен', platform: 'dzen', status: 'active' }),
      ...workspace.publicationChannels
    ]);
  });
});
