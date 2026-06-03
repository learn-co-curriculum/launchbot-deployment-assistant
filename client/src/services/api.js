async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = data.message || `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return data;
}

export function getHealth() {
  return request("/api/health");
}

export function getRagHealth() {
  return request("/api/rag/health");
}

export function listThreads() {
  return request("/api/threads");
}

export function createThread(title = "New deployment chat") {
  return request("/api/threads", {
    method: "POST",
    body: JSON.stringify({ title })
  });
}

export function getThread(threadId) {
  return request(`/api/threads/${threadId}`);
}

export function deleteThread(threadId) {
  return request(`/api/threads/${threadId}`, {
    method: "DELETE"
  });
}

export function sendMessage(threadId, question) {
  return request(`/api/threads/${threadId}/messages`, {
    method: "POST",
    body: JSON.stringify({ question })
  });
}
