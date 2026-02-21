"use client";

import { useEffect, useRef } from "react";
import { MessageBubble } from "./MessageBubble";
import type { Message } from "@/stores/chat";

interface ChatWindowProps {
  messages: Message[];
  isStreaming: boolean;
}

export function ChatWindow({ messages, isStreaming }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.length === 0 ? (
        <div className="flex h-full flex-col items-center justify-center text-center">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
            <span className="text-2xl font-bold text-primary">AI</span>
          </div>
          <h2 className="mb-2 text-xl font-semibold">IDP Portal AI Assistant</h2>
          <p className="mb-6 max-w-md text-sm text-muted-foreground">
            Ask me to manage deployments, create services, check incidents,
            validate policies, or any platform engineering task.
          </p>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {[
              "List all ArgoCD applications",
              "Create a new Kafka topic",
              "Check active PagerDuty incidents",
              "Validate my deployment config",
              "Scaffold a new microservice",
              "Show Vault secrets for auth-service",
            ].map((suggestion) => (
              <button
                key={suggestion}
                className="rounded-lg border border-border px-3 py-2 text-left text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          {isStreaming && (
            <div className="flex items-center gap-2 px-4 py-2 text-sm text-muted-foreground">
              <div className="flex gap-1">
                <span className="h-2 w-2 animate-bounce rounded-full bg-primary" style={{ animationDelay: "0ms" }} />
                <span className="h-2 w-2 animate-bounce rounded-full bg-primary" style={{ animationDelay: "150ms" }} />
                <span className="h-2 w-2 animate-bounce rounded-full bg-primary" style={{ animationDelay: "300ms" }} />
              </div>
              <span>Thinking...</span>
            </div>
          )}
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
