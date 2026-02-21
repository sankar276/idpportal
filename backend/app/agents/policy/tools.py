import httpx
from langchain_core.tools import tool

from app.config import settings


@tool
async def validate_config(domain: str, config_yaml: str) -> dict:
    """Validate a configuration against OPA/Rego policies. Domains: kafka, kubernetes, terraform, cicd, gitops."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.policy_agent_url}/validate",
            json={"domain": domain, "config": config_yaml},
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "valid": data.get("valid", False),
            "violations": data.get("violations", []),
            "violations_count": len(data.get("violations", [])),
            "domain": domain,
        }


@tool
async def generate_config(domain: str, requirements: str) -> dict:
    """Generate a policy-compliant configuration using AI. Provide natural language requirements."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.policy_agent_url}/generate",
            json={"domain": domain, "requirements": requirements},
        )
        resp.raise_for_status()
        return resp.json()


@tool
async def fix_violations(domain: str, config_yaml: str, violations: list[str]) -> dict:
    """Auto-fix policy violations in a configuration using AI remediation."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.policy_agent_url}/fix",
            json={"domain": domain, "config": config_yaml, "violations": violations},
        )
        resp.raise_for_status()
        return resp.json()


@tool
async def list_policies(domain: str = "") -> list[dict]:
    """List available OPA/Rego policies, optionally filtered by domain."""
    path = f"/policies/{domain}" if domain else "/policies"
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.policy_agent_url}{path}")
        resp.raise_for_status()
        return resp.json().get("policies", [])
