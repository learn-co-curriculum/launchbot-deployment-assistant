export default function StatusBanner({ health, ragHealth, isBooting }) {
  if (isBooting) {
    return <div className="status-card">Checking services…</div>;
  }

  const ragOk = ragHealth?.status === "ok";

  return (
    <div className={`status-card ${ragOk ? "ok" : "warn"}`}>
      <div>
        <strong>App:</strong> {health?.status || "unknown"}
      </div>
      <div>
        <strong>RAG:</strong> {ragHealth?.status || "unknown"}
      </div>
      <div>
        <strong>Ollama:</strong> {ragHealth?.ollama?.available ? "reachable" : "check server"}
      </div>
    </div>
  );
}
