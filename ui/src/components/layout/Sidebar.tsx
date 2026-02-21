"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  MessageSquare,
  BookOpen,
  Rocket,
  AlertTriangle,
  Database,
  Shield,
  Lock,
  Wand2,
  Server,
  Brain,
  Settings,
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "AI Chat", href: "/chat", icon: MessageSquare },
  { name: "Service Catalog", href: "/catalog", icon: BookOpen },
  { name: "Deployments", href: "/deployments", icon: Rocket },
  { name: "Incidents", href: "/incidents", icon: AlertTriangle },
  { name: "Kafka", href: "/kafka", icon: Database },
  { name: "Policies", href: "/policies", icon: Shield },
  { name: "Secrets", href: "/secrets", icon: Lock },
  { name: "Self-Service", href: "/self-service", icon: Wand2 },
  { name: "Clusters", href: "/clusters", icon: Server },
  { name: "Knowledge Base", href: "/knowledge", icon: Brain },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-64 flex-col border-r border-sidebar-border bg-sidebar">
      <div className="flex h-14 items-center border-b border-sidebar-border px-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground text-sm font-bold">
            IDP
          </div>
          <span className="text-lg font-semibold text-sidebar-foreground">Portal</span>
        </Link>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-foreground"
                  : "text-muted-foreground hover:bg-sidebar-accent hover:text-sidebar-foreground",
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-sidebar-border p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-xs font-medium">
            PE
          </div>
          <div className="flex-1 text-sm">
            <p className="font-medium text-sidebar-foreground">Platform Eng</p>
            <p className="text-xs text-muted-foreground">Admin</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
