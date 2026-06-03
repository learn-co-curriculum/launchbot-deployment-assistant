import { useEffect, useMemo, useState } from "react";
import {
  createThread,
  deleteThread,
  getHealth,
  getRagHealth,
  getThread,
  listThreads,
  sendMessage
} from "./services/api.js";
import ChatWindow from "./components/ChatWindow.jsx";
import DeploymentChecklist from "./components/DeploymentChecklist.jsx";
import SourcePanel from "./components/SourcePanel.jsx";
import StatusBanner from "./components/StatusBanner.jsx";
import ThreadSidebar from "./components/ThreadSidebar.jsx";

const STARTER_QUESTIONS = [
  "Why can my friend not open my localhost app?",
  "What should run on the EC2 instance for this teaching deployment?",
  "How do I verify that Ollama and Chroma are working after deployment?"
];

export default function App() {
  const [health, setHealth] = useState(null);
  const [ragHealth, setRagHealth] = useState(null);
  const [threads, setThreads] = useState([]);
  const [activeThreadId, setActiveThreadId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sources, setSources] = useState([]);
  const [ragDebug, setRagDebug] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const [isBooting, setIsBooting] = useState(true);
  const [error, setError] = useState("");

  const activeThread = useMemo(
    () => threads.find((thread) => thread.id === activeThreadId),
    [threads, activeThreadId]
  );

  useEffect(() => {
    async function bootstrap() {
      setIsBooting(true);
      setError("");

      try {
        const [healthData, ragHealthData, threadData] = await Promise.all([
          getHealth(),
          getRagHealth().catch((err) => ({ status: "degraded", error: err.message })),
          listThreads()
        ]);

        setHealth(healthData);
        setRagHealth(ragHealthData);

        let availableThreads = threadData.threads || [];

        if (availableThreads.length === 0) {
          const created = await createThread();
          availableThreads = [created.thread];
        }

        setThreads(availableThreads);
        setActiveThreadId(availableThreads[0].id);

        const active = await getThread(availableThreads[0].id);
        setMessages(active.messages || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsBooting(false);
      }
    }

    bootstrap();
  }, []);

  async function refreshThreads(selectedThreadId = activeThreadId) {
    const threadData = await listThreads();
    setThreads(threadData.threads || []);

    if (selectedThreadId) {
      const active = await getThread(selectedThreadId);
      setMessages(active.messages || []);
      setActiveThreadId(selectedThreadId);
    }
  }

  async function handleCreateThread() {
    setError("");

    try {
      const created = await createThread();
      await refreshThreads(created.thread.id);
      setSources([]);
      setRagDebug(null);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleSelectThread(threadId) {
    setError("");
    setActiveThreadId(threadId);

    try {
      const data = await getThread(threadId);
      setMessages(data.messages || []);

      const lastAssistant = [...(data.messages || [])]
        .reverse()
        .find((message) => message.role === "assistant");

      setSources(lastAssistant?.metadata?.sources || []);
      setRagDebug(lastAssistant?.metadata?.rag || null);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDeleteThread(threadId) {
    setError("");

    try {
      await deleteThread(threadId);
      const data = await listThreads();
      let nextThreads = data.threads || [];

      if (nextThreads.length === 0) {
        const created = await createThread();
        nextThreads = [created.thread];
      }

      setThreads(nextThreads);
      setActiveThreadId(nextThreads[0].id);

      const active = await getThread(nextThreads[0].id);
      setMessages(active.messages || []);
      setSources([]);
      setRagDebug(null);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleSend(question) {
    if (!activeThreadId || isSending) return;

    setIsSending(true);
    setError("");

    const optimisticUserMessage = {
      id: `pending-${Date.now()}`,
      role: "user",
      content: question,
      created_at: new Date().toISOString(),
      metadata: {}
    };

    setMessages((current) => [...current, optimisticUserMessage]);

    try {
      const data = await sendMessage(activeThreadId, question);
      setMessages(data.messages || []);
      setSources(data.sources || []);
      setRagDebug(data.rag || null);
      await refreshThreads(activeThreadId);
    } catch (err) {
      setError(err.message);
      setMessages((current) =>
        current.filter((message) => message.id !== optimisticUserMessage.id)
      );
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="app-shell">
      <ThreadSidebar
        threads={threads}
        activeThreadId={activeThreadId}
        onCreateThread={handleCreateThread}
        onSelectThread={handleSelectThread}
        onDeleteThread={handleDeleteThread}
      />

      <main className="main-panel">
        <header className="hero">
          <div>
            <p className="eyebrow">Full-stack AI deployment demo</p>
            <h1>LaunchBot Deployment Assistant</h1>
            <p>
              Ask source-backed questions about moving a React, Flask, Chroma, and
              Ollama app from localhost to a public AWS server.
            </p>
          </div>
          <StatusBanner health={health} ragHealth={ragHealth} isBooting={isBooting} />
        </header>

        {error ? <div className="error-banner">{error}</div> : null}

        <section className="workspace">
          <div className="chat-column">
            <ChatWindow
              activeThread={activeThread}
              messages={messages}
              starterQuestions={STARTER_QUESTIONS}
              isSending={isSending}
              onSend={handleSend}
            />
          </div>

          <aside className="context-column">
            <SourcePanel sources={sources} ragDebug={ragDebug} />
            <DeploymentChecklist />
          </aside>
        </section>
      </main>
    </div>
  );
}
