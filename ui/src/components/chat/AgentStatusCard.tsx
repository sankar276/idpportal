"use client";

import { cn } from "@/lib/utils";
import type { AgentStatus } from "@/stores/chat";
import { CheckCircle, Loader2, XCircle } from "lucide-react";

interface AgentStatusCardProps {
  agent: AgentStatus;
}

export function AgentStatusCard({ agent }: AgentStatusCardProps) {
  return (
    <div className="rounded-lg border border-border bg-card p-3">
      <div className="flex items-center gap-2">
        {agent.status === "working" && (
          <Loader2 className="h-4 w-4 animate-spin text-primary" />
        )}
        {agent.status === "done" && (
          <CheckCircle className="h-4 w-4 text-green-500" />
        )}
        {agent.status === "error" && (
          <XCircle className="h-4 w-4 text-destructive" />
        )}
        {agent.status === "idle" && (
          <div className="h-4 w-4 rounded-full border-2 border-muted-foreground" />
        )}

        <span className="text-sm font-medium capitalize">{agent.name}</span>

        <span
          className={cn(
            "ml-auto rounded-full px-2 py-0.5 text-[10px] font-medium",
            agent.status === "working" && "bg-blue-100 text-blue-700",
            agent.status === "done" && "bg-green-100 text-green-700",
            agent.status === "error" && "bg-red-100 text-red-700",
            agent.status === "idle" && "bg-gray-100 text-gray-600",
          )}
        >
          {agent.status}
        </span>
      </div>

      {agent.lastAction && (
        <p className="mt-1 text-xs text-muted-foreground">{agent.lastAction}</p>
      )}
    </div>
  );
}
