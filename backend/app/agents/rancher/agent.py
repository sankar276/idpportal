from app.agents.base import AgentCapability, AgentCard, BaseAgent
from app.agents.rancher.tools import get_cluster_events, get_cluster_status, list_clusters, scale_nodepool
from app.config import settings
from app.services.llm import get_llm


class Agent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(name="rancher", description="Manages Kubernetes clusters via Rancher (list, status, scaling, events)", capabilities=[
            AgentCapability(name="cluster_management", description="List clusters, check status, scale node pools", tools=["list_clusters", "get_cluster_status", "scale_nodepool"]),
            AgentCapability(name="cluster_monitoring", description="View cluster events", tools=["get_cluster_events"]),
        ])

    def get_tools(self):
        return [list_clusters, get_cluster_status, scale_nodepool, get_cluster_events]

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
        return "You are a Rancher cluster management agent. You manage Kubernetes clusters, monitor their health, scale node pools, and review cluster events."
