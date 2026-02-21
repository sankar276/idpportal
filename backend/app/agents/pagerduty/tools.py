import httpx
from langchain_core.tools import tool

from app.config import settings

PD_API = "https://api.pagerduty.com"


def _headers() -> dict:
    return {"Authorization": f"Token token={settings.pagerduty_api_key}", "Content-Type": "application/json", "Accept": "application/vnd.pagerduty+json;version=2"}


@tool
async def list_incidents(status: str = "triggered,acknowledged", limit: int = 10) -> list[dict]:
    """List PagerDuty incidents filtered by status (triggered, acknowledged, resolved)."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{PD_API}/incidents", headers=_headers(), params={"statuses[]": status.split(","), "limit": limit, "sort_by": "created_at:desc"})
        resp.raise_for_status()
        return [{"id": i["id"], "title": i["title"], "status": i["status"], "urgency": i["urgency"], "service": i["service"]["summary"], "created_at": i["created_at"], "url": i["html_url"]} for i in resp.json().get("incidents", [])]


@tool
async def acknowledge_incident(incident_id: str) -> dict:
    """Acknowledge a PagerDuty incident."""
    async with httpx.AsyncClient() as client:
        resp = await client.put(f"{PD_API}/incidents/{incident_id}", headers={**_headers(), "From": "idpportal@example.com"}, json={"incident": {"type": "incident_reference", "status": "acknowledged"}})
        resp.raise_for_status()
        return {"id": incident_id, "status": "acknowledged"}


@tool
async def resolve_incident(incident_id: str) -> dict:
    """Resolve a PagerDuty incident."""
    async with httpx.AsyncClient() as client:
        resp = await client.put(f"{PD_API}/incidents/{incident_id}", headers={**_headers(), "From": "idpportal@example.com"}, json={"incident": {"type": "incident_reference", "status": "resolved"}})
        resp.raise_for_status()
        return {"id": incident_id, "status": "resolved"}


@tool
async def get_on_call_schedule(schedule_id: str) -> dict:
    """Get the current on-call schedule from PagerDuty."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{PD_API}/schedules/{schedule_id}", headers=_headers(), params={"include[]": "users"})
        resp.raise_for_status()
        schedule = resp.json().get("schedule", {})
        users = schedule.get("users", [])
        return {"schedule": schedule.get("name", ""), "on_call": [{"name": u["summary"], "email": u.get("email", "")} for u in users]}


@tool
async def trigger_incident(service_id: str, title: str, description: str, urgency: str = "high") -> dict:
    """Create a new PagerDuty incident."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{PD_API}/incidents", headers={**_headers(), "From": "idpportal@example.com"}, json={"incident": {"type": "incident", "title": title, "service": {"id": service_id, "type": "service_reference"}, "urgency": urgency, "body": {"type": "incident_body", "details": description}}})
        resp.raise_for_status()
        data = resp.json().get("incident", {})
        return {"id": data.get("id"), "title": title, "status": data.get("status"), "url": data.get("html_url")}
