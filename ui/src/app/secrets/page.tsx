"use client";

import { useState } from "react";
import { ChevronRight, Folder, Key, Lock } from "lucide-react";

interface SecretPath {
  path: string;
  type: "folder" | "secret";
  version?: number;
  updatedAt?: string;
}

const mockPaths: SecretPath[] = [
  { path: "secret/data/services/payment-service", type: "folder" },
  { path: "secret/data/services/user-api", type: "folder" },
  { path: "secret/data/services/auth-service", type: "folder" },
  { path: "secret/data/infrastructure/database", type: "folder" },
  { path: "secret/data/infrastructure/kafka", type: "folder" },
  { path: "secret/data/services/payment-service/db-credentials", type: "secret", version: 3, updatedAt: "2 days ago" },
  { path: "secret/data/services/payment-service/api-keys", type: "secret", version: 1, updatedAt: "1 week ago" },
  { path: "secret/data/services/user-api/jwt-secret", type: "secret", version: 5, updatedAt: "1 day ago" },
];

export default function SecretsPage() {
  const [currentPath, setCurrentPath] = useState("secret/data");

  const items = mockPaths.filter((p) =>
    p.path.startsWith(currentPath) && p.path !== currentPath,
  );

  const breadcrumbs = currentPath.split("/").filter(Boolean);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-1 text-sm">
        <Lock className="h-4 w-4 text-muted-foreground" />
        {breadcrumbs.map((crumb, i) => (
          <div key={i} className="flex items-center gap-1">
            <ChevronRight className="h-3 w-3 text-muted-foreground" />
            <button
              onClick={() => setCurrentPath(breadcrumbs.slice(0, i + 1).join("/"))}
              className="text-muted-foreground hover:text-foreground"
            >
              {crumb}
            </button>
          </div>
        ))}
      </div>

      <div className="rounded-lg border border-border bg-card">
        <div className="divide-y divide-border">
          {items.length === 0 ? (
            <div className="p-8 text-center text-sm text-muted-foreground">
              No secrets at this path. Use the Vault CLI or AI Chat to manage secrets.
            </div>
          ) : (
            items.map((item) => (
              <button
                key={item.path}
                onClick={() => item.type === "folder" && setCurrentPath(item.path)}
                className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-muted/50"
              >
                {item.type === "folder" ? (
                  <Folder className="h-4 w-4 text-yellow-500" />
                ) : (
                  <Key className="h-4 w-4 text-primary" />
                )}
                <div className="flex-1">
                  <p className="text-sm font-medium">{item.path.split("/").pop()}</p>
                  <p className="text-xs text-muted-foreground">{item.path}</p>
                </div>
                {item.type === "secret" && (
                  <div className="text-right text-xs text-muted-foreground">
                    <p>v{item.version}</p>
                    <p>{item.updatedAt}</p>
                  </div>
                )}
                {item.type === "folder" && (
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                )}
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
