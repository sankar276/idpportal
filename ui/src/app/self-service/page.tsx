"use client";

import { useState } from "react";
import { ArrowRight, Database, GitBranch, Layers, MessageSquare, Server, HardDrive } from "lucide-react";
import { cn } from "@/lib/utils";

interface Template {
  name: string;
  description: string;
  category: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

const templates: Template[] = [
  { name: "Microservice", description: "Create a new microservice with repo, CI/CD, and GitOps deployment", category: "application", icon: Layers, color: "bg-blue-100 text-blue-600" },
  { name: "API Service", description: "REST API service with OpenAPI spec and golden path patterns", category: "application", icon: Server, color: "bg-green-100 text-green-600" },
  { name: "Worker Service", description: "Background worker (Kafka consumer or SQS processor)", category: "application", icon: MessageSquare, color: "bg-purple-100 text-purple-600" },
  { name: "Kafka Topic", description: "Create a Kafka topic with schema registry integration", category: "infrastructure", icon: Database, color: "bg-orange-100 text-orange-600" },
  { name: "Database", description: "Provision a managed database (RDS Postgres/MySQL/Aurora)", category: "infrastructure", icon: HardDrive, color: "bg-red-100 text-red-600" },
  { name: "S3 Bucket", description: "Create an S3 bucket with encryption and lifecycle policies", category: "infrastructure", icon: GitBranch, color: "bg-yellow-100 text-yellow-600" },
];

export default function SelfServicePage() {
  const [categoryFilter, setCategoryFilter] = useState<"all" | "application" | "infrastructure">("all");
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);

  const filtered = templates.filter(
    (t) => categoryFilter === "all" || t.category === categoryFilter,
  );

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-muted-foreground">
          Provision new services and infrastructure from pre-approved templates.
          All configs are validated against OPA/Rego policies before deployment.
        </p>
      </div>

      <div className="flex items-center gap-2">
        {(["all", "application", "infrastructure"] as const).map((cat) => (
          <button
            key={cat}
            onClick={() => setCategoryFilter(cat)}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm font-medium capitalize transition-colors",
              categoryFilter === cat
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:text-foreground",
            )}
          >
            {cat === "all" ? "All Templates" : cat}
          </button>
        ))}
      </div>

      {!selectedTemplate ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((template) => (
            <button
              key={template.name}
              onClick={() => setSelectedTemplate(template)}
              className="group rounded-lg border border-border bg-card p-6 text-left transition-all hover:border-primary hover:shadow-md"
            >
              <div className={`inline-flex rounded-lg p-3 ${template.color}`}>
                <template.icon className="h-6 w-6" />
              </div>
              <h3 className="mt-4 text-sm font-semibold">{template.name}</h3>
              <p className="mt-1 text-xs text-muted-foreground">{template.description}</p>
              <div className="mt-4 flex items-center gap-1 text-xs font-medium text-primary opacity-0 transition-opacity group-hover:opacity-100">
                Get Started <ArrowRight className="h-3 w-3" />
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="mx-auto max-w-2xl rounded-lg border border-border bg-card p-6">
          <div className="mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`rounded-lg p-2 ${selectedTemplate.color}`}>
                <selectedTemplate.icon className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">{selectedTemplate.name}</h2>
                <p className="text-xs text-muted-foreground">{selectedTemplate.description}</p>
              </div>
            </div>
            <button
              onClick={() => setSelectedTemplate(null)}
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              Back
            </button>
          </div>

          <form className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium">Name</label>
              <input
                type="text"
                placeholder={`my-${selectedTemplate.name.toLowerCase().replace(" ", "-")}`}
                className="h-10 w-full rounded-md border border-border bg-muted px-3 text-sm outline-none focus:border-primary"
              />
            </div>

            {selectedTemplate.category === "application" && (
              <>
                <div>
                  <label className="mb-1 block text-sm font-medium">Language</label>
                  <select className="h-10 w-full rounded-md border border-border bg-muted px-3 text-sm">
                    <option value="python">Python</option>
                    <option value="go">Go</option>
                    <option value="node">Node.js</option>
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium">GitOps Engine</label>
                  <select className="h-10 w-full rounded-md border border-border bg-muted px-3 text-sm">
                    <option value="argocd">Argo CD</option>
                    <option value="flux">Flux CD</option>
                  </select>
                </div>
              </>
            )}

            {selectedTemplate.name === "Kafka Topic" && (
              <>
                <div>
                  <label className="mb-1 block text-sm font-medium">Partitions</label>
                  <input type="number" defaultValue={3} className="h-10 w-full rounded-md border border-border bg-muted px-3 text-sm outline-none focus:border-primary" />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium">Retention (days)</label>
                  <input type="number" defaultValue={7} className="h-10 w-full rounded-md border border-border bg-muted px-3 text-sm outline-none focus:border-primary" />
                </div>
              </>
            )}

            {selectedTemplate.name === "Database" && (
              <div>
                <label className="mb-1 block text-sm font-medium">Engine</label>
                <select className="h-10 w-full rounded-md border border-border bg-muted px-3 text-sm">
                  <option value="postgres">PostgreSQL</option>
                  <option value="mysql">MySQL</option>
                  <option value="aurora-postgres">Aurora PostgreSQL</option>
                </select>
              </div>
            )}

            <div className="rounded-md bg-green-50 p-3">
              <p className="text-xs text-green-700">
                Policy validation will run automatically before provisioning.
                All configs will be checked against your organization&apos;s OPA/Rego policies.
              </p>
            </div>

            <button
              type="button"
              className="w-full rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Validate & Provision
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
