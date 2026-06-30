import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from '../../App';
import { renderAppCabinet } from '../../test-support/appFlowDriver';

describe('Author memory app flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('opens on author memory with demo notes and evidence-backed assertions', () => {
    renderAppCabinet();

    expect(screen.getByText('Авторская память')).toBeInTheDocument();
    expect(screen.getByText(/Workflow risk важнее выбора модели/i)).toBeInTheDocument();
    expect(screen.getByText(/AI Product Manager с исследовательской оптикой/i)).toBeInTheDocument();
    expect(screen.getByText(/Как система поняла автора/i)).toBeInTheDocument();
  });

  it('shows external source tabs and demo sources as a single-column list inside author memory', () => {
    renderAppCabinet();

    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    expect(screen.getByText('Импорт и архив')).toBeInTheDocument();
    expect(screen.getAllByText('Источники').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Кандидаты').length).toBeGreaterThan(0);
    expect(screen.getByRole('tab', { name: /Лента|Р›РµРЅС‚Р°/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Источники|РСЃС‚РѕС‡РЅРёРєРё/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Очередь разбора|РћС‡РµСЂРµРґСЊ СЂР°Р·Р±РѕСЂР°/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Архив|РђСЂС…РёРІ/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Источники|РСЃС‚РѕС‡РЅРёРєРё/i }));

    expect(screen.getByText('TG archive · AI Product Manager')).toBeInTheDocument();
    expect(screen.getByText('Customer interviews · AI adoption')).toBeInTheDocument();
    expect(screen.getByText('Blog essays · Evals and trust')).toBeInTheDocument();
    expect(screen.getByTestId('external-source-list')).toBeInTheDocument();
    expect(document.querySelector('.source-grid')).toBeNull();
    expect(document.querySelectorAll('.source-row').length).toBeGreaterThan(1);
    expect(document.querySelector('.source-row-main')).toBeInTheDocument();
    expect(document.querySelector('.source-row-meta-bar')).toBeInTheDocument();
    expect(document.querySelector('.source-title-button')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Customer interviews/i }));
    const sourceRow = screen.getByRole('button', { name: /Customer interviews/i }).closest('article') as HTMLElement;
    expect(sourceRow.querySelector('.source-row-details')).toBeInTheDocument();
  });

  it('allows clearing import candidate selection', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('tab', { name: /Очередь разбора|РћС‡РµСЂРµРґСЊ СЂР°Р·Р±РѕСЂР°/i }));
    fireEvent.click(screen.getByRole('button', { name: /Выбрать все по фильтру|Р’С‹Р±СЂР°С‚СЊ РІСЃРµ РїРѕ С„РёР»СЊС‚СЂСѓ/i }));

    expect(screen.getByRole('button', { name: /Сбросить выделение/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Снять выделение по фильтру/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Сбросить выделение/i }));

    expect(screen.queryByRole('button', { name: /Сбросить выделение/i })).not.toBeInTheDocument();
    expect(screen.getByText(/выбрано 0/i)).toBeInTheDocument();
  });

  it('makes archive records actionable and can return an archive record to review queue', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('tab', { name: /Архив|РђСЂС…РёРІ/i }));
    const archiveRecord = screen.getByText(/Старый пост про пилоты/i).closest('article');
    expect(archiveRecord).toBeInTheDocument();

    expect(within(archiveRecord as HTMLElement).getByRole('button', { name: /Добавить в память/i })).toBeInTheDocument();
    expect(within(archiveRecord as HTMLElement).getByRole('button', { name: /Вернуть в очередь/i })).toBeInTheDocument();
    expect(within(archiveRecord as HTMLElement).getByRole('button', { name: /Не evidence/i })).toBeInTheDocument();
    expect(within(archiveRecord as HTMLElement).getByRole('button', { name: /Удалить из архива/i })).toBeInTheDocument();

    fireEvent.click(within(archiveRecord as HTMLElement).getByRole('button', { name: /Вернуть в очередь/i }));

    expect(screen.getByRole('tab', { name: /Очередь разбора|РћС‡РµСЂРµРґСЊ СЂР°Р·Р±РѕСЂР°/i })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByText(/Старый пост про пилоты/i)).toBeInTheDocument();
  });

  it('bulk archives filtered import candidates and can undo the latest bulk action', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('tab', { name: /Очередь разбора|РћС‡РµСЂРµРґСЊ СЂР°Р·Р±РѕСЂР°/i }));
    fireEvent.change(screen.getByLabelText(/Источник|РСЃС‚РѕС‡РЅРёРє/i), { target: { value: 'source-tg-archive' } });
    fireEvent.change(screen.getByLabelText('Evidence policy'), { target: { value: 'archiveOnly' } });
    fireEvent.click(screen.getByRole('button', { name: /Выбрать все по фильтру|Р’С‹Р±СЂР°С‚СЊ РІСЃРµ РїРѕ С„РёР»СЊС‚СЂСѓ/i }));
    fireEvent.click(screen.getByRole('button', { name: /^Добавить все$|^Р”РѕР±Р°РІРёС‚СЊ РІСЃРµ$/i }));

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Подтвердить|РџРѕРґС‚РІРµСЂРґРёС‚СЊ/i }));

    expect(screen.getAllByText(/Bulk archive/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Как система поняла автора/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Архив|РђСЂС…РёРІ/i }));
    expect(screen.getByText(/Почему demo magic не становится adoption/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Отменить последнее групповое действие|РћС‚РјРµРЅРёС‚СЊ РїРѕСЃР»РµРґРЅРµРµ РіСЂСѓРїРїРѕРІРѕРµ РґРµР№СЃС‚РІРёРµ/i }));
    expect(screen.queryByText(/Почему demo magic не становится adoption/i)).not.toBeInTheDocument();
  });

  it('accepts one import candidate into author memory', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('tab', { name: /Очередь разбора|РћС‡РµСЂРµРґСЊ СЂР°Р·Р±РѕСЂР°/i }));
    fireEvent.change(screen.getByLabelText(/Источник|РСЃС‚РѕС‡РЅРёРє/i), { target: { value: 'source-blog-essays' } });
    fireEvent.change(screen.getByLabelText('Evidence policy'), { target: { value: 'canSupportAssertions' } });

    const candidate = screen.getByText(/Evals как интерфейс доверия/i).closest('article');
    expect(candidate).toBeInTheDocument();
    fireEvent.click(within(candidate as HTMLElement).getByRole('button', { name: /^В память$/i }));

    expect(screen.getByRole('tab', { name: /Лента|Р›РµРЅС‚Р°/i })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getAllByText(/Evals как интерфейс доверия/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText('imported').length).toBeGreaterThan(0);
  });

  it('adds an author thought note without a title and persists it after reload', () => {
    const { unmount } = renderAppCabinet();

    fireEvent.change(screen.getByLabelText('Заметка автора'), {
      target: { value: 'AI onboarding должен объяснять, где пользователь может доверять системе, а где нужен fallback.' }
    });
    fireEvent.change(screen.getByLabelText('Теги'), { target: { value: 'onboarding, trust' } });
    fireEvent.click(screen.getByRole('button', { name: /Добавить в память/i }));

    expect(screen.getAllByText(/AI onboarding должен объяснять/i).length).toBeGreaterThan(0);

    unmount();
    renderAppCabinet();

    expect(screen.getAllByText(/AI onboarding должен объяснять/i).length).toBeGreaterThan(0);
  });

  it('reveals and hides the optional title field', () => {
    renderAppCabinet();

    expect(screen.queryByLabelText('Заголовок')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Заголовок/i }));
    expect(screen.getByLabelText('Заголовок')).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Заголовок'), { target: { value: 'Заголовок можно убрать' } });
    fireEvent.click(screen.getByRole('button', { name: /Заголовок/i }));

    expect(screen.queryByLabelText('Заголовок')).not.toBeInTheDocument();
  });

  it('attaches a small file to a thought note and persists it after reload', async () => {
    const { unmount } = renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Файл/i }));
    fireEvent.change(screen.getByLabelText('Файл'), {
      target: { files: [new File(['AI-B2B research memo'], 'research-memo.txt', { type: 'text/plain' })] }
    });

    await waitFor(() => expect(screen.getByText('research-memo.txt')).toBeInTheDocument());

    fireEvent.change(screen.getByLabelText('Заметка автора'), {
      target: { value: 'Прикладываю короткую исследовательскую заметку про adoption review.' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Добавить в память/i }));

    await waitFor(() => expect(screen.getAllByText('research-memo.txt').length).toBeGreaterThan(0));

    unmount();
    renderAppCabinet();

    expect(screen.getByText('research-memo.txt')).toBeInTheDocument();
  });

  it('rejects oversized author-memory attachments', async () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Файл/i }));
    fireEvent.change(screen.getByLabelText('Файл'), {
      target: {
        files: [new File([new Uint8Array(1024 * 1024 + 1)], 'too-large.pdf', { type: 'application/pdf' })]
      }
    });

    await waitFor(() => expect(screen.getByText(/Файл больше 1 MB/i)).toBeInTheDocument());
    expect(screen.queryByText('too-large.pdf')).not.toBeInTheDocument();
  });

  it('removes an attachment before saving a note', async () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Файл/i }));
    fireEvent.change(screen.getByLabelText('Файл'), {
      target: { files: [new File(['draft'], 'remove-me.md', { type: 'text/markdown' })] }
    });

    await waitFor(() => expect(screen.getByText('remove-me.md')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: /Удалить файл/i }));

    expect(screen.queryByText('remove-me.md')).not.toBeInTheDocument();
  });

  it('replaces an attachment while editing a note', async () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Файл/i }));
    fireEvent.change(screen.getByLabelText('Файл'), {
      target: { files: [new File(['old'], 'old-context.txt', { type: 'text/plain' })] }
    });
    await waitFor(() => expect(screen.getByText('old-context.txt')).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText('Заметка автора'), {
      target: { value: 'Заметка с файлом, который надо заменить.' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Добавить в память/i }));

    await waitFor(() => expect(screen.getAllByText('old-context.txt').length).toBeGreaterThan(0));
    fireEvent.click(screen.getAllByRole('button', { name: /Редактировать/i })[0]);
    fireEvent.click(screen.getByRole('button', { name: /Удалить файл/i }));
    fireEvent.change(screen.getByLabelText('Файл заметки'), {
      target: { files: [new File(['new'], 'new-context.txt', { type: 'text/plain' })] }
    });
    await waitFor(() => expect(screen.getByText('new-context.txt')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: /Сохранить/i }));

    expect(screen.queryByText('old-context.txt')).not.toBeInTheDocument();
    expect(screen.getByText('new-context.txt')).toBeInTheDocument();
  });

  it('shows a local link preview in the composer and saved note feed', () => {
    renderAppCabinet();

    fireEvent.change(screen.getByLabelText('Тип записи'), { target: { value: 'linkReaction' } });
    fireEvent.change(screen.getByLabelText('Ссылка'), { target: { value: 'ux-source.test/research-note' } });

    expect(screen.getByText('Ссылка из ux-source.test')).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Заметка автора'), {
      target: { value: 'Ссылка полезна как пример того, как AI pilot должен проходить adoption review.' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Добавить в память/i }));

    expect(screen.getAllByText('Ссылка из ux-source.test').length).toBeGreaterThan(0);
    expect(screen.getByText('https://ux-source.test/research-note')).toBeInTheDocument();
  });

  it('starts a targeted manual correction from an assertion and shows a conflict prompt', () => {
    renderAppCabinet();

    fireEvent.click(screen.getAllByRole('button', { name: /^Корректировать$/i })[0]);

    expect(screen.getByLabelText('Что корректируем')).toBeInTheDocument();
    expect(screen.queryByLabelText('Ссылка')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Теги')).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Корректировка'), {
      target: { value: 'Не согласен: этот вывод нужно заменить, потому что позиция автора жестче.' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Добавить в память/i }));

    expect(screen.getByText(/Корректировка спорит с текущим evidence/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Откатить корректировку/i }));

    expect(screen.queryByText(/Корректировка спорит с текущим evidence/i)).not.toBeInTheDocument();
  });

  it('preselects the exact evidence target when correcting evidence', () => {
    renderAppCabinet();

    fireEvent.click(screen.getAllByText('Evidence')[0]);
    fireEvent.click(screen.getAllByRole('button', { name: /Корректировать evidence/i })[0]);

    const targetSelect = screen.getByLabelText('Что корректируем') as HTMLSelectElement;

    expect(targetSelect.value).toMatch(/^evidence:/);
    expect(targetSelect.selectedOptions[0].textContent).toContain('Evidence ·');
  });

  it('searches, filters, and lazily expands the author memory feed', () => {
    renderAppCabinet();

    expect(screen.getByRole('button', { name: /Показать еще/i })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Поиск по памяти'), { target: { value: 'customer interview' } });
    expect(screen.getByText(/AI-фича должна объяснять границы уверенности/i)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Показать еще/i })).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Поиск по памяти'), { target: { value: '' } });
    fireEvent.change(screen.getByLabelText('Фильтр типа заметки'), { target: { value: 'linkReaction' } });

    expect(screen.getAllByText('Реакция').length).toBeGreaterThan(0);
  });

  it('collapses long notes and allows expanding them', () => {
    renderAppCabinet();
    const longText = Array.from({ length: 12 }, () => 'AI-B2B заметка про workflow, adoption, trust loop и границы уверенности.').join(' ');

    fireEvent.change(screen.getByLabelText('Заметка автора'), { target: { value: longText } });
    fireEvent.click(screen.getByRole('button', { name: /Добавить в память/i }));

    expect(screen.getByRole('button', { name: /Показать полностью/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Показать полностью/i }));
    expect(screen.getByRole('button', { name: /Свернуть/i })).toBeInTheDocument();
  });

  it('edits and deletes author notes with evidence-aware confirmation', () => {
    renderAppCabinet();

    fireEvent.change(screen.getByLabelText('Заметка автора'), {
      target: { value: 'Редактируемая заметка про onboarding и доверие.' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Добавить в память/i }));
    fireEvent.click(screen.getAllByRole('button', { name: /Редактировать/i })[0]);
    fireEvent.change(screen.getByLabelText('Текст'), {
      target: { value: 'Отредактированная заметка про onboarding и доверие.' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Сохранить/i }));

    expect(screen.getAllByText(/Отредактированная заметка/i).length).toBeGreaterThan(0);

    fireEvent.click(screen.getAllByRole('button', { name: /Удалить/i })[0]);
    const editedDeleteDialog = screen.getByRole('dialog', { name: /Подтверждение удаления/i });
    fireEvent.click(within(editedDeleteDialog).getByRole('button', { name: /^Удалить$/i }));
    expect(screen.queryAllByText(/Отредактированная заметка/i)).toHaveLength(0);

    fireEvent.click(screen.getAllByRole('button', { name: /Удалить/i })[0]);
    expect(screen.getByRole('dialog', { name: /Подтверждение удаления/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^Отмена$/i }));
  });

  it('shows memory summary and voice input fallback', () => {
    renderAppCabinet();

    expect(screen.getByText('Сводка памяти')).toBeInTheDocument();
    expect(screen.getByText('Всего')).toBeInTheDocument();
    expect(screen.getByText('Месяц')).toBeInTheDocument();

    const voiceButton = screen.getByRole('button', { name: /Голосом/i });
    expect(voiceButton).toBeDisabled();
    expect(voiceButton).toHaveAttribute('title', 'Голосовой ввод недоступен в этом браузере');
  });
});
