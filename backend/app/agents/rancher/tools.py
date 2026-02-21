import httpx
from langchain_core.tools import tool

from app.config import settings


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.rancher_api_token}", "Content-Type": "application/json"}


@tool
async def list_clusters() -> list[dict]:
    """List all Kubernetes clusters managed by Rancher."""
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(f"{settings.rancher_server_url}/v3/clusters", headers=_headers())
        resp.raise_for_status()
        return [{"id": c["id"], "name": c["name"], "state": c["state"], "provider": c.get("driver", ""), "k8s_version": c.get("version", {}).get("gitVersion", ""), "node_count": c.get("nodeCount", 0)} for c in resp.json().get("data", [])]


@tool
async def get_cluster_status(cluster_id: str) -> dict:
    """Get detailed status of a Rancher-managed cluster."""
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(f"{settings.rancher_server_url}/v3/clusters/{cluster_id}", headers=_headers())
        resp.raise_for_status()
        c = resp.json()
        return {"id": c["id"], "name": c["name"], "state": c["state"], "provider": c.get("driver", ""), "k8s_version": c.get("version", {}).get("gitVersion", ""), "node_count": c.get("nodeCount", 0), "cpu": c.get("allocatable", {}).get("cpu", ""), "memory": c.get("allocatable", {}).get("memory", ""), "conditions": [{"type": cd["type"], "status": cd["status"]} for cd in c.get("conditions", [])[:5]]}


@tool
async def scale_nodepool(cluster_id: str, nodepool_id: str, quantity: int) -> dict:
    """Scale a node pool in a Rancher-managed cluster."""
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.put(f"{settings.rancher_server_url}/v3/clusters/{cluster_id}/nodePools/{nodepool_id}", headers=_headers(), json={"quantity": quantity})
        resp.raise_for_status()
        return {"cluster_id": cluster_id, "nodepool_id": nodepool_id, "new_quantity": quantity, "status": "scaling"}


@tool
async def get_cluster_events(cluster_id: str, limit: int = 20) -> list[dict]:
    """Get recent events from a Rancher-managed cluster."""
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(f"{settings.rancher_server_url}/v3/clusters/{cluster_id}/events", headers=_headers(), params={"limit": limit, "sort": "created", "order": "desc"})
        resp.raise_for_status()
        return [{"type": e.get("eventType", ""), "reason": e.get("reason", ""), "message": e.get("message", ""), "source": e.get("source", {}).get("component", ""), "created": e.get("created", "")} for e in resp.json().get("data", [])]
