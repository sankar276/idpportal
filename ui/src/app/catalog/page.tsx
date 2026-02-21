"use client";

import { useEffect, useState } from "react";
import { ExternalLink, Search } from "lucide-react";

interface CatalogEntity {
  metadata: { name: string; namespace: string; description?: string; tags?: string[] };
  kind: string;
  spec: { type?: string; lifecycle?: string; owner?: string };
}

export default function CatalogPage() {
  const [entities, setEntities] = useState<CatalogEntity[]>([]);
  const [search, setSearch] = useState("");
  const [kindFilter, setKindFilter] = useState("all");

  useEffect(() => {
    // Mock data - replace with Backstage API proxy
    setEntities([
      { metadata: { name: "payment-service", namespace: "default", description: "Handles payment processing", tags: ["python", "kafka"] }, kind: "Component", spec: { type: "service", lifecycle: "production", owner: "payments-team" } },
      { metadata: { name: "user-api", namespace: "default", description: "User management REST API", tags: ["go", "grpc"] }, kind: "Component", spec: { type: "service", lifecycle: "production", owner: "platform-team" } },
      { metadata: { name: "order-events", namespace: "default", description: "Order event streaming topic", tags: ["kafka"] }, kind: "Resource", spec: { type: "kafka-topic", lifecycle: "production", owner: "orders-team" } },
      { metadata: { name: "auth-service", namespace: "default", description: "Authentication and authorization", tags: ["go", "keycloak"] }, kind: "Component", spec: { type: "service", lifecycle: "production", owner: "security-team" } },
      { metadata: { name: "notification-worker", namespace: "default", description: "Processes notification queue", tags: ["python", "sqs"] }, kind: "Component", spec: { type: "service", lifecycle: "production", owner: "platform-team" } },
      { metadata: { name: "frontend-app", namespace: "default", description: "Customer-facing web application", tags: ["react", "nextjs"] }, kind: "Component", spec: { type: "website", lifecycle: "production", owner: "frontend-team" } },
    ]);
  }, []);

  const filtered = entities.filter((e) => {
    const matchesSearch = e.metadata.name.includes(search.toLowerCase()) || e.metadata.description?.toLowerCase().includes(search.toLowerCase());
    const matchesKind = kindFilter === "all" || e.kind.toLowerCase() === kindFilter;
    return matchesSearch && matchesKind;
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search catalog..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-10 w-full rounded-md border border-border bg-muted pl-9 pr-3 text-sm outline-none focus:border-primary"
          />
        </div>
        <select
          value={kindFilter}
          onChange={(e) => setKindFilter(e.target.value)}
          className="h-10 rounded-md border border-border bg-muted px-3 text-sm"
        >
          <option value="all">All Kinds</option>
          <option value="component">Components</option>
          <option value="resource">Resources</option>
          <option value="api">APIs</option>
        </select>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filtered.map((entity) => (
          <div key={entity.metadata.name} className="rounded-lg border border-border bg-card p-5 transition-shadow hover:shadow-md">
            <div className="flex items-start justify-between">
              <div>
                <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-medium text-blue-700">{entity.kind}</span>
                <h3 className="mt-2 text-sm font-semibold">{entity.metadata.name}</h3>
                <p className="mt-1 text-xs text-muted-foreground">{entity.metadata.description}</p>
              </div>
              <button className="text-muted-foreground hover:text-foreground">
                <ExternalLink className="h-4 w-4" />
              </button>
            </div>
            <div className="mt-3 flex flex-wrap gap-1">
              {entity.metadata.tags?.map((tag) => (
                <span key={tag} className="rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">{tag}</span>
              ))}
            </div>
            <div className="mt-3 flex items-center justify-between border-t border-border pt-3 text-xs text-muted-foreground">
              <span>{entity.spec.owner}</span>
              <span className={entity.spec.lifecycle === "production" ? "text-green-600" : "text-yellow-600"}>
                {entity.spec.lifecycle}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
