import {
  Activity,
  AlertTriangle,
  CheckCircle,
  GitBranch,
  Server,
  Shield,
} from "lucide-react";

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color,
}: {
  title: string;
  value: string;
  subtitle: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="mt-1 text-3xl font-bold">{value}</p>
          <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>
        </div>
        <div className={`rounded-lg p-3 ${color}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Services"
          value="47"
          subtitle="3 deployed today"
          icon={Server}
          color="bg-blue-100 text-blue-600"
        />
        <StatCard
          title="Deployments"
          value="12"
          subtitle="All synced"
          icon={GitBranch}
          color="bg-green-100 text-green-600"
        />
        <StatCard
          title="Active Incidents"
          value="2"
          subtitle="1 acknowledged"
          icon={AlertTriangle}
          color="bg-yellow-100 text-yellow-600"
        />
        <StatCard
          title="Policy Compliance"
          value="94%"
          subtitle="6 violations"
          icon={Shield}
          color="bg-purple-100 text-purple-600"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-border bg-card p-6">
          <h2 className="mb-4 text-lg font-semibold">Recent Activity</h2>
          <div className="space-y-4">
            {[
              { action: "Deployed payment-service v2.3.1", time: "5 min ago", icon: CheckCircle, color: "text-green-500" },
              { action: "Kafka topic orders.events created", time: "23 min ago", icon: Activity, color: "text-blue-500" },
              { action: "PagerDuty incident #4521 acknowledged", time: "1 hr ago", icon: AlertTriangle, color: "text-yellow-500" },
              { action: "Policy violation fixed in auth-service", time: "2 hrs ago", icon: Shield, color: "text-purple-500" },
              { action: "New repo user-api scaffolded", time: "3 hrs ago", icon: GitBranch, color: "text-blue-500" },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <item.icon className={`h-4 w-4 ${item.color}`} />
                <span className="flex-1 text-sm">{item.action}</span>
                <span className="text-xs text-muted-foreground">{item.time}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-border bg-card p-6">
          <h2 className="mb-4 text-lg font-semibold">Platform Health</h2>
          <div className="space-y-3">
            {[
              { name: "ArgoCD", status: "Healthy", healthy: true },
              { name: "Flux CD", status: "Healthy", healthy: true },
              { name: "Backstage", status: "Healthy", healthy: true },
              { name: "Keycloak", status: "Healthy", healthy: true },
              { name: "Vault", status: "Healthy", healthy: true },
              { name: "Kafka (Strimzi)", status: "Healthy", healthy: true },
              { name: "Rancher", status: "Degraded", healthy: false },
              { name: "OPA Gatekeeper", status: "Healthy", healthy: true },
            ].map((svc) => (
              <div key={svc.name} className="flex items-center justify-between rounded-md bg-muted px-4 py-2">
                <span className="text-sm font-medium">{svc.name}</span>
                <span className={`text-xs font-medium ${svc.healthy ? "text-green-600" : "text-yellow-600"}`}>
                  {svc.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
