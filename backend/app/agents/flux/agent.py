from app.agents.base import AgentCapability, AgentCard, BaseAgent
from app.agents.flux.tools import (
    get_source_status,
    list_kustomizations,
    reconcile_kustomization,
    resume_kustomization,
    suspend_kustomization,
)
from app.config import settings
from app.services.llm import get_llm


class Agent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(
            name="flux",
            description="Manages Flux CD GitOps resources including Kustomizations and GitRepository sources",
            capabilities=[
                AgentCapability(name="kustomization_management", description="List, reconcile, suspend, and resume Flux Kustomizations", tools=["list_kustomizations", "reconcile_kustomization", "suspend_kustomization", "resume_kustomization"]),
                AgentCapability(name="source_monitoring", description="Check GitRepository source status", tools=["get_source_status"]),
            ],
        )

    def get_tools(self):
        return [list_kustomizations, reconcile_kustomization, suspend_kustomization, resume_kustomization, get_source_status]

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
        return "You are a Flux CD operations agent. You manage GitOps deployments via Flux Kustomizations and GitRepository sources. You can list, reconcile, suspend, and resume Flux resources."
