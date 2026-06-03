import { EditorialWorkflow } from './domain/editorialWorkflow';

const workflow = EditorialWorkflow.default();

export function App() {
  const stages = workflow.stages();
  const firstGate = stages.find((stage) => stage.requiresApproval);

  return (
    <main className="app-shell">
      <section className="hero" aria-labelledby="hero-title">
        <p className="eyebrow">Project foundation</p>
        <h1 id="hero-title">Glavred</h1>
        <p className="lead">
          An AI-native editorial service for turning signals into an approved content plan,
          briefs, drafts, release, and learning analytics.
        </p>
      </section>

      <section className="panel" aria-labelledby="workflow-title">
        <div>
          <p className="eyebrow">Baseline workflow</p>
          <h2 id="workflow-title">Editorial loop</h2>
        </div>
        <ol className="workflow-list">
          {stages.map((stage) => (
            <li key={stage.id}>
              <span>{stage.label}</span>
              {stage.requiresApproval ? <strong>Human approval</strong> : null}
            </li>
          ))}
        </ol>
        {firstGate ? (
          <p className="gate-note">
            First approval gate: <strong>{firstGate.label}</strong>
          </p>
        ) : null}
      </section>
    </main>
  );
}
