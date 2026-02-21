const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

interface ChatMessage {
  message: string;
  conversation_id: string;
}

interface StreamEvent {
  type: string;
  content?: string;
  agent?: string;
  tools_used?: string[];
  conversation_id?: string;
}

export async function sendChatMessage(
  message: string,
  conversationId: string,
): Promise<Response> {
  const body: ChatMessage = { message, conversation_id: conversationId };
  return fetch(`${API_BASE}/api/v1/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function fetchAgents() {
  const res = await fetch(`${API_BASE}/api/v1/agents`);
  if (!res.ok) throw new Error("Failed to fetch agents");
  return res.json();
}

export async function fetchTemplates() {
  const res = await fetch(`${API_BASE}/api/v1/self-service/templates`);
  if (!res.ok) throw new Error("Failed to fetch templates");
  return res.json();
}

export async function provisionTemplate(
  templateName: string,
  parameters: Record<string, unknown>,
) {
  const res = await fetch(`${API_BASE}/api/v1/self-service/provision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ template_name: templateName, parameters }),
  });
  if (!res.ok) throw new Error("Failed to provision");
  return res.json();
}

export function parseSSEStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  onEvent: (event: StreamEvent) => void,
  onDone: () => void,
): void {
  const decoder = new TextDecoder();
  let buffer = "";

  function processBuffer() {
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          onEvent(data);
        } catch {
          // skip invalid JSON
        }
      }
    }
  }

  function read() {
    reader.read().then(({ done, value }) => {
      if (done) {
        processBuffer();
        onDone();
        return;
      }
      buffer += decoder.decode(value, { stream: true });
      processBuffer();
      read();
    });
  }

  read();
}
