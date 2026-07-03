import type { FoundMaterial, RadarRun, SourceHandle } from '../../domain/editorialWorkspace';

export function RadarRunTraceSection({
  latestRun,
  sourceHandles,
  foundMaterials
}: {
  latestRun?: RadarRun;
  sourceHandles: SourceHandle[];
  foundMaterials: FoundMaterial[];
}) {
  return (
    <div className="radar-config-section" data-testid="radar-upstream-trace">
      <h4>Трасса запуска</h4>
      <SourceHandleList sourceHandles={sourceHandles} />
      <LatestRunTrace latestRun={latestRun} />
      <SearchPlanTrace latestRun={latestRun} />
      <SearchResultTrace latestRun={latestRun} />
      <FoundMaterialList foundMaterials={foundMaterials} />
    </div>
  );
}

function SourceHandleList({ sourceHandles }: { sourceHandles: SourceHandle[] }) {
  if (sourceHandles.length === 0) return <p className="muted">Источники не связаны с радаром.</p>;
  return (
    <div className="radar-object-list">
      {sourceHandles.map((handle) => (
        <div className="radar-object" key={handle.id}>
          <span className="sig">{handle.type}</span>
          <p>
            <strong>{handle.title}</strong>
            <br />
            {handle.locator || handle.notes || handle.status}
          </p>
        </div>
      ))}
    </div>
  );
}

function LatestRunTrace({ latestRun }: { latestRun?: RadarRun }) {
  if (!latestRun) return <p className="muted">Радар еще не запускался.</p>;
  const skipped = latestRun.operations.filter((operation) => operation.status === 'skipped').length;
  return (
    <>
      <dl className="meta-list upstream-run-meta">
        <dt>Статус</dt>
        <dd>{latestRun.status}</dd>
        <dt>Найдено</dt>
        <dd>{latestRun.foundMaterialIds.length}</dd>
        <dt>Пропущено</dt>
        <dd>{skipped}</dd>
      </dl>
      <div className="radar-object-list">
        {latestRun.operations.map((operation) => (
          <div className="radar-object" key={operation.id}>
            <span className="sig">{operation.status}</span>
            <p>
              <strong>{operation.label}</strong>
              <br />
              {operation.error ?? operation.skippedReason ?? operation.kind}
            </p>
          </div>
        ))}
      </div>
    </>
  );
}

function SearchPlanTrace({ latestRun }: { latestRun?: RadarRun }) {
  if (!latestRun?.searchPlan) return null;
  return (
    <>
      <h4>Карта поиска</h4>
      <p className="muted">
        {latestRun.searchPlan.strategy} · {latestRun.searchPlan.language}
      </p>
      <div className="radar-object-list">
        {latestRun.searchPlan.queries.map((query) => (
          <div className="radar-object" key={query.id}>
            <span className="sig">{query.intent}</span>
            <p>
              <strong>{query.label}</strong>
              <br />
              {query.query}
              <br />
              <span className="muted">{query.rationale}</span>
            </p>
          </div>
        ))}
      </div>
    </>
  );
}

function SearchResultTrace({ latestRun }: { latestRun?: RadarRun }) {
  if (!latestRun?.rawResults?.length) return null;
  return (
    <>
      <h4>Отбор перед чтением</h4>
      <dl className="meta-list upstream-run-meta">
        <dt>Сырые результаты</dt>
        <dd>{latestRun.rawResults.length}</dd>
        <dt>Выбрано читать</dt>
        <dd>{latestRun.selectedForRead?.length ?? 0}</dd>
        <dt>Отклонено до чтения</dt>
        <dd>{latestRun.rejectedBeforeRead?.length ?? 0}</dd>
      </dl>
      <div className="radar-object-list">
        {(latestRun.selectedForRead ?? []).map((selection) => (
          <div className="radar-object" key={selection.rawResultId}>
            <span className="sig">read</span>
            <p>
              <strong>{selection.reason}</strong>
              <br />
              {selection.url}
              <br />
              <span className="muted">score {selection.score}</span>
            </p>
          </div>
        ))}
        {(latestRun.rejectedBeforeRead ?? []).slice(0, 4).map((rejection) => (
          <div className="radar-object" key={rejection.rawResultId}>
            <span className="sig">skip</span>
            <p>
              <strong>{rejection.reason}</strong>
              <br />
              {rejection.url}
              <br />
              <span className="muted">score {rejection.score}</span>
            </p>
          </div>
        ))}
      </div>
    </>
  );
}

function FoundMaterialList({ foundMaterials }: { foundMaterials: FoundMaterial[] }) {
  if (foundMaterials.length === 0) return null;
  return (
    <>
      <h4>Найденные материалы</h4>
      <div className="radar-object-list">
        {foundMaterials.map((material) => (
          <div className="radar-object" key={material.id}>
            <span className="sig">{material.status}</span>
            <p>
              <strong>{material.title}</strong>
              <br />
              {material.snippet}
            </p>
          </div>
        ))}
      </div>
    </>
  );
}
