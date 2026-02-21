import asyncio
import json

from langchain_core.tools import tool


async def _kubectl(args: str) -> str:
    proc = await asyncio.create_subprocess_shell(f"kubectl {args}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        return f"Error: {stderr.decode()}"
    return stdout.decode()


@tool
async def create_topic(name: str, partitions: int = 3, replication_factor: int = 3, retention_ms: int = 604800000, namespace: str = "kafka") -> dict:
    """Create a Kafka topic via Strimzi KafkaTopic CRD."""
    manifest = json.dumps({"apiVersion": "kafka.strimzi.io/v1beta2", "kind": "KafkaTopic", "metadata": {"name": name, "namespace": namespace, "labels": {"strimzi.io/cluster": "idpportal-kafka"}}, "spec": {"partitions": partitions, "replicas": replication_factor, "config": {"retention.ms": str(retention_ms)}}})
    output = await _kubectl(f"apply -f - <<EOF\n{manifest}\nEOF")
    return {"name": name, "partitions": partitions, "replication_factor": replication_factor, "status": "created", "output": output.strip()}


@tool
async def list_topics(namespace: str = "kafka") -> list[dict]:
    """List Kafka topics from Strimzi KafkaTopic CRDs."""
    output = await _kubectl(f"get kafkatopics -n {namespace} -o json")
    try:
        data = json.loads(output)
        return [{"name": t["metadata"]["name"], "partitions": t["spec"].get("partitions", 0), "replicas": t["spec"].get("replicas", 0), "ready": next((c["status"] for c in t.get("status", {}).get("conditions", []) if c["type"] == "Ready"), "Unknown")} for t in data.get("items", [])]
    except json.JSONDecodeError:
        return [{"error": output}]


@tool
async def describe_topic(name: str, namespace: str = "kafka") -> dict:
    """Get detailed information about a Kafka topic."""
    output = await _kubectl(f"get kafkatopic {name} -n {namespace} -o json")
    try:
        data = json.loads(output)
        return {"name": data["metadata"]["name"], "partitions": data["spec"].get("partitions"), "replicas": data["spec"].get("replicas"), "config": data["spec"].get("config", {}), "conditions": data.get("status", {}).get("conditions", [])}
    except json.JSONDecodeError:
        return {"error": output}


@tool
async def update_topic_config(name: str, namespace: str = "kafka", config: dict | None = None) -> dict:
    """Update Kafka topic configuration (e.g., retention, cleanup policy)."""
    if not config:
        return {"error": "No config provided"}
    patch = json.dumps({"spec": {"config": {k: str(v) for k, v in config.items()}}})
    output = await _kubectl(f"patch kafkatopic {name} -n {namespace} --type=merge -p '{patch}'")
    return {"name": name, "updated_config": config, "output": output.strip()}


@tool
async def delete_topic(name: str, namespace: str = "kafka") -> dict:
    """Delete a Kafka topic."""
    output = await _kubectl(f"delete kafkatopic {name} -n {namespace}")
    return {"name": name, "status": "deleted", "output": output.strip()}
