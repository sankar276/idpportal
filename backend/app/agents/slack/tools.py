import httpx
from langchain_core.tools import tool

from app.config import settings

SLACK_API = "https://slack.com/api"


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.slack_bot_token}", "Content-Type": "application/json"}


@tool
async def send_message(channel: str, text: str) -> dict:
    """Send a message to a Slack channel."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{SLACK_API}/chat.postMessage", headers=_headers(), json={"channel": channel, "text": text})
        data = resp.json()
        return {"ok": data.get("ok"), "channel": data.get("channel"), "ts": data.get("ts")}


@tool
async def create_channel(name: str, is_private: bool = False) -> dict:
    """Create a new Slack channel."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{SLACK_API}/conversations.create", headers=_headers(), json={"name": name, "is_private": is_private})
        data = resp.json()
        if data.get("ok"):
            return {"channel_id": data["channel"]["id"], "name": data["channel"]["name"]}
        return {"error": data.get("error", "Unknown error")}


@tool
async def post_incident_update(channel: str, incident_title: str, status: str, details: str) -> dict:
    """Post a structured incident update to a Slack channel using Block Kit."""
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"Incident: {incident_title}"}},
        {"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*Status:*\n{status}"},
            {"type": "mrkdwn", "text": f"*Updated:*\n<!date^{int(__import__('time').time())}^{{date_short}} {{time}}|now>"},
        ]},
        {"type": "section", "text": {"type": "mrkdwn", "text": details}},
        {"type": "divider"},
    ]
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{SLACK_API}/chat.postMessage", headers=_headers(), json={"channel": channel, "blocks": blocks, "text": f"Incident Update: {incident_title}"})
        return {"ok": resp.json().get("ok"), "channel": channel}


@tool
async def send_notification(channel: str, title: str, message: str, severity: str = "info") -> dict:
    """Send a structured notification to Slack with severity color coding."""
    color_map = {"info": "#2563eb", "warning": "#f59e0b", "error": "#ef4444", "success": "#22c55e"}
    attachments = [{"color": color_map.get(severity, "#2563eb"), "blocks": [
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*{title}*\n{message}"}},
    ]}]
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{SLACK_API}/chat.postMessage", headers=_headers(), json={"channel": channel, "attachments": attachments, "text": title})
        return {"ok": resp.json().get("ok"), "channel": channel}
