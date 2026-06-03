const CHECKS = [
  "React build is copied into Flask templates and static assets.",
  "Flask API routes are namespaced under /api.",
  "SQLite and Chroma paths point to persistent server storage.",
  "Ollama is running on 127.0.0.1:11434.",
  "Nginx proxies public HTTP traffic to Gunicorn.",
  "The public URL can answer a question with source cards."
];

export default function DeploymentChecklist() {
  return (
    <section className="card checklist">
      <div className="section-heading">
        <p className="eyebrow">Verify</p>
        <h2>Deployment checks</h2>
      </div>
      <ul>
        {CHECKS.map((check) => (
          <li key={check}>{check}</li>
        ))}
      </ul>
    </section>
  );
}
