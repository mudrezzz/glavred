import { updateLearningNote, type EditorialLearningNote, type ManualMetricSnapshot, type WorkspaceState } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import { HitlGate } from '../../shared/ui/WorkflowPrimitives';
import { analyticsStatusLabel, releaseStatusLabel, targetLabel } from '../../shared/format/production';

export function AnalyticsView({
  workspace,
  onGoRelease,
  onCreateNote,
  onChangeNote,
  onCapture
}: {
  workspace: WorkspaceState;
  onGoRelease: () => void;
  onCreateNote: () => void;
  onChangeNote: (note: EditorialLearningNote) => void;
  onCapture: () => void;
}) {
  const releasePackage = workspace.releasePackage;
  const note = workspace.editorialLearningNote;

  if (!releasePackage || releasePackage.status !== 'exported') {
    return (
      <div className="page fade-up">
        <section className="card edit-empty">
          <div className="placeholder-icon">
            <Icon name="release" size={28} />
          </div>
          <h2>Сначала завершите ручной выпуск</h2>
          <p>Аналитика открывается после статуса «Экспортировано вручную» в разделе «Выпуск».</p>
          <button className="btn btn-pri" type="button" onClick={onGoRelease}>
            <Icon name="release" size={16} />
            Перейти в выпуск
          </button>
        </section>
      </div>
    );
  }

  if (!note) {
    return (
      <div className="page wide fade-up">
        <section className="card draft-start">
          <span className="rub">Analytics prep</span>
          <h2>Подготовить редакционные выводы</h2>
          <p>
            Метрики вводятся вручную. Этот слой фиксирует не просмотры ради просмотров,
            а выводы для следующего редакционного цикла.
          </p>
          <button className="btn btn-pri" type="button" onClick={onCreateNote}>
            <Icon name="analytics" size={16} />
            Подготовить аналитику
          </button>
        </section>
      </div>
    );
  }

  const currentNote = note;

  function patchNote(patch: Partial<EditorialLearningNote>) {
    onChangeNote(updateLearningNote(currentNote, patch));
  }

  function patchMetric(metric: keyof ManualMetricSnapshot, value: string) {
    patchNote({
      metricSnapshot: {
        ...currentNote.metricSnapshot,
        [metric]: Number(value) || 0
      }
    });
  }

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="Analytics · Learning"
        title={`Статус: ${analyticsStatusLabel(note.status)}`}
        subtitle="Площадочные API не подключены: редакция вручную заносит метрики и фиксирует выводы."
        action="Зафиксировать выводы"
        onAction={onCapture}
      />
      <div className="analytics-grid">
        <section className="analytics-doc">
          <div className="doc-head">
            <div>
              <span className="rub">Ручные метрики</span>
              <h2>Редакционный разбор выпуска</h2>
            </div>
            <span className={`pill ${note.status === 'captured' ? 'ok' : 'pin'}`}>
              <i />
              {analyticsStatusLabel(note.status)}
            </span>
          </div>
          <div className="metric-grid">
            <MetricInput label="Просмотры" value={note.metricSnapshot.views} onChange={(value) => patchMetric('views', value)} />
            <MetricInput label="Реакции" value={note.metricSnapshot.reactions} onChange={(value) => patchMetric('reactions', value)} />
            <MetricInput label="Комментарии" value={note.metricSnapshot.comments} onChange={(value) => patchMetric('comments', value)} />
            <MetricInput label="Сохранения" value={note.metricSnapshot.saves} onChange={(value) => patchMetric('saves', value)} />
            <MetricInput label="Лиды" value={note.metricSnapshot.leads} onChange={(value) => patchMetric('leads', value)} />
          </div>
          <div className="learning-fields">
            <LearningTextArea label="Что сработало" value={note.observedResult} onChange={(observedResult) => patchNote({ observedResult })} />
            <LearningTextArea label="Реакция аудитории" value={note.audienceReaction} onChange={(audienceReaction) => patchNote({ audienceReaction })} />
            <LearningTextArea label="Какие тезисы работают" value={note.workingTheses} onChange={(workingTheses) => patchNote({ workingTheses })} />
            <LearningTextArea label="Какие рубрики усиливают доверие" value={note.trustRubrics} onChange={(trustRubrics) => patchNote({ trustRubrics })} />
            <LearningTextArea label="Какие темы приводят качественную аудиторию" value={note.qualityAudienceTopics} onChange={(qualityAudienceTopics) => patchNote({ qualityAudienceTopics })} />
            <LearningTextArea label="Где автор звучит сильнее" value={note.strongerVoice} onChange={(strongerVoice) => patchNote({ strongerVoice })} />
            <LearningTextArea label="Какие форматы стоит повторить" value={note.repeatFormats} onChange={(repeatFormats) => patchNote({ repeatFormats })} />
            <LearningTextArea label="Что развить в серию" value={note.seriesCandidates} onChange={(seriesCandidates) => patchNote({ seriesCandidates })} />
          </div>
        </section>
        <aside className="edit-side">
          <section className="panel">
            <h4>Контекст выпуска</h4>
            <dl className="meta-list">
              <dt>Release</dt>
              <dd>{note.releasePackageId}</dd>
              <dt>Статус</dt>
              <dd>{releaseStatusLabel(releasePackage.status)}</dd>
              <dt>Площадки</dt>
              <dd>{releasePackage.targets.map(targetLabel).join(' + ')}</dd>
            </dl>
          </section>
          <section className="panel">
            <h4>Learning note</h4>
            <span className={`pill ${note.status === 'captured' ? 'ok' : 'pin'}`}>
              <i />
              {analyticsStatusLabel(note.status)}
            </span>
            <dl className="meta-list analytics-meta">
              <dt>Обновлено</dt>
              <dd>{note.updatedAt}</dd>
              <dt>Зафиксировано</dt>
              <dd>{note.capturedAt ?? 'еще нет'}</dd>
            </dl>
          </section>
        </aside>
      </div>
    </div>
  );
}

function MetricInput({
  label,
  value,
  onChange
}: {
  label: string;
  value: number;
  onChange: (value: string) => void;
}) {
  return (
    <label className="metric-input">
      <span>{label}</span>
      <input type="number" min="0" value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function LearningTextArea({
  label,
  value,
  onChange
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="learning-field">
      <span>{label}</span>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}
