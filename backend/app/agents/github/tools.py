import httpx
from langchain_core.tools import tool

from app.config import settings

GITHUB_API = "https://api.github.com"


def _headers() -> dict:
    return {
        "Authorization": f"token {settings.github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


@tool
async def create_repository(name: str, org: str, description: str = "", private: bool = True) -> dict:
    """Create a new GitHub repository in an organization."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GITHUB_API}/orgs/{org}/repos",
            headers=_headers(),
            json={"name": name, "description": description, "private": private, "auto_init": True},
        )
        resp.raise_for_status()
        data = resp.json()
        return {"url": data["html_url"], "clone_url": data["clone_url"], "name": data["full_name"]}


@tool
async def create_pull_request(
    repo: str, title: str, body: str, head: str, base: str = "main"
) -> dict:
    """Create a pull request on a GitHub repository. Repo format: owner/repo."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GITHUB_API}/repos/{repo}/pulls",
            headers=_headers(),
            json={"title": title, "body": body, "head": head, "base": base},
        )
        resp.raise_for_status()
        data = resp.json()
        return {"url": data["html_url"], "number": data["number"], "state": data["state"]}


@tool
async def list_repositories(org: str, limit: int = 30) -> list[dict]:
    """List repositories in a GitHub organization."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/orgs/{org}/repos",
            headers=_headers(),
            params={"per_page": limit, "sort": "updated"},
        )
        resp.raise_for_status()
        return [
            {"name": r["full_name"], "url": r["html_url"], "description": r.get("description", "")}
            for r in resp.json()
        ]


@tool
async def create_issue(repo: str, title: str, body: str, labels: list[str] | None = None) -> dict:
    """Create an issue on a GitHub repository. Repo format: owner/repo."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GITHUB_API}/repos/{repo}/issues",
            headers=_headers(),
            json={"title": title, "body": body, "labels": labels or []},
        )
        resp.raise_for_status()
        data = resp.json()
        return {"url": data["html_url"], "number": data["number"]}


@tool
async def search_code(query: str, org: str = "") -> list[dict]:
    """Search for code across GitHub repositories."""
    q = f"{query} org:{org}" if org else query
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/search/code",
            headers=_headers(),
            params={"q": q, "per_page": 10},
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            {"path": item["path"], "repo": item["repository"]["full_name"], "url": item["html_url"]}
            for item in data.get("items", [])
        ]


@tool
async def get_workflow_runs(repo: str, limit: int = 5) -> list[dict]:
    """Get recent GitHub Actions workflow runs for a repository."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{repo}/actions/runs",
            headers=_headers(),
            params={"per_page": limit},
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "id": run["id"],
                "name": run["name"],
                "status": run["status"],
                "conclusion": run.get("conclusion"),
                "url": run["html_url"],
                "branch": run["head_branch"],
            }
            for run in data.get("workflow_runs", [])
        ]
