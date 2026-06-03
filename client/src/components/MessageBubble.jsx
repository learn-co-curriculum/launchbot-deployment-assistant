export default function MessageBubble({ message }) {
  const isAssistant = message.role === "assistant";

  return (
    <div className={`message ${isAssistant ? "assistant" : "user"}`}>
      <div className="message-meta">
        {isAssistant ? "LaunchBot" : "You"}
      </div>
      <div className="bubble">{message.content}</div>
    </div>
  );
}
