import asyncio
import json

from langchain_core.tools import tool


async def _kubectl(args: str) -> str:
    proc = await asyncio.create_subprocess_shell(
        f"kubectl {args}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        return f"Error: {stderr.decode()}"
    return stdout.decode()


@tool
async def list_kustomizations(namespace: str = "") -> list[dict]:
    """List Flux Kustomization resources across namespaces."""
    ns_flag = f"-n {namespace}" if namespace else "-A"
    output = await _kubectl(f"get kustomizations.kustomize.toolkit.fluxcd.io {ns_flag} -o json")
    try:
        data = json.loads(output)
        return [
            {
                "name": item["metadata"]["name"],
                "namespace": item["metadata"]["namespace"],
                "ready": next((c["status"] for c in item.get("status", {}).get("conditions", []) if c["type"] == "Ready"), "Unknown"),
                "source": item["spec"].get("sourceRef", {}).get("name", ""),
                "path": item["spec"].get("path", ""),
            }
            for item in data.get("items", [])
        ]
    except json.JSONDecodeError:
        return [{"error": output}]


@tool
async def reconcile_kustomization(name: str, namespace: str = "flux-system") -> dict:
    """Trigger reconciliation of a Flux Kustomization."""
    output = await _kubectl(
        f"annotate kustomizations.kustomize.toolkit.fluxcd.io {name} -n {namespace} "
        f"reconcile.fluxcd.io/requestedAt=$(date +%s) --overwrite"
    )
    return {"status": "reconciliation_triggered", "name": name, "output": output.strip()}


@tool
async def suspend_kustomization(name: str, namespace: str = "flux-system") -> dict:
    """Suspend a Flux Kustomization to pause reconciliation."""
    output = await _kubectl(f"suspend kustomization {name} -n {namespace}")
    return {"status": "suspended", "name": name, "output": output.strip()}


@tool
async def resume_kustomization(name: str, namespace: str = "flux-system") -> dict:
    """Resume a suspended Flux Kustomization."""
    output = await _kubectl(f"resume kustomization {name} -n {namespace}")
    return {"status": "resumed", "name": name, "output": output.strip()}


@tool
async def get_source_status(name: str, namespace: str = "flux-system") -> dict:
    """Get the status of a Flux GitRepository source."""
    output = await _kubectl(f"get gitrepositories.source.toolkit.fluxcd.io {name} -n {namespace} -o json")
    try:
        data = json.loads(output)
        conditions = data.get("status", {}).get("conditions", [])
        return {
            "name": data["metadata"]["name"],
            "url": data["spec"].get("url", ""),
            "branch": data["spec"].get("ref", {}).get("branch", ""),
            "ready": next((c["status"] for c in conditions if c["type"] == "Ready"), "Unknown"),
            "last_revision": data.get("status", {}).get("artifact", {}).get("revision", ""),
        }
    except json.JSONDecodeError:
        return {"error": output}
