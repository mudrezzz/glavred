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
              {operation.skippedReason ?? operation.kind}
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
  );
}
