"use client";

import { AlertTriangle, CheckCircle, Clock, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface Incident {
  id: string;
  title: string;
  status: "triggered" | "acknowledged" | "resolved";
  urgency: "high" | "low";
  service: string;
  assignee: string;
  createdAt: string;
}

const mockIncidents: Incident[] = [
  { id: "INC-4523", title: "High latency on payment-service endpoints", status: "triggered", urgency: "high", service: "payment-service", assignee: "On-call: Alice", createdAt: "10 min ago" },
  { id: "INC-4521", title: "Database connection pool exhausted", status: "acknowledged", urgency: "high", service: "user-api", assignee: "Bob", createdAt: "1 hr ago" },
  { id: "INC-4519", title: "Kafka consumer lag exceeding threshold", status: "resolved", urgency: "low", service: "order-processor", assignee: "Charlie", createdAt: "3 hrs ago" },
  { id: "INC-4517", title: "Certificate expiry warning (7 days)", status: "resolved", urgency: "low", service: "auth-service", assignee: "Diana", createdAt: "1 day ago" },
];

function StatusBadge({ status }: { status: Incident["status"] }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium",
        status === "triggered" && "bg-red-100 text-red-700",
        status === "acknowledged" && "bg-yellow-100 text-yellow-700",
        status === "resolved" && "bg-green-100 text-green-700",
      )}
    >
      {status === "triggered" && <AlertTriangle className="h-3 w-3" />}
      {status === "acknowledged" && <Clock className="h-3 w-3" />}
      {status === "resolved" && <CheckCircle className="h-3 w-3" />}
      {status}
    </span>
  );
}

export default function IncidentsPage() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center">
          <p className="text-2xl font-bold text-red-600">{mockIncidents.filter((i) => i.status === "triggered").length}</p>
          <p className="text-xs text-red-600">Triggered</p>
        </div>
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-center">
          <p className="text-2xl font-bold text-yellow-600">{mockIncidents.filter((i) => i.status === "acknowledged").length}</p>
          <p className="text-xs text-yellow-600">Acknowledged</p>
        </div>
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-center">
          <p className="text-2xl font-bold text-green-600">{mockIncidents.filter((i) => i.status === "resolved").length}</p>
          <p className="text-xs text-green-600">Resolved</p>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-card">
        <div className="divide-y divide-border">
          {mockIncidents.map((incident) => (
            <div key={incident.id} className="flex items-center gap-4 px-4 py-4">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <code className="text-xs text-muted-foreground">{incident.id}</code>
                  <StatusBadge status={incident.status} />
                  {incident.urgency === "high" && (
                    <span className="rounded bg-red-100 px-1.5 py-0.5 text-[10px] font-medium text-red-700">HIGH</span>
                  )}
                </div>
                <h3 className="mt-1 text-sm font-medium">{incident.title}</h3>
                <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                  <span>{incident.service}</span>
                  <span className="flex items-center gap-1"><User className="h-3 w-3" />{incident.assignee}</span>
                  <span>{incident.createdAt}</span>
                </div>
              </div>
              {incident.status === "triggered" && (
                <button className="rounded-md bg-yellow-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-yellow-600">
                  Acknowledge
                </button>
              )}
              {incident.status === "acknowledged" && (
                <button className="rounded-md bg-green-500 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-600">
                  Resolve
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
