import type { EditorialWorkItemContext } from './editorialWorkItemContext';

export function EditorialBriefContextPanel({ context }: { context: EditorialWorkItemContext }) {
  return (
    <>
      <div className="post-candidate-facts editorial-brief-context" data-testid="editorial-brief-context">
        <Fact label="Сигнал" value={context.signal.title} />
        <Fact label="Тема" value={context.topicTitle} />
        <Fact label="Фабула" value={context.fabulaTitle} />
        <Fact label="Аудитория" value={context.audience} />
        <Fact label="Ценность" value={context.value} />
        <Fact label="Цель" value={context.goal} />
        <Fact label="Платформа" value={context.platform} />
        <Fact label="Публикация" value={context.publication} />
        <Fact label="Confidence" value={context.confidence === null ? 'Не задано' : `${Math.round(context.confidence * 100)}%`} />
        <Fact label="Доказательство кандидата" value={context.evidence} wide />
      </div>
      {context.risks.length > 0 ? (
        <div className="post-candidate-risks editorial-brief-risks">
          <span className="rub">Risks</span>
          <ul>
            {context.risks.map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </>
  );
}

function Fact({ label, value, wide = false }: { label: string; value: string; wide?: boolean }) {
  return (
    <div className={`candidate-fact${wide ? ' wide' : ''}`}>
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}
