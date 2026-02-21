import { create } from "zustand";
import { parseSSEStream, sendChatMessage } from "@/lib/api";

export interface Message {
  id: string;
  role: "user" | "assistant" | "agent";
  content: string;
  agentName?: string;
  toolsUsed?: string[];
  timestamp: Date;
}

export interface AgentStatus {
  name: string;
  status: "idle" | "working" | "done" | "error";
  lastAction?: string;
}

interface ChatStore {
  messages: Message[];
  isStreaming: boolean;
  activeAgents: AgentStatus[];
  conversationId: string;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  newConversation: () => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  isStreaming: false,
  activeAgents: [],
  conversationId: crypto.randomUUID(),

  sendMessage: async (content: string) => {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: new Date(),
    };

    set((state) => ({
      messages: [...state.messages, userMsg],
      isStreaming: true,
    }));

    try {
      const response = await sendChatMessage(content, get().conversationId);

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      let assistantContent = "";

      parseSSEStream(
        reader,
        (event) => {
          switch (event.type) {
            case "thinking":
              set((state) => ({
                activeAgents: [
                  ...state.activeAgents,
                  { name: "supervisor", status: "working", lastAction: event.content },
                ],
              }));
              break;

            case "agent_output":
              set((state) => ({
                messages: [
                  ...state.messages,
                  {
                    id: crypto.randomUUID(),
                    role: "agent",
                    content: event.content || "",
                    agentName: event.agent,
                    toolsUsed: event.tools_used,
                    timestamp: new Date(),
                  },
                ],
                activeAgents: state.activeAgents.map((a) =>
                  a.name === event.agent ? { ...a, status: "done" as const } : a,
                ),
              }));
              break;

            case "message":
              assistantContent = event.content || "";
              break;

            case "done":
              if (assistantContent) {
                set((state) => ({
                  messages: [
                    ...state.messages,
                    {
                      id: crypto.randomUUID(),
                      role: "assistant",
                      content: assistantContent,
                      timestamp: new Date(),
                    },
                  ],
                }));
              }
              break;
          }
        },
        () => {
          set({ isStreaming: false, activeAgents: [] });
        },
      );
    } catch (error) {
      set((state) => ({
        isStreaming: false,
        activeAgents: [],
        messages: [
          ...state.messages,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: `Error: ${error instanceof Error ? error.message : "Something went wrong"}`,
            timestamp: new Date(),
          },
        ],
      }));
    }
  },

  clearMessages: () => set({ messages: [] }),

  newConversation: () =>
    set({ messages: [], conversationId: crypto.randomUUID(), activeAgents: [] }),
}));
