import type { Fabula, SourceSignal, Topic, TopicFabulaMatrixEntry } from '../../domain/editorialWorkspace';
import { isTopicFabulaEnabled } from '../../domain/editorialWorkspace';

export function PostCandidateEditContext({
  fabulaId,
  fabulas,
  matrix,
  signal,
  topic,
  onFabulaChange
}: {
  fabulaId: string;
  fabulas: Fabula[];
  matrix: TopicFabulaMatrixEntry[];
  signal?: SourceSignal;
  topic?: Topic;
  onFabulaChange: (fabulaId: string) => void;
}) {
  const visibleFabulas = fabulas.filter((fabula) => fabula.status === 'active');
  const options = visibleFabulas.length > 0 ? visibleFabulas : fabulas;
  const compatible = topic ? isTopicFabulaEnabled(matrix, topic.id, fabulaId) : true;

  return (
    <div className="post-candidate-edit-context">
      <ContextItem label="Сигнал" value={signal?.title ?? 'Сигнал не найден'} />
      <ContextItem label="Тема" value={topic?.title ?? 'Тема не найдена'} />
      <label>
        Фабула
        <select value={fabulaId} onChange={(event) => onFabulaChange(event.target.value)}>
          {options.map((fabula) => (
            <option key={fabula.id} value={fabula.id}>
              {fabula.title}
            </option>
          ))}
        </select>
      </label>
      {!compatible ? (
        <p className="post-candidate-edit-warning">Фабула не включена для текущей темы в матрице совместимости.</p>
      ) : null}
    </div>
  );
}

function ContextItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}
