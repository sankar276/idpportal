# CI/CD pipeline security policies
package policy

import rego.v1

violations contains violation if {
	input.type == "github_actions"
	job := input.jobs[_]
	step := job.steps[_]
	contains(step.run, "curl")
	contains(step.run, "| bash")
	violation := {
		"rule": "no-pipe-to-bash",
		"message": "CI steps must not pipe curl output to bash",
		"severity": "critical",
	}
}

violations contains violation if {
	input.type == "github_actions"
	job := input.jobs[_]
	step := job.steps[_]
	step.uses
	not contains(step.uses, "@")
	violation := {
		"rule": "pin-action-versions",
		"message": sprintf("GitHub Action '%s' must be pinned to a specific version", [step.uses]),
		"severity": "high",
	}
}

violations contains violation if {
	input.type == "github_actions"
	input.on.pull_request
	not input.on.pull_request.branches
	violation := {
		"rule": "restrict-pr-triggers",
		"message": "Pull request triggers should specify target branches",
		"severity": "medium",
	}
}

violations contains violation if {
	input.type == "github_actions"
	job := input.jobs[_]
	step := job.steps[_]
	contains(step.run, "${{ secrets.")
	contains(step.run, "echo")
	violation := {
		"rule": "no-secret-logging",
		"message": "CI steps must not echo secrets to output",
		"severity": "critical",
	}
}

violations contains violation if {
	input.type == "github_actions"
	job := input.jobs[_]
	not job.timeout-minutes
	violation := {
		"rule": "require-timeout",
		"message": "CI jobs must define timeout-minutes to prevent runaway builds",
		"severity": "low",
	}
}
