"use client";

import { AlertTriangle, CheckCircle, Shield, XCircle } from "lucide-react";

interface PolicyViolation {
  service: string;
  policy: string;
  domain: string;
  severity: "high" | "medium" | "low";
  description: string;
  fixable: boolean;
}

const violations: PolicyViolation[] = [
  { service: "order-processor", policy: "require-resource-limits", domain: "kubernetes", severity: "high", description: "Container resource limits not set", fixable: true },
  { service: "temp-worker", policy: "require-liveness-probe", domain: "kubernetes", severity: "medium", description: "Missing liveness probe configuration", fixable: true },
  { service: "legacy-api", policy: "require-encryption", domain: "terraform", severity: "high", description: "S3 bucket encryption not enabled", fixable: true },
  { service: "events-topic", policy: "min-replication-factor", domain: "kafka", severity: "medium", description: "Kafka topic replication factor below minimum (1 < 3)", fixable: true },
  { service: "ci-pipeline", policy: "require-signed-commits", domain: "cicd", severity: "low", description: "GitHub Actions workflow missing commit signature verification", fixable: false },
  { service: "staging-app", policy: "require-network-policy", domain: "kubernetes", severity: "medium", description: "No NetworkPolicy defined for namespace", fixable: true },
];

export default function PoliciesPage() {
  const totalServices = 47;
  const compliantServices = totalServices - new Set(violations.map((v) => v.service)).size;
  const complianceRate = Math.round((compliantServices / totalServices) * 100);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div className="rounded-lg border border-border bg-card p-5 text-center">
          <Shield className="mx-auto h-8 w-8 text-primary" />
          <p className="mt-2 text-3xl font-bold">{complianceRate}%</p>
          <p className="text-xs text-muted-foreground">Overall Compliance</p>
        </div>
        <div className="rounded-lg border border-border bg-card p-5 text-center">
          <p className="text-3xl font-bold text-red-500">{violations.filter((v) => v.severity === "high").length}</p>
          <p className="text-xs text-muted-foreground">High Severity</p>
        </div>
        <div className="rounded-lg border border-border bg-card p-5 text-center">
          <p className="text-3xl font-bold text-yellow-500">{violations.filter((v) => v.severity === "medium").length}</p>
          <p className="text-xs text-muted-foreground">Medium Severity</p>
        </div>
        <div className="rounded-lg border border-border bg-card p-5 text-center">
          <p className="text-3xl font-bold text-green-500">{violations.filter((v) => v.fixable).length}</p>
          <p className="text-xs text-muted-foreground">Auto-fixable</p>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-card">
        <div className="border-b border-border px-4 py-3">
          <h2 className="text-sm font-semibold">Policy Violations</h2>
        </div>
        <div className="divide-y divide-border">
          {violations.map((v, i) => (
            <div key={i} className="flex items-center gap-4 px-4 py-3">
              {v.severity === "high" ? (
                <XCircle className="h-5 w-5 shrink-0 text-red-500" />
              ) : v.severity === "medium" ? (
                <AlertTriangle className="h-5 w-5 shrink-0 text-yellow-500" />
              ) : (
                <CheckCircle className="h-5 w-5 shrink-0 text-blue-500" />
              )}
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{v.service}</span>
                  <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">{v.domain}</span>
                </div>
                <p className="text-xs text-muted-foreground">{v.description}</p>
                <p className="mt-0.5 text-[10px] text-muted-foreground">Policy: {v.policy}</p>
              </div>
              {v.fixable && (
                <button className="rounded-md bg-primary px-3 py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90">
                  Auto-fix
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
