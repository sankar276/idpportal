"use client";

import { useState } from "react";
import { Brain, FileText, Search, Upload } from "lucide-react";

export default function KnowledgePage() {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search runbooks, docs, and platform knowledge..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-10 w-full rounded-md border border-border bg-muted pl-9 pr-3 text-sm outline-none focus:border-primary"
          />
        </div>
        <button className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
          <Upload className="h-4 w-4" />
          Ingest Document
        </button>
      </div>

      {searchQuery ? (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">Results for &quot;{searchQuery}&quot;</p>
          {[
            { title: "EKS Cluster Troubleshooting Guide", source: "runbooks/eks-troubleshooting.md", score: 0.94 },
            { title: "Kafka Consumer Lag Remediation", source: "runbooks/kafka-consumer-lag.md", score: 0.87 },
            { title: "ArgoCD Sync Failure Playbook", source: "runbooks/argocd-sync-failures.md", score: 0.82 },
          ].map((result) => (
            <div key={result.title} className="rounded-lg border border-border bg-card p-4 hover:shadow-sm">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <FileText className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                  <div>
                    <h3 className="text-sm font-medium">{result.title}</h3>
                    <p className="mt-0.5 text-xs text-muted-foreground">{result.source}</p>
                  </div>
                </div>
                <span className="rounded bg-green-100 px-1.5 py-0.5 text-[10px] font-medium text-green-700">
                  {Math.round(result.score * 100)}% match
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-muted/30 py-16">
          <Brain className="h-12 w-12 text-muted-foreground/50" />
          <h2 className="mt-4 text-lg font-medium">Platform Knowledge Base</h2>
          <p className="mt-1 max-w-md text-center text-sm text-muted-foreground">
            Search through runbooks, architecture docs, incident reports, and
            platform documentation. Powered by RAG with pgvector embeddings.
          </p>
        </div>
      )}
    </div>
  );
}
