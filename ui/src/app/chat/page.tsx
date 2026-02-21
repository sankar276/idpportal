"use client";

import { ChatWindow } from "@/components/chat/ChatWindow";
import { ChatInput } from "@/components/chat/ChatInput";
import { AgentStatusCard } from "@/components/chat/AgentStatusCard";
import { useChatStore } from "@/stores/chat";
import { Plus } from "lucide-react";

export default function ChatPage() {
  const { messages, sendMessage, isStreaming, activeAgents, newConversation } =
    useChatStore();

  return (
    <div className="flex h-full gap-4">
      <div className="flex flex-1 flex-col rounded-lg border border-border bg-card">
        <div className="flex items-center justify-between border-b border-border px-4 py-2">
          <h2 className="text-sm font-medium">Conversation</h2>
          <button
            onClick={newConversation}
            className="flex items-center gap-1 rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-muted"
          >
            <Plus className="h-3 w-3" />
            New
          </button>
        </div>
        <ChatWindow messages={messages} isStreaming={isStreaming} />
        <ChatInput onSend={sendMessage} disabled={isStreaming} />
      </div>

      {activeAgents.length > 0 && (
        <aside className="w-72 space-y-3">
          <h3 className="text-sm font-medium text-muted-foreground">
            Active Agents
          </h3>
          {activeAgents.map((agent) => (
            <AgentStatusCard key={agent.name} agent={agent} />
          ))}
        </aside>
      )}
    </div>
  );
}
