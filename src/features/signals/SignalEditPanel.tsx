import type { SignalsController } from './useSignalsController';

export function SignalEditPanel({ controller }: { controller: SignalsController }) {
  if (!controller.editingSignal) return null;
  return (
    <section className="signal-edit-form" data-testid="signal-edit-form">
      <h4>Редакционная коррекция</h4>
      <p className="muted">Источник, доказательства, механизм, результат и ограничения остаются неизменными.</p>
      <label>
        <span>Заголовок</span>
        <input value={controller.editingSignal.title} onChange={(event) => controller.patchSignalDraft({ title: event.target.value })} />
      </label>
      <label>
        <span>Краткая сводка</span>
        <textarea value={controller.editingSignal.summary} onChange={(event) => controller.patchSignalDraft({ summary: event.target.value })} />
      </label>
      <label>
        <span>Правка автора и причина</span>
        <textarea
          value={controller.editingSignal.authorCorrection ?? ''}
          onChange={(event) => controller.patchSignalDraft({ authorCorrection: event.target.value })}
          placeholder="Что именно исправлено и почему"
        />
      </label>
      <div className="row-actions signal-actions entity-actions-footer">
        <button className="btn btn-pri btn-sm" type="button" onClick={controller.saveSignalDraft}>Сохранить</button>
        <button className="btn btn-sec btn-sm" type="button" onClick={() => controller.setEditingSignal(null)}>Отменить</button>
      </div>
    </section>
  );
}
