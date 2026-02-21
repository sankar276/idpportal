import httpx
from langchain_core.tools import tool

from app.config import settings


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.argocd_auth_token}"}


def _url(path: str) -> str:
    return f"{settings.argocd_server_url}/api/v1{path}"


@tool
async def list_applications(project: str = "") -> list[dict]:
    """List all ArgoCD applications, optionally filtered by project."""
    params = {}
    if project:
        params["projects"] = [project]
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(_url("/applications"), headers=_headers(), params=params)
        resp.raise_for_status()
        apps = resp.json().get("items", [])
        return [
            {
                "name": app["metadata"]["name"],
                "namespace": app["spec"].get("destination", {}).get("namespace", ""),
                "status": app["status"].get("sync", {}).get("status", "Unknown"),
                "health": app["status"].get("health", {}).get("status", "Unknown"),
                "repo": app["spec"].get("source", {}).get("repoURL", ""),
            }
            for app in apps
        ]


@tool
async def get_application_status(app_name: str) -> dict:
    """Get detailed status of an ArgoCD application."""
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(_url(f"/applications/{app_name}"), headers=_headers())
        resp.raise_for_status()
        app = resp.json()
        return {
            "name": app["metadata"]["name"],
            "sync_status": app["status"].get("sync", {}).get("status"),
            "health_status": app["status"].get("health", {}).get("status"),
            "revision": app["status"].get("sync", {}).get("revision", ""),
            "repo": app["spec"].get("source", {}).get("repoURL", ""),
            "path": app["spec"].get("source", {}).get("path", ""),
            "target_revision": app["spec"].get("source", {}).get("targetRevision", ""),
        }


@tool
async def sync_application(app_name: str, prune: bool = False) -> dict:
    """Trigger a sync for an ArgoCD application."""
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.post(
            _url(f"/applications/{app_name}/sync"),
            headers=_headers(),
            json={"prune": prune},
        )
        resp.raise_for_status()
        return {"status": "sync_triggered", "app": app_name}


@tool
async def rollback_application(app_name: str, revision_id: int) -> dict:
    """Rollback an ArgoCD application to a specific revision."""
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.post(
            _url(f"/applications/{app_name}/rollback"),
            headers=_headers(),
            json={"id": revision_id},
        )
        resp.raise_for_status()
        return {"status": "rollback_triggered", "app": app_name, "revision": revision_id}


@tool
async def get_deployment_history(app_name: str) -> list[dict]:
    """Get deployment history for an ArgoCD application."""
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(_url(f"/applications/{app_name}"), headers=_headers())
        resp.raise_for_status()
        app = resp.json()
        history = app.get("status", {}).get("history", [])
        return [
            {
                "id": h.get("id"),
                "revision": h.get("revision", "")[:12],
                "deployed_at": h.get("deployedAt", ""),
                "source": h.get("source", {}).get("repoURL", ""),
            }
            for h in history
        ]
