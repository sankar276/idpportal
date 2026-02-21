"use client";

import { usePathname } from "next/navigation";
import { Bell, Search } from "lucide-react";

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/chat": "AI Chat",
  "/catalog": "Service Catalog",
  "/deployments": "Deployments",
  "/incidents": "Incidents",
  "/kafka": "Kafka Topics",
  "/policies": "Policy Compliance",
  "/secrets": "Vault Secrets",
  "/self-service": "Self-Service Hub",
  "/clusters": "Cluster Management",
  "/knowledge": "Knowledge Base",
  "/settings": "Settings",
};

export function Header() {
  const pathname = usePathname();
  const title = pageTitles[pathname] || "IDP Portal";

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-background px-6">
      <h1 className="text-lg font-semibold">{title}</h1>

      <div className="flex items-center gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search..."
            className="h-9 w-64 rounded-md border border-border bg-muted pl-9 pr-3 text-sm outline-none focus:border-primary"
          />
        </div>

        <button className="relative rounded-md p-2 hover:bg-muted">
          <Bell className="h-4 w-4 text-muted-foreground" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-destructive" />
        </button>
      </div>
    </header>
  );
}
