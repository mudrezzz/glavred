import { EditorialWorkflow, MVP_MODULES } from './domain/editorialWorkflow';

const workflow = EditorialWorkflow.default();

export function App() {
  const stages = workflow.stages();
  const approvalGates = workflow.approvalGates();

  return (
    <main className="app-shell">
      <section className="hero" aria-labelledby="hero-title">
        <p className="eyebrow">Brief-backed foundation</p>
        <h1 id="hero-title">Glavred</h1>
        <p className="lead">
          Not an AI copywriter. Glavred is an AI-native editorial office for expert
          authors who need a disciplined path from source signals to approved posts.
        </p>
      </section>

      <section className="panel" aria-labelledby="workflow-title">
        <div>
          <p className="eyebrow">Operating loop</p>
          <h2 id="workflow-title">Editorial loop</h2>
        </div>
        <ol className="workflow-list">
          {stages.map((stage) => (
            <li key={stage.id}>
              <span>{stage.label}</span>
              <p>{stage.purpose}</p>
              {stage.requiresApproval ? <strong>Human approval</strong> : null}
            </li>
          ))}
        </ol>
      </section>

      <section className="panel panel-secondary" aria-labelledby="mvp-title">
        <div>
          <p className="eyebrow">MVP perimeter</p>
          <h2 id="mvp-title">First five modules</h2>
        </div>
        <ul className="module-list">
          {MVP_MODULES.map((module) => (
            <li key={module.id}>
              <span>{module.label}</span>
              <p>{module.outcome}</p>
            </li>
          ))}
        </ul>
        <p className="gate-note">
          Approval gates: <strong>{approvalGates.map((stage) => stage.label).join(', ')}</strong>
        </p>
      </section>
    </main>
  );
}
