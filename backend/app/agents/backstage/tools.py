import httpx
from langchain_core.tools import tool

from app.config import settings


@tool
async def list_catalog_entities(kind: str = "Component", filter_query: str = "") -> list[dict]:
    """List entities from the Backstage service catalog."""
    params = {"filter": f"kind={kind}"}
    if filter_query:
        params["filter"] += f",{filter_query}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.backstage_url}/api/catalog/entities", params=params)
        resp.raise_for_status()
        return [{"name": e["metadata"]["name"], "kind": e["kind"], "namespace": e["metadata"].get("namespace", "default"), "description": e["metadata"].get("description", ""), "owner": e.get("spec", {}).get("owner", "")} for e in resp.json()]


@tool
async def get_entity_details(entity_ref: str) -> dict:
    """Get details of a Backstage catalog entity. Format: kind:namespace/name."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.backstage_url}/api/catalog/entities/by-name/{entity_ref.replace(':', '/')}")
        resp.raise_for_status()
        e = resp.json()
        return {"name": e["metadata"]["name"], "kind": e["kind"], "description": e["metadata"].get("description", ""), "annotations": e["metadata"].get("annotations", {}), "spec": e.get("spec", {}), "relations": e.get("relations", [])}


@tool
async def trigger_scaffolder_template(template_name: str, parameters: dict) -> dict:
    """Trigger a Backstage scaffolder template to create a new component."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{settings.backstage_url}/api/scaffolder/v2/tasks", json={"templateRef": f"template:default/{template_name}", "values": parameters})
        resp.raise_for_status()
        data = resp.json()
        return {"task_id": data.get("id"), "status": data.get("status", "created")}


@tool
async def search_catalog(query: str) -> list[dict]:
    """Full-text search across the Backstage catalog."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.backstage_url}/api/search/query", params={"term": query})
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [{"title": r.get("document", {}).get("title", ""), "type": r.get("type", ""), "location": r.get("document", {}).get("location", "")} for r in results[:10]]
