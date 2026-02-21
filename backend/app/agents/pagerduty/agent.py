from app.agents.base import AgentCapability, AgentCard, BaseAgent
from app.agents.pagerduty.tools import acknowledge_incident, get_on_call_schedule, list_incidents, resolve_incident, trigger_incident
from app.config import settings
from app.services.llm import get_llm


class Agent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(name="pagerduty", description="Manages PagerDuty incidents, on-call schedules, and alerting", capabilities=[
            AgentCapability(name="incident_management", description="List, acknowledge, resolve, and trigger incidents", tools=["list_incidents", "acknowledge_incident", "resolve_incident", "trigger_incident"]),
            AgentCapability(name="on_call", description="View on-call schedules", tools=["get_on_call_schedule"]),
        ])

    def get_tools(self):
        return [list_incidents, acknowledge_incident, resolve_incident, get_on_call_schedule, trigger_incident]

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
        return "You are a PagerDuty incident management agent. You help manage incidents, check on-call schedules, and coordinate incident response."
