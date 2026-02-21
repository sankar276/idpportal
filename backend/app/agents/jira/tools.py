import base64

import httpx
from langchain_core.tools import tool

from app.config import settings

JIRA_API = "/rest/api/3"


def _headers() -> dict:
    creds = base64.b64encode(f"{settings.jira_user_email}:{settings.jira_api_token}".encode()).decode()
    return {"Authorization": f"Basic {creds}", "Content-Type": "application/json", "Accept": "application/json"}


def _url(path: str) -> str:
    return f"{settings.jira_base_url}{JIRA_API}{path}"


@tool
async def create_jira_issue(project_key: str, summary: str, description: str, issue_type: str = "Task") -> dict:
    """Create a Jira issue in the specified project."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(_url("/issue"), headers=_headers(), json={
            "fields": {"project": {"key": project_key}, "summary": summary, "description": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]}, "issuetype": {"name": issue_type}},
        })
        resp.raise_for_status()
        data = resp.json()
        return {"key": data["key"], "url": f"{settings.jira_base_url}/browse/{data['key']}"}


@tool
async def search_issues(jql_query: str, max_results: int = 10) -> list[dict]:
    """Search Jira issues using JQL query."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(_url("/search"), headers=_headers(), json={"jql": jql_query, "maxResults": max_results, "fields": ["summary", "status", "assignee", "priority"]})
        resp.raise_for_status()
        return [{"key": i["key"], "summary": i["fields"]["summary"], "status": i["fields"]["status"]["name"], "assignee": (i["fields"].get("assignee") or {}).get("displayName", "Unassigned")} for i in resp.json().get("issues", [])]


@tool
async def update_issue_status(issue_key: str, transition_name: str) -> dict:
    """Transition a Jira issue to a new status."""
    async with httpx.AsyncClient() as client:
        trans_resp = await client.get(_url(f"/issue/{issue_key}/transitions"), headers=_headers())
        trans_resp.raise_for_status()
        transitions = trans_resp.json().get("transitions", [])
        transition = next((t for t in transitions if t["name"].lower() == transition_name.lower()), None)
        if not transition:
            return {"error": f"Transition '{transition_name}' not found", "available": [t["name"] for t in transitions]}
        resp = await client.post(_url(f"/issue/{issue_key}/transitions"), headers=_headers(), json={"transition": {"id": transition["id"]}})
        resp.raise_for_status()
        return {"key": issue_key, "new_status": transition_name}


@tool
async def get_sprint_board(board_id: int) -> dict:
    """Get active sprint information for a Jira board."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{settings.jira_base_url}/rest/agile/1.0/board/{board_id}/sprint", headers=_headers(), params={"state": "active"})
        resp.raise_for_status()
        sprints = resp.json().get("values", [])
        return {"board_id": board_id, "active_sprints": [{"id": s["id"], "name": s["name"], "state": s["state"], "start": s.get("startDate", ""), "end": s.get("endDate", "")} for s in sprints]}


@tool
async def add_comment(issue_key: str, comment_body: str) -> dict:
    """Add a comment to a Jira issue."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(_url(f"/issue/{issue_key}/comment"), headers=_headers(), json={"body": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment_body}]}]}})
        resp.raise_for_status()
        return {"issue": issue_key, "comment_id": resp.json().get("id")}
