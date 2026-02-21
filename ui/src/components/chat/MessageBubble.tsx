"use client";

import { cn } from "@/lib/utils";
import type { Message } from "@/stores/chat";
import { Bot, User, Wrench } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isAgent = message.role === "agent";

  return (
    <div className={cn("flex gap-3", isUser ? "flex-row-reverse" : "flex-row")}>
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser
            ? "bg-primary text-primary-foreground"
            : isAgent
              ? "bg-purple-100 text-purple-600"
              : "bg-muted text-muted-foreground",
        )}
      >
        {isUser ? (
          <User className="h-4 w-4" />
        ) : isAgent ? (
          <Wrench className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>

      <div
        className={cn(
          "max-w-[75%] rounded-lg px-4 py-2.5",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-foreground",
        )}
      >
        {isAgent && message.agentName && (
          <div className="mb-1 flex items-center gap-1.5">
            <span className="text-xs font-semibold text-purple-600">
              {message.agentName} agent
            </span>
            {message.toolsUsed && message.toolsUsed.length > 0 && (
              <span className="rounded bg-purple-100 px-1.5 py-0.5 text-[10px] text-purple-700">
                {message.toolsUsed.join(", ")}
              </span>
            )}
          </div>
        )}
        <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        <p
          className={cn(
            "mt-1 text-[10px]",
            isUser ? "text-primary-foreground/70" : "text-muted-foreground",
          )}
        >
          {message.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
