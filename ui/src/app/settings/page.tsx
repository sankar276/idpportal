"use client";

export default function SettingsPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="rounded-lg border border-border bg-card p-6">
        <h2 className="text-sm font-semibold">Profile</h2>
        <div className="mt-4 space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">Email</label>
            <input type="email" value="admin@example.com" readOnly className="h-9 w-full rounded-md border border-border bg-muted px-3 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">Role</label>
            <input type="text" value="Platform Admin" readOnly className="h-9 w-full rounded-md border border-border bg-muted px-3 text-sm" />
          </div>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-card p-6">
        <h2 className="text-sm font-semibold">AI Agent Preferences</h2>
        <div className="mt-4 space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">Default LLM Provider</label>
            <select className="h-9 w-full rounded-md border border-border bg-muted px-3 text-sm">
              <option value="anthropic">Anthropic (Claude)</option>
              <option value="openai">OpenAI (GPT)</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">Default GitOps Engine</label>
            <select className="h-9 w-full rounded-md border border-border bg-muted px-3 text-sm">
              <option value="argocd">Argo CD</option>
              <option value="flux">Flux CD</option>
            </select>
          </div>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-card p-6">
        <h2 className="text-sm font-semibold">Connected Services</h2>
        <div className="mt-4 space-y-3">
          {[
            { name: "GitHub", status: "Connected" },
            { name: "Jira", status: "Connected" },
            { name: "Slack", status: "Connected" },
            { name: "PagerDuty", status: "Not configured" },
            { name: "ArgoCD", status: "Connected" },
            { name: "Vault", status: "Connected" },
          ].map((svc) => (
            <div key={svc.name} className="flex items-center justify-between rounded-md bg-muted px-4 py-2">
              <span className="text-sm">{svc.name}</span>
              <span className={`text-xs font-medium ${svc.status === "Connected" ? "text-green-600" : "text-muted-foreground"}`}>
                {svc.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
