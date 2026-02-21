# GitOps (ArgoCD and Flux) policies
package policy

import rego.v1

violations contains violation if {
	input.kind == "Application"
	input.apiVersion == "argoproj.io/v1alpha1"
	input.spec.syncPolicy.automated
	not input.spec.syncPolicy.automated.selfHeal
	violation := {
		"rule": "require-self-heal",
		"message": "ArgoCD Applications with automated sync must enable selfHeal",
		"severity": "medium",
	}
}

violations contains violation if {
	input.kind == "Application"
	input.spec.source.targetRevision == "HEAD"
	violation := {
		"rule": "no-head-revision",
		"message": "ArgoCD Applications must target a specific branch or tag, not HEAD",
		"severity": "high",
	}
}

violations contains violation if {
	input.kind == "Application"
	not input.spec.destination.namespace
	violation := {
		"rule": "require-namespace",
		"message": "ArgoCD Applications must specify a destination namespace",
		"severity": "high",
	}
}

violations contains violation if {
	input.kind == "Kustomization"
	input.apiVersion == "kustomize.toolkit.fluxcd.io/v1"
	not input.spec.interval
	violation := {
		"rule": "require-reconcile-interval",
		"message": "Flux Kustomizations must specify a reconciliation interval",
		"severity": "medium",
	}
}

violations contains violation if {
	input.kind == "Kustomization"
	input.apiVersion == "kustomize.toolkit.fluxcd.io/v1"
	not input.spec.healthChecks
	violation := {
		"rule": "require-health-checks",
		"message": "Flux Kustomizations should define health checks",
		"severity": "low",
	}
}

violations contains violation if {
	input.kind == "HelmRelease"
	input.apiVersion == "helm.toolkit.fluxcd.io/v2"
	not input.spec.chart.spec.version
	violation := {
		"rule": "pin-chart-version",
		"message": "Flux HelmReleases must pin a specific chart version",
		"severity": "high",
	}
}
