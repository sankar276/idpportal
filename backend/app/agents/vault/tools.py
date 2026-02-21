import httpx
from langchain_core.tools import tool

from app.config import settings


def _headers() -> dict:
    return {"X-Vault-Token": settings.vault_token, "Content-Type": "application/json"}


@tool
async def read_secret(path: str) -> dict:
    """Read a secret from Vault KV-v2 engine. Path should not include 'secret/data/' prefix."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.vault_addr}/v1/secret/data/{path}", headers=_headers())
        resp.raise_for_status()
        data = resp.json().get("data", {})
        return {"path": path, "keys": list(data.get("data", {}).keys()), "version": data.get("metadata", {}).get("version")}


@tool
async def write_secret(path: str, data: dict) -> dict:
    """Write a secret to Vault KV-v2 engine."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{settings.vault_addr}/v1/secret/data/{path}", headers=_headers(), json={"data": data})
        resp.raise_for_status()
        meta = resp.json().get("data", {})
        return {"path": path, "version": meta.get("version"), "created_time": meta.get("created_time")}


@tool
async def list_secrets(path: str = "") -> list[str]:
    """List secrets at a path in Vault KV-v2 engine."""
    async with httpx.AsyncClient() as client:
        resp = await client.request("LIST", f"{settings.vault_addr}/v1/secret/metadata/{path}", headers=_headers())
        resp.raise_for_status()
        return resp.json().get("data", {}).get("keys", [])


@tool
async def create_vault_policy(name: str, rules_hcl: str) -> dict:
    """Create or update a Vault policy with HCL rules."""
    async with httpx.AsyncClient() as client:
        resp = await client.put(f"{settings.vault_addr}/v1/sys/policy/{name}", headers=_headers(), json={"policy": rules_hcl})
        resp.raise_for_status()
        return {"policy": name, "status": "created"}


@tool
async def enable_secrets_engine(path: str, engine_type: str = "kv-v2") -> dict:
    """Enable a secrets engine at a given path."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{settings.vault_addr}/v1/sys/mounts/{path}", headers=_headers(), json={"type": engine_type, "options": {"version": "2"} if engine_type == "kv" else {}})
        resp.raise_for_status()
        return {"path": path, "type": engine_type, "status": "enabled"}
