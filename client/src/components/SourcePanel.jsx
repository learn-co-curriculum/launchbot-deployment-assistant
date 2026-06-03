export default function SourcePanel({ sources, ragDebug }) {
  return (
    <section className="source-panel card">
      <div className="section-heading">
        <p className="eyebrow">RAG evidence</p>
        <h2>Sources</h2>
      </div>

      {sources.length === 0 ? (
        <p className="muted">
          Ask a question to see the approved deployment chunks that supported the answer.
        </p>
      ) : (
        <div className="source-list">
          {sources.map((source) => (
            <article className="source-card" key={source.chunk_id}>
              <div className="source-id">{source.source_id}</div>
              <h3>{source.title}</h3>
              <p>{source.section}</p>
              <small>
                {source.category} · chunk {source.chunk_id} · distance {source.distance}
              </small>
            </article>
          ))}
        </div>
      )}

      {ragDebug ? (
        <details className="debug-details">
          <summary>Developer verification metadata</summary>
          <dl>
            <div>
              <dt>Pipeline</dt>
              <dd>{ragDebug.pipeline}</dd>
            </div>
            <div>
              <dt>Retrieved chunks</dt>
              <dd>{ragDebug.retrieved_chunk_ids?.join(", ") || "None"}</dd>
            </div>
            <div>
              <dt>Models</dt>
              <dd>
                {ragDebug.models?.generation} / {ragDebug.models?.embedding}
              </dd>
            </div>
            <div>
              <dt>Fallback</dt>
              <dd>{String(ragDebug.fallback)}</dd>
            </div>
          </dl>
        </details>
      ) : null}
    </section>
  );
}
