export default function ThreadSidebar({
  threads,
  activeThreadId,
  onCreateThread,
  onSelectThread,
  onDeleteThread
}) {
  return (
    <aside className="thread-sidebar">
      <div className="sidebar-header">
        <div>
          <p className="eyebrow">Threads</p>
          <h2>Chats</h2>
        </div>
        <button className="icon-button" type="button" onClick={onCreateThread} title="New chat">
          +
        </button>
      </div>

      <div className="thread-list">
        {threads.map((thread) => (
          <div
            className={`thread-card ${thread.id === activeThreadId ? "active" : ""}`}
            key={thread.id}
          >
            <button type="button" onClick={() => onSelectThread(thread.id)}>
              <span>{thread.title}</span>
              <small>{new Date(thread.updated_at).toLocaleString()}</small>
            </button>
            <button
              className="delete-button"
              type="button"
              onClick={() => onDeleteThread(thread.id)}
              title="Delete thread"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </aside>
  );
}
