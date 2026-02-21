"use client";

import { useState } from "react";
import { CheckCircle, Clock, RefreshCw, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

type GitOpsEngine = "argocd" | "flux";

interface Deployment {
  name: string;
  namespace: string;
  engine: GitOpsEngine;
  syncStatus: "Synced" | "OutOfSync" | "Unknown";
  healthStatus: "Healthy" | "Degraded" | "Progressing" | "Missing";
  repo: string;
  revision: string;
  lastSynced: string;
}

const mockDeployments: Deployment[] = [
  { name: "payment-service", namespace: "payments", engine: "argocd", syncStatus: "Synced", healthStatus: "Healthy", repo: "org/payment-service", revision: "a1b2c3d", lastSynced: "2 min ago" },
  { name: "user-api", namespace: "users", engine: "argocd", syncStatus: "Synced", healthStatus: "Healthy", repo: "org/user-api", revision: "e4f5g6h", lastSynced: "5 min ago" },
  { name: "order-processor", namespace: "orders", engine: "flux", syncStatus: "Synced", healthStatus: "Healthy", repo: "org/order-processor", revision: "i7j8k9l", lastSynced: "10 min ago" },
  { name: "notification-worker", namespace: "notifications", engine: "flux", syncStatus: "OutOfSync", healthStatus: "Progressing", repo: "org/notification-worker", revision: "m0n1o2p", lastSynced: "15 min ago" },
  { name: "auth-service", namespace: "auth", engine: "argocd", syncStatus: "Synced", healthStatus: "Degraded", repo: "org/auth-service", revision: "q3r4s5t", lastSynced: "1 hr ago" },
  { name: "frontend-app", namespace: "frontend", engine: "argocd", syncStatus: "OutOfSync", healthStatus: "Healthy", repo: "org/frontend-app", revision: "u6v7w8x", lastSynced: "2 hrs ago" },
];

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case "Synced":
    case "Healthy":
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    case "OutOfSync":
    case "Degraded":
      return <XCircle className="h-4 w-4 text-yellow-500" />;
    case "Progressing":
      return <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />;
    default:
      return <Clock className="h-4 w-4 text-muted-foreground" />;
  }
}

export default function DeploymentsPage() {
  const [engineFilter, setEngineFilter] = useState<"all" | GitOpsEngine>("all");

  const filtered = mockDeployments.filter(
    (d) => engineFilter === "all" || d.engine === engineFilter,
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        {(["all", "argocd", "flux"] as const).map((engine) => (
          <button
            key={engine}
            onClick={() => setEngineFilter(engine)}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              engineFilter === engine
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:text-foreground",
            )}
          >
            {engine === "all" ? "All" : engine === "argocd" ? "Argo CD" : "Flux CD"}
          </button>
        ))}
      </div>

      <div className="rounded-lg border border-border bg-card">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border text-left text-xs font-medium text-muted-foreground">
              <th className="px-4 py-3">Application</th>
              <th className="px-4 py-3">Engine</th>
              <th className="px-4 py-3">Sync</th>
              <th className="px-4 py-3">Health</th>
              <th className="px-4 py-3">Revision</th>
              <th className="px-4 py-3">Last Synced</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((dep) => (
              <tr key={dep.name} className="border-b border-border last:border-0">
                <td className="px-4 py-3">
                  <div>
                    <p className="text-sm font-medium">{dep.name}</p>
                    <p className="text-xs text-muted-foreground">{dep.namespace}</p>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={cn(
                    "rounded-full px-2 py-0.5 text-[10px] font-medium",
                    dep.engine === "argocd" ? "bg-orange-100 text-orange-700" : "bg-blue-100 text-blue-700",
                  )}>
                    {dep.engine === "argocd" ? "Argo CD" : "Flux CD"}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <StatusIcon status={dep.syncStatus} />
                    <span className="text-xs">{dep.syncStatus}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    <StatusIcon status={dep.healthStatus} />
                    <span className="text-xs">{dep.healthStatus}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <code className="rounded bg-muted px-1.5 py-0.5 text-xs">{dep.revision}</code>
                </td>
                <td className="px-4 py-3 text-xs text-muted-foreground">{dep.lastSynced}</td>
                <td className="px-4 py-3">
                  <button className="rounded-md bg-muted px-2 py-1 text-xs font-medium hover:bg-accent">
                    Sync
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
