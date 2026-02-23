import asyncio
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


async def _kubectl(args: list[str]) -> str:
    """Execute kubectl command safely using argument list (no shell injection)."""
    cmd = ["kubectl"] + args
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"kubectl error: {stderr.decode().strip()}")
    return stdout.decode().strip()


@tool
async def list_pods(namespace: str = "default", label_selector: str = "") -> list[dict]:
    """List pods in a Kubernetes namespace, optionally filtered by label selector."""
    args = ["get", "pods", "-n", namespace, "-o", "json"]
    if label_selector:
        args.extend(["-l", label_selector])
    import json
    result = await _kubectl(args)
    data = json.loads(result)
    return [
        {
            "name": pod["metadata"]["name"],
            "namespace": pod["metadata"]["namespace"],
            "status": pod["status"].get("phase", "Unknown"),
            "ready": all(
                c.get("ready", False)
                for c in pod["status"].get("containerStatuses", [])
            ),
            "restarts": sum(
                c.get("restartCount", 0)
                for c in pod["status"].get("containerStatuses", [])
            ),
            "node": pod["spec"].get("nodeName", ""),
            "age": pod["metadata"].get("creationTimestamp", ""),
        }
        for pod in data.get("items", [])
    ]


@tool
async def get_pod_status(pod_name: str, namespace: str = "default") -> dict:
    """Get detailed status of a specific pod including container statuses."""
    import json
    result = await _kubectl(["get", "pod", pod_name, "-n", namespace, "-o", "json"])
    pod = json.loads(result)
    containers = []
    for cs in pod["status"].get("containerStatuses", []):
        containers.append({
            "name": cs["name"],
            "ready": cs.get("ready", False),
            "restart_count": cs.get("restartCount", 0),
            "state": list(cs.get("state", {}).keys())[0] if cs.get("state") else "unknown",
            "image": cs.get("image", ""),
        })
    return {
        "name": pod["metadata"]["name"],
        "namespace": pod["metadata"]["namespace"],
        "phase": pod["status"].get("phase", "Unknown"),
        "conditions": [
            {"type": c["type"], "status": c["status"]}
            for c in pod["status"].get("conditions", [])
        ],
        "containers": containers,
        "node": pod["spec"].get("nodeName", ""),
        "ip": pod["status"].get("podIP", ""),
    }


@tool
async def list_services(namespace: str = "default") -> list[dict]:
    """List services in a Kubernetes namespace."""
    import json
    result = await _kubectl(["get", "services", "-n", namespace, "-o", "json"])
    data = json.loads(result)
    return [
        {
            "name": svc["metadata"]["name"],
            "namespace": svc["metadata"]["namespace"],
            "type": svc["spec"].get("type", "ClusterIP"),
            "cluster_ip": svc["spec"].get("clusterIP", ""),
            "ports": [
                {"port": p.get("port"), "target_port": str(p.get("targetPort", "")), "protocol": p.get("protocol", "TCP")}
                for p in svc["spec"].get("ports", [])
            ],
            "external_ip": (svc["status"].get("loadBalancer", {}).get("ingress", [{}])[0].get("hostname", "")
                           if svc["spec"].get("type") == "LoadBalancer" else ""),
        }
        for svc in data.get("items", [])
    ]


@tool
async def list_namespaces() -> list[dict]:
    """List all Kubernetes namespaces."""
    import json
    result = await _kubectl(["get", "namespaces", "-o", "json"])
    data = json.loads(result)
    return [
        {
            "name": ns["metadata"]["name"],
            "status": ns["status"].get("phase", "Active"),
            "labels": ns["metadata"].get("labels", {}),
            "age": ns["metadata"].get("creationTimestamp", ""),
        }
        for ns in data.get("items", [])
    ]


@tool
async def get_logs(pod_name: str, namespace: str = "default", container: str = "", tail_lines: int = 100) -> str:
    """Get logs from a pod. Optionally specify container name and number of tail lines."""
    args = ["logs", pod_name, "-n", namespace, f"--tail={tail_lines}"]
    if container:
        args.extend(["-c", container])
    return await _kubectl(args)


@tool
async def scale_deployment(deployment_name: str, replicas: int, namespace: str = "default") -> dict:
    """Scale a Kubernetes deployment to the specified number of replicas."""
    await _kubectl(["scale", "deployment", deployment_name, f"--replicas={replicas}", "-n", namespace])
    return {
        "deployment": deployment_name,
        "namespace": namespace,
        "replicas": replicas,
        "status": "scaling",
    }


@tool
async def get_events(namespace: str = "default", limit: int = 20) -> list[dict]:
    """Get recent events from a Kubernetes namespace."""
    import json
    result = await _kubectl(["get", "events", "-n", namespace, "-o", "json", "--sort-by=.lastTimestamp"])
    data = json.loads(result)
    events = data.get("items", [])[-limit:]
    return [
        {
            "type": e.get("type", ""),
            "reason": e.get("reason", ""),
            "message": e.get("message", ""),
            "object": f"{e.get('involvedObject', {}).get('kind', '')}/{e.get('involvedObject', {}).get('name', '')}",
            "count": e.get("count", 0),
            "last_seen": e.get("lastTimestamp", ""),
        }
        for e in events
    ]
