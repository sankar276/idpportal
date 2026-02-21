"use client";

import { CheckCircle, Server, XCircle } from "lucide-react";

interface Cluster {
  id: string;
  name: string;
  provider: string;
  region: string;
  version: string;
  nodes: number;
  status: "active" | "degraded" | "provisioning";
  cpu: number;
  memory: number;
}

const mockClusters: Cluster[] = [
  { id: "c-1", name: "prod-us-east-1", provider: "AWS EKS", region: "us-east-1", version: "1.31", nodes: 6, status: "active", cpu: 67, memory: 72 },
  { id: "c-2", name: "prod-eu-west-1", provider: "AWS EKS", region: "eu-west-1", version: "1.31", nodes: 4, status: "active", cpu: 45, memory: 58 },
  { id: "c-3", name: "staging", provider: "AWS EKS", region: "us-east-1", version: "1.31", nodes: 3, status: "active", cpu: 32, memory: 41 },
  { id: "c-4", name: "dev", provider: "AWS EKS", region: "us-east-1", version: "1.31", nodes: 2, status: "degraded", cpu: 89, memory: 91 },
];

function ProgressBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="h-2 w-full rounded-full bg-muted">
      <div className={`h-2 rounded-full ${color}`} style={{ width: `${value}%` }} />
    </div>
  );
}

export default function ClustersPage() {
  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Managed by Rancher - view cluster health, node pools, and resource utilization
      </p>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {mockClusters.map((cluster) => (
          <div key={cluster.id} className="rounded-lg border border-border bg-card p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Server className="h-5 w-5 text-muted-foreground" />
                <div>
                  <h3 className="text-sm font-semibold">{cluster.name}</h3>
                  <p className="text-xs text-muted-foreground">{cluster.provider} - {cluster.region}</p>
                </div>
              </div>
              {cluster.status === "active" ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-yellow-500" />
              )}
            </div>

            <div className="mt-4 grid grid-cols-3 gap-4 text-center text-xs">
              <div>
                <p className="font-medium">{cluster.nodes}</p>
                <p className="text-muted-foreground">Nodes</p>
              </div>
              <div>
                <p className="font-medium">v{cluster.version}</p>
                <p className="text-muted-foreground">K8s Version</p>
              </div>
              <div>
                <p className="font-medium capitalize">{cluster.status}</p>
                <p className="text-muted-foreground">Status</p>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <div>
                <div className="mb-1 flex justify-between text-xs">
                  <span className="text-muted-foreground">CPU</span>
                  <span>{cluster.cpu}%</span>
                </div>
                <ProgressBar value={cluster.cpu} color={cluster.cpu > 80 ? "bg-red-500" : "bg-primary"} />
              </div>
              <div>
                <div className="mb-1 flex justify-between text-xs">
                  <span className="text-muted-foreground">Memory</span>
                  <span>{cluster.memory}%</span>
                </div>
                <ProgressBar value={cluster.memory} color={cluster.memory > 80 ? "bg-red-500" : "bg-primary"} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
