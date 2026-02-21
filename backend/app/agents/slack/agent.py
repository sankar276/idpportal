from app.agents.base import AgentCapability, AgentCard, BaseAgent
from app.agents.slack.tools import create_channel, post_incident_update, send_message, send_notification
from app.config import settings
from app.services.llm import get_llm


class Agent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(name="slack", description="Sends messages, creates channels, and posts notifications on Slack", capabilities=[
            AgentCapability(name="messaging", description="Send messages and notifications", tools=["send_message", "send_notification"]),
            AgentCapability(name="incident_communication", description="Post incident updates", tools=["post_incident_update"]),
            AgentCapability(name="channel_management", description="Create Slack channels", tools=["create_channel"]),
        ])

    def get_tools(self):
        return [send_message, create_channel, post_incident_update, send_notification]

    async def invoke(self, task: str, context: dict) -> dict:
        llm = get_llm(settings)
        tools = self.get_tools()
        llm_with_tools = llm.bind_tools(tools)
        from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
        messages = [SystemMessage(content=self.get_system_prompt()), HumanMessage(content=task)]
        response = await llm_with_tools.ainvoke(messages)
        tools_used = []
        if response.tool_calls:
            tool_map = {t.name: t for t in tools}
            for tc in response.tool_calls:
                fn = tool_map.get(tc["name"])
                if fn:
                    result = await fn.ainvoke(tc["args"])
                    tools_used.append(tc["name"])
                    messages.append(response)
                    messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
            final = await llm_with_tools.ainvoke(messages)
            return {"content": final.content, "tools_used": tools_used}
        return {"content": response.content, "tools_used": []}

    def get_system_prompt(self) -> str:
        return "You are a Slack communication agent. You send messages, create channels, post incident updates, and send structured notifications."
