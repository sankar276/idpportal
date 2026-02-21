"use client";

import { Lock } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-sm rounded-lg border border-border bg-card p-8">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <Lock className="h-6 w-6" />
          </div>
          <h1 className="text-xl font-bold">IDP Portal</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Sign in to access the developer portal
          </p>
        </div>

        <button
          onClick={() => {
            // Redirect to Keycloak OIDC
            window.location.href = "/api/auth/signin/keycloak";
          }}
          className="w-full rounded-md bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          Sign in with Keycloak
        </button>

        <p className="mt-4 text-center text-xs text-muted-foreground">
          Authentication managed by Keycloak SSO
        </p>
      </div>
    </div>
  );
}
