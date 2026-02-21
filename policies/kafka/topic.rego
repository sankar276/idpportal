# Kafka topic configuration policies
package policy

import rego.v1

violations contains violation if {
	input.kind == "KafkaTopic"
	input.spec.partitions < 3
	violation := {
		"rule": "min-partitions",
		"message": "Kafka topics must have at least 3 partitions for availability",
		"severity": "high",
	}
}

violations contains violation if {
	input.kind == "KafkaTopic"
	input.spec.replicas < 3
	violation := {
		"rule": "min-replicas",
		"message": "Kafka topics must have at least 3 replicas for durability",
		"severity": "high",
	}
}

violations contains violation if {
	input.kind == "KafkaTopic"
	retention := input.spec.config["retention.ms"]
	to_number(retention) > 604800000
	violation := {
		"rule": "max-retention",
		"message": "Kafka topic retention must not exceed 7 days (604800000ms)",
		"severity": "medium",
	}
}

violations contains violation if {
	input.kind == "KafkaTopic"
	not contains(input.metadata.name, "-")
	violation := {
		"rule": "naming-convention",
		"message": "Kafka topic names must use kebab-case with team prefix (e.g., team-name.event-type)",
		"severity": "low",
	}
}

violations contains violation if {
	input.kind == "KafkaTopic"
	input.spec.partitions > 50
	violation := {
		"rule": "max-partitions",
		"message": "Kafka topics must not exceed 50 partitions without approval",
		"severity": "medium",
	}
}

violations contains violation if {
	input.kind == "KafkaTopic"
	cleanup := input.spec.config["cleanup.policy"]
	cleanup == "delete"
	not input.spec.config["retention.ms"]
	violation := {
		"rule": "require-retention-with-delete",
		"message": "Topics with delete cleanup policy must specify retention.ms",
		"severity": "high",
	}
}
