# Kubernetes deployment security and best practices policies
package policy

import rego.v1

violations contains violation if {
	input.kind == "Deployment"
	not input.spec.template.spec.securityContext
	violation := {
		"rule": "require-security-context",
		"message": "Deployment must define a pod-level securityContext",
		"severity": "high",
	}
}

violations contains violation if {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	not container.resources.limits
	violation := {
		"rule": "require-resource-limits",
		"message": sprintf("Container '%s' must define resource limits", [container.name]),
		"severity": "high",
	}
}

violations contains violation if {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	not container.resources.requests
	violation := {
		"rule": "require-resource-requests",
		"message": sprintf("Container '%s' must define resource requests", [container.name]),
		"severity": "medium",
	}
}

violations contains violation if {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	container.securityContext.privileged == true
	violation := {
		"rule": "no-privileged-containers",
		"message": sprintf("Container '%s' must not run in privileged mode", [container.name]),
		"severity": "critical",
	}
}

violations contains violation if {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	container.securityContext.runAsUser == 0
	violation := {
		"rule": "no-root-user",
		"message": sprintf("Container '%s' must not run as root (UID 0)", [container.name]),
		"severity": "critical",
	}
}

violations contains violation if {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	not container.livenessProbe
	violation := {
		"rule": "require-liveness-probe",
		"message": sprintf("Container '%s' should define a livenessProbe", [container.name]),
		"severity": "medium",
	}
}

violations contains violation if {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	not container.readinessProbe
	violation := {
		"rule": "require-readiness-probe",
		"message": sprintf("Container '%s' should define a readinessProbe", [container.name]),
		"severity": "medium",
	}
}

violations contains violation if {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	tag := split(container.image, ":")[1]
	tag == "latest"
	violation := {
		"rule": "no-latest-tag",
		"message": sprintf("Container '%s' must not use 'latest' image tag", [container.name]),
		"severity": "high",
	}
}

violations contains violation if {
	input.kind == "Deployment"
	input.spec.replicas < 2
	violation := {
		"rule": "min-replicas",
		"message": "Production deployments should have at least 2 replicas",
		"severity": "low",
	}
}
