import { useEffect, useRef, useState } from "react";
import MessageBubble from "./MessageBubble.jsx";

export default function ChatWindow({
  activeThread,
  messages,
  starterQuestions,
  isSending,
  onSend
}) {
  const [draft, setDraft] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  function handleSubmit(event) {
    event.preventDefault();

    const question = draft.trim();
    if (!question || isSending) return;

    setDraft("");
    onSend(question);
  }

  return (
    <section className="chat-window">
      <div className="chat-header">
        <div>
          <p className="eyebrow">Active thread</p>
          <h2>{activeThread?.title || "Deployment chat"}</h2>
        </div>
      </div>

      {messages.length === 0 ? (
        <div className="empty-state">
          <h3>Try a deployment question</h3>
          <p>
            LaunchBot retrieves approved runbook chunks before answering. This lets
            students inspect the answer and the source cards.
          </p>
          <div className="starter-grid">
            {starterQuestions.map((question) => (
              <button
                type="button"
                key={question}
                onClick={() => onSend(question)}
                disabled={isSending}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="message-list">
          {messages.map((message) => (
            <MessageBubble message={message} key={message.id} />
          ))}
          {isSending ? (
            <div className="message assistant">
              <div className="bubble">LaunchBot is retrieving context and generating a response…</div>
            </div>
          ) : null}
          <div ref={bottomRef} />
        </div>
      )}

      <form className="chat-form" onSubmit={handleSubmit}>
        <label htmlFor="question">Ask about deployment</label>
        <div className="input-row">
          <textarea
            id="question"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Example: What should I check if the public URL loads but the chatbot fails?"
            rows={2}
          />
          <button type="submit" disabled={isSending || !draft.trim()}>
            {isSending ? "Sending..." : "Send"}
          </button>
        </div>
      </form>
    </section>
  );
}
